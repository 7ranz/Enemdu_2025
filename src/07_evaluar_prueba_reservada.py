# ETAPA 8: evaluación única de los modelos congelados en la prueba reservada.
# ARCHIVO: 07_evaluar_prueba_reservada.py; puntúa la prueba una vez y no reajusta decisiones.
# BLOQUE 1: dependencias, rutas y bloqueo contra una segunda evaluación.
import hashlib  # Calcula huellas de integridad.
import json  # Lee contratos congelados y escribe resultados.
from pathlib import Path  # Maneja rutas portables.
import joblib  # Carga los modelos ya congelados.
import matplotlib  # Configura gráficos automáticos.
matplotlib.use('Agg')  # Evita depender de una ventana gráfica.
import matplotlib.pyplot as plt  # Genera figuras científicas.
import numpy as np  # Ejecuta remuestreo y cálculos numéricos.
import pandas as pd  # Lee y exporta tablas.
from scipy import optimize  # Estima intercepto y pendiente de calibración.
from scipy.special import expit  # Evalúa la función logística de forma estable.
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, precision_recall_curve, roc_auc_score, roc_curve  # Calcula evaluación predictiva.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto.
CONFIG = json.loads((RAIZ / 'config/evaluacion_prueba_v1.json').read_text(encoding='utf-8'))  # Lee el protocolo de evaluación.
CONGELADO = json.loads((RAIZ / 'models/metadatos_modelos_congelados.json').read_text(encoding='utf-8'))  # Lee modelos, predictores y umbrales congelados.
PREPARACION = json.loads((RAIZ / 'config/preparacion_v1.json').read_text(encoding='utf-8'))  # Lee las variables autorizadas.
ENTRENAMIENTO = RAIZ / 'data/processed/modelado/entrenamiento.csv'  # Localiza desarrollo solo para la prevalencia base.
PRUEBA = RAIZ / 'data/processed/modelado/prueba_reservada.csv'  # Localiza la prueba que se abrirá en esta etapa.
SALIDAS = RAIZ / 'reports/eda08_evaluacion'  # Define tablas y controles finales.
FIGURAS = RAIZ / 'reports/figures/eda08_evaluacion'  # Define las figuras finales.
PREDICCIONES = RAIZ / 'data/processed/modelado/evaluacion'  # Define el archivo protegido de puntuaciones.
SALIDAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de reportes.
FIGURAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de figuras.
PREDICCIONES.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de predicciones.
MARCADOR = SALIDAS / '00_estado_evaluacion.json'  # Define el bloqueo persistente.
if MARCADOR.exists():  # Detecta una evaluación anterior.
    raise RuntimeError('La evaluación única ya fue iniciada. No se vuelve a puntuar la prueba reservada.')  # Impide observar la prueba por segunda vez.
MARCADOR.write_text(json.dumps({'estado': 'iniciada', 'fecha': CONFIG['fecha_evaluacion'], 'regla': CONFIG['regla']}, ensure_ascii=False, indent=2), encoding='utf-8')  # Registra el inicio antes de leer la prueba.
NUMERICAS = PREPARACION['predictores_numericos']  # Recupera predictores numéricos congelados.
CATEGORICAS = PREPARACION['predictores_categoricos']  # Recupera predictores categóricos congelados.
PREDICTORES = NUMERICAS + CATEGORICAS  # Forma la lista blanca completa.
UMBRALES = {clave: float(valor) for clave, valor in CONGELADO['umbrales_oof'].items()}  # Recupera umbrales sin modificarlos.
AZUL = '#0072B2'  # Define azul accesible.
NARANJA = '#E69F00'  # Define naranja accesible.
VERDE = '#009E73'  # Define verde accesible.
GRIS = '#6B7280'  # Define gris de referencia.
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 12, 'axes.labelsize': 9})  # Fija el estilo científico.

# BLOQUE 2: funciones de integridad, métricas y calibración.
def sha256(ruta):  # Calcula una huella SHA-256.
    objeto = hashlib.sha256()  # Inicializa el algoritmo.
    with ruta.open('rb') as archivo:  # Abre el archivo en modo binario.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee por bloques.
            objeto.update(bloque)  # Incorpora el contenido.
    return objeto.hexdigest()  # Devuelve la huella.

def normalizar_codigo(serie):  # Homogeneiza códigos categóricos.
    return serie.astype('string').str.strip().str.replace(r'\.0$', '', regex=True)  # Convierte a texto entero.

def media_ponderada(valores, pesos):  # Calcula una media ponderada.
    return float(np.average(np.asarray(valores, dtype=float), weights=np.asarray(pesos, dtype=float)))  # Devuelve un escalar.

def metricas_probabilidad(y, p, w):  # Calcula métricas independientes de umbral.
    p = np.clip(np.asarray(p, dtype=float), 1e-7, 1 - 1e-7)  # Evita extremos numéricos.
    return {'roc_auc': roc_auc_score(y, p, sample_weight=w), 'pr_auc': average_precision_score(y, p, sample_weight=w), 'brier': brier_score_loss(y, p, sample_weight=w), 'log_loss': log_loss(y, p, sample_weight=w, labels=[0, 1])}  # Devuelve discriminación y exactitud probabilística.

def metricas_umbral(y, p, w, umbral):  # Calcula métricas con el umbral congelado.
    y = np.asarray(y, dtype=int)  # Normaliza el objetivo.
    d = np.asarray(p, dtype=float) >= float(umbral)  # Aplica el umbral sin optimizarlo.
    w = np.asarray(w, dtype=float)  # Normaliza los pesos.
    tp = w[(y == 1) & d].sum()  # Suma verdaderos positivos.
    fn = w[(y == 1) & ~d].sum()  # Suma falsos negativos.
    tn = w[(y == 0) & ~d].sum()  # Suma verdaderos negativos.
    fp = w[(y == 0) & d].sum()  # Suma falsos positivos.
    sensibilidad = tp / (tp + fn)  # Calcula sensibilidad.
    especificidad = tn / (tn + fp)  # Calcula especificidad.
    precision = tp / (tp + fp) if tp + fp > 0 else np.nan  # Calcula precisión positiva.
    exactitud = (tp + tn) / (tp + tn + fp + fn)  # Calcula exactitud.
    return {'sensibilidad': sensibilidad, 'especificidad': especificidad, 'precision': precision, 'exactitud': exactitud, 'exactitud_balanceada': (sensibilidad + especificidad) / 2, 'tasa_predicha_positiva': (tp + fp) / (tp + tn + fp + fn)}  # Devuelve todas las métricas de decisión.

def todas_metricas(y, p, w, umbral):  # Une métricas probabilísticas y de decisión.
    resultado = metricas_probabilidad(y, p, w)  # Calcula métricas probabilísticas.
    resultado.update(metricas_umbral(y, p, w, umbral))  # Añade métricas con umbral.
    return resultado  # Devuelve un diccionario uniforme.

def calibracion_logistica(y, p, w):  # Estima calibración en la prueba sin alterar probabilidades.
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)  # Evita logits infinitos.
    z = np.log(p / (1 - p))  # Calcula el logit pronosticado.
    def objetivo(parametros):  # Define la pérdida ponderada.
        q = expit(parametros[0] + parametros[1] * z)  # Calcula valores recalibrados solo para estimación.
        return -np.sum(w * (y * np.log(q + 1e-12) + (1 - y) * np.log(1 - q + 1e-12))) / np.sum(w)  # Devuelve entropía cruzada.
    ajuste = optimize.minimize(objetivo, np.array([0.0, 1.0]), method='BFGS')  # Estima intercepto y pendiente.
    return float(ajuste.x[0]), float(ajuste.x[1]), bool(ajuste.success)  # Devuelve parámetros diagnósticos.

def curva_calibracion(y, p, w, grupos=10):  # Construye deciles de masa ponderada.
    tabla = pd.DataFrame({'y': y, 'p': p, 'w': w}).sort_values('p').reset_index(drop=True)  # Ordena probabilidades.
    tabla['masa'] = tabla['w'].cumsum() / tabla['w'].sum()  # Calcula masa acumulada.
    tabla['grupo'] = np.minimum((tabla['masa'] * grupos).astype(int), grupos - 1) + 1  # Asigna deciles ponderados.
    return tabla.groupby('grupo', observed=True).apply(lambda bloque: pd.Series({'n': len(bloque), 'peso': bloque['w'].sum(), 'prediccion_media': media_ponderada(bloque['p'], bloque['w']), 'proporcion_observada': media_ponderada(bloque['y'], bloque['w'])}), include_groups=False).reset_index()  # Resume cada decil.

def intervalo_percentil(valores, alfa=0.05):  # Calcula un intervalo bootstrap percentil.
    arreglo = np.asarray(valores, dtype=float)  # Convierte réplicas a arreglo.
    arreglo = arreglo[np.isfinite(arreglo)]  # Omite réplicas degeneradas.
    return float(np.quantile(arreglo, alfa / 2)), float(np.quantile(arreglo, 1 - alfa / 2)), len(arreglo)  # Devuelve límites y réplicas válidas.

# BLOQUE 3: apertura única, controles de separación y puntuación congelada.
tipos = {columna: 'string' for columna in ['id_persona', 'id_vivienda_sin_mes', 'id_hogar_sin_mes', 'clave_posicion_sin_mes', 'upm', 'estrato', 'particion_ml'] + CATEGORICAS}  # Conserva identificadores y códigos exactos.
prueba = pd.read_csv(PRUEBA, dtype=tipos, encoding='utf-8-sig')  # Abre por primera y única vez la muestra reservada.
for columna in CATEGORICAS:  # Recorre predictores categóricos.
    prueba[columna] = normalizar_codigo(prueba[columna])  # Homogeneiza el código.
prueba['mes'] = prueba['mes'].str.zfill(2)  # Conserva mes con dos dígitos.
for columna in NUMERICAS + ['fexp', 'y_adecuado']:  # Recorre variables numéricas necesarias.
    prueba[columna] = pd.to_numeric(prueba[columna], errors='raise')  # Exige números válidos.
prueba['y_adecuado'] = prueba['y_adecuado'].astype(int)  # Convierte el objetivo a entero.
assert set(prueba['particion_ml']) == {'prueba'}  # Exige la partición reservada.
assert prueba[PREDICTORES].notna().all().all()  # Exige covariables completas.
assert set(prueba['y_adecuado']) == {0, 1}  # Exige ambas clases.
tipos_entrenamiento = {'upm': 'string', 'id_hogar_sin_mes': 'string'}  # Define claves mínimas de desarrollo.
entrenamiento_control = pd.read_csv(ENTRENAMIENTO, usecols=['upm', 'id_hogar_sin_mes', 'fexp', 'y_adecuado'], dtype=tipos_entrenamiento, encoding='utf-8-sig')  # Lee desarrollo sin covariables de selección.
assert set(prueba['upm']).isdisjoint(set(entrenamiento_control['upm']))  # Exige cero UPM compartidas.
assert set(prueba['id_hogar_sin_mes']).isdisjoint(set(entrenamiento_control['id_hogar_sin_mes']))  # Exige cero hogares compartidos.
prevalencia_entrenamiento = media_ponderada(entrenamiento_control['y_adecuado'], entrenamiento_control['fexp'])  # Calcula la referencia sin mirar el resultado de prueba.
x_prueba = prueba[PREDICTORES].copy()  # Extrae solo la lista blanca.
modelo_logistico = joblib.load(RAIZ / 'models/logistica_predictiva_congelada.joblib')  # Carga la logística congelada.
modelo_boosting = joblib.load(RAIZ / 'models/boosting_congelado.joblib')  # Carga boosting congelado.
prueba['p_base'] = prevalencia_entrenamiento  # Asigna la prevalencia de desarrollo.
prueba['p_logistica'] = modelo_logistico.predict_proba(x_prueba)[:, 1]  # Puntúa la logística una vez.
prueba['p_boosting'] = modelo_boosting.predict_proba(x_prueba)[:, 1]  # Puntúa boosting una vez.
columnas_predicciones = ['id_persona', 'upm', 'estrato', 'fexp', 'y_adecuado', 'p02', 'area', 'p_base', 'p_logistica', 'p_boosting']  # Limita el archivo de evaluación.
prueba[columnas_predicciones].to_csv(PREDICCIONES / 'predicciones_prueba_unica.csv.gz', index=False, encoding='utf-8-sig', compression='gzip')  # Guarda puntuaciones para análisis sin volver a abrir la prueba.
y = prueba['y_adecuado'].to_numpy(dtype=int)  # Extrae el objetivo final.
w = prueba['fexp'].to_numpy(dtype=float)  # Extrae pesos finales.

# BLOQUE 4: estimaciones puntuales globales y calibración.
filas_globales = []  # Reserva métricas por modelo.
curvas = []  # Reserva deciles de calibración.
for nombre in CONFIG['modelos']:  # Recorre los tres comparadores.
    p = prueba[f'p_{nombre}'].to_numpy(dtype=float)  # Recupera probabilidades congeladas.
    fila = {'modelo': nombre, 'n': len(prueba), 'upm': prueba['upm'].nunique(), 'umbral_congelado': UMBRALES[nombre]}  # Registra soporte y umbral.
    fila.update(todas_metricas(y, p, w, UMBRALES[nombre]))  # Añade todas las métricas.
    intercepto, pendiente, convergencia = calibracion_logistica(y, p, w)  # Estima calibración externa.
    fila.update({'intercepto_calibracion': intercepto, 'pendiente_calibracion': pendiente, 'convergencia_calibracion': convergencia})  # Registra calibración.
    filas_globales.append(fila)  # Conserva la fila.
    curva = curva_calibracion(y, p, w)  # Construye calibración agrupada.
    curva.insert(0, 'modelo', nombre)  # Identifica el modelo.
    curvas.append(curva)  # Conserva la curva.
tabla_global = pd.DataFrame(filas_globales)  # Consolida métricas puntuales.
tabla_calibracion = pd.concat(curvas, ignore_index=True)  # Consolida deciles.

# BLOQUE 5: estructura del bootstrap estratificado por UPM.
pares = prueba[['estrato', 'upm']].drop_duplicates().sort_values(['estrato', 'upm']).reset_index(drop=True)  # Enumera conglomerados de prueba.
mapa_cluster = pd.Series(np.arange(len(pares)), index=pd.MultiIndex.from_frame(pares))  # Asigna un código a cada UPM.
codigo_fila = mapa_cluster.loc[pd.MultiIndex.from_frame(prueba[['estrato', 'upm']])].to_numpy(dtype=int)  # Vincula cada fila a su UPM.
clusters_por_estrato = [indices.to_numpy(dtype=int) for _, indices in pares.groupby('estrato', observed=True).groups.items()]  # Agrupa códigos por estrato.
generador = np.random.default_rng(CONFIG['semilla_bootstrap'])  # Inicializa el remuestreo reproducible.
metricas_boot = {(modelo, metrica): [] for modelo in CONFIG['modelos'] for metrica in CONFIG['metricas_globales']}  # Reserva réplicas globales.
diferencias_boot = {metrica: [] for metrica in ['roc_auc', 'pr_auc', 'brier', 'log_loss', 'exactitud_balanceada']}  # Reserva comparaciones pareadas.
grupos_definidos = [('p02', '1', '2', 'Mujer menos hombre'), ('area', '1', '2', 'Rural menos urbana')]  # Define orden de brechas.
brechas_boot = {(modelo, variable, metrica): [] for modelo in ['logistica', 'boosting'] for variable, _, _, _ in grupos_definidos for metrica in ['roc_auc', 'brier', 'sensibilidad', 'especificidad']}  # Reserva brechas por grupo.
replicas_validas = 0  # Cuenta réplicas utilizables.
for replica in range(CONFIG['replicas_bootstrap']):  # Recorre las mil réplicas preespecificadas.
    multiplicidad_cluster = np.zeros(len(pares), dtype=int)  # Inicializa multiplicidades.
    for indices in clusters_por_estrato:  # Recorre estratos de prueba.
        seleccion = generador.choice(indices, size=len(indices), replace=True)  # Remuestrea UPM dentro del estrato.
        multiplicidad_cluster += np.bincount(seleccion, minlength=len(pares))  # Acumula selecciones repetidas.
    w_replica = w * multiplicidad_cluster[codigo_fila]  # Lleva la multiplicidad a cada persona.
    resultados_replica = {}  # Reserva métricas de los modelos en la réplica.
    try:  # Protege contra una réplica degenerada improbable.
        for nombre in CONFIG['modelos']:  # Recorre modelos.
            resultado = todas_metricas(y, prueba[f'p_{nombre}'], w_replica, UMBRALES[nombre])  # Calcula métricas con pesos remuestreados.
            resultados_replica[nombre] = resultado  # Conserva el resultado.
            for metrica in CONFIG['metricas_globales']:  # Recorre métricas globales.
                metricas_boot[(nombre, metrica)].append(resultado[metrica])  # Guarda la réplica.
        for metrica in diferencias_boot:  # Recorre métricas comparativas.
            diferencias_boot[metrica].append(resultados_replica['boosting'][metrica] - resultados_replica['logistica'][metrica])  # Calcula boosting menos logística.
        for nombre in ['logistica', 'boosting']:  # Recorre modelos auditados.
            for variable, referencia, comparacion, _ in grupos_definidos:  # Recorre sexo y área.
                resultados_grupo = {}  # Reserva los dos grupos.
                for codigo in [referencia, comparacion]:  # Recorre referencia y comparación.
                    mascara = prueba[variable].eq(codigo).to_numpy()  # Identifica el grupo.
                    resultados_grupo[codigo] = todas_metricas(y[mascara], prueba.loc[mascara, f'p_{nombre}'], w_replica[mascara], UMBRALES[nombre])  # Calcula métricas del grupo.
                for metrica in ['roc_auc', 'brier', 'sensibilidad', 'especificidad']:  # Recorre dimensiones de equidad.
                    brechas_boot[(nombre, variable, metrica)].append(resultados_grupo[comparacion][metrica] - resultados_grupo[referencia][metrica])  # Registra comparación menos referencia.
        replicas_validas += 1  # Cuenta la réplica completa.
    except ValueError:  # Captura ausencia accidental de una clase.
        continue  # Omite únicamente la réplica degenerada.
assert replicas_validas >= int(0.95 * CONFIG['replicas_bootstrap'])  # Exige al menos 95 % de réplicas completas.

# BLOQUE 6: intervalos globales, comparación pareada y auditoría de grupos.
filas_ic = []  # Reserva una fila por modelo y métrica.
for _, fila in tabla_global.iterrows():  # Recorre estimaciones puntuales.
    for metrica in CONFIG['metricas_globales']:  # Recorre métricas.
        inferior, superior, validas = intervalo_percentil(metricas_boot[(fila['modelo'], metrica)])  # Calcula intervalo.
        filas_ic.append({'modelo': fila['modelo'], 'metrica': metrica, 'estimacion': fila[metrica], 'ic95_inferior': inferior, 'ic95_superior': superior, 'replicas_validas': validas, 'metodo_ic': 'bootstrap UPM dentro de estrato'})  # Registra resultado científico.
tabla_ic = pd.DataFrame(filas_ic)  # Consolida intervalos.
filas_comparacion = []  # Reserva diferencias entre los dos modelos.
for metrica, replicas in diferencias_boot.items():  # Recorre comparaciones pareadas.
    punto = float(tabla_global.loc[tabla_global['modelo'] == 'boosting', metrica].iloc[0] - tabla_global.loc[tabla_global['modelo'] == 'logistica', metrica].iloc[0])  # Calcula diferencia puntual.
    inferior, superior, validas = intervalo_percentil(replicas)  # Calcula IC pareado.
    direccion_favorable = 'mayor' if metrica in ['roc_auc', 'pr_auc', 'exactitud_balanceada'] else 'menor'  # Define el sentido deseable.
    filas_comparacion.append({'comparacion': 'boosting menos logistica', 'metrica': metrica, 'diferencia': punto, 'ic95_inferior': inferior, 'ic95_superior': superior, 'replicas_validas': validas, 'direccion_favorable': direccion_favorable})  # Registra la diferencia.
tabla_comparacion = pd.DataFrame(filas_comparacion)  # Consolida comparación.
filas_grupos = []  # Reserva métricas puntuales por grupo.
filas_brechas = []  # Reserva brechas e intervalos.
for nombre in ['logistica', 'boosting']:  # Recorre modelos finales.
    for variable, referencia, comparacion, etiqueta_brecha in grupos_definidos:  # Recorre dimensiones.
        resultados_punto = {}  # Reserva resultados por categoría.
        for codigo in [referencia, comparacion]:  # Recorre los dos grupos.
            mascara = prueba[variable].eq(codigo).to_numpy()  # Selecciona el grupo.
            resultado = todas_metricas(y[mascara], prueba.loc[mascara, f'p_{nombre}'], w[mascara], UMBRALES[nombre])  # Calcula métricas puntuales.
            resultados_punto[codigo] = resultado  # Conserva el resultado.
            filas_grupos.append({'modelo': nombre, 'variable_grupo': variable, 'codigo_grupo': codigo, 'n': int(mascara.sum()), 'upm': int(prueba.loc[mascara, 'upm'].nunique()), **resultado})  # Registra soporte y métricas.
        for metrica in ['roc_auc', 'brier', 'sensibilidad', 'especificidad']:  # Recorre medidas de brecha.
            punto = resultados_punto[comparacion][metrica] - resultados_punto[referencia][metrica]  # Calcula comparación menos referencia.
            inferior, superior, validas = intervalo_percentil(brechas_boot[(nombre, variable, metrica)])  # Calcula IC pareado por UPM.
            filas_brechas.append({'modelo': nombre, 'variable': variable, 'brecha': etiqueta_brecha, 'metrica': metrica, 'diferencia': punto, 'ic95_inferior': inferior, 'ic95_superior': superior, 'replicas_validas': validas})  # Registra brecha.
tabla_grupos = pd.DataFrame(filas_grupos)  # Consolida métricas de grupos.
tabla_brechas = pd.DataFrame(filas_brechas)  # Consolida brechas.
tabla_global.to_csv(SALIDAS / '01_metricas_prueba_globales.csv', index=False, encoding='utf-8-sig')  # Exporta estimaciones puntuales.
tabla_ic.to_csv(SALIDAS / '02_metricas_prueba_ic95.csv', index=False, encoding='utf-8-sig')  # Exporta intervalos.
tabla_comparacion.to_csv(SALIDAS / '03_comparacion_pareada_modelos.csv', index=False, encoding='utf-8-sig')  # Exporta comparación principal.
tabla_calibracion.to_csv(SALIDAS / '04_calibracion_prueba_deciles.csv', index=False, encoding='utf-8-sig')  # Exporta calibración.
tabla_grupos.to_csv(SALIDAS / '05_metricas_prueba_por_grupo.csv', index=False, encoding='utf-8-sig')  # Exporta auditoría de grupos.
tabla_brechas.to_csv(SALIDAS / '06_brechas_desempeno_ic95.csv', index=False, encoding='utf-8-sig')  # Exporta brechas e IC.

# BLOQUE 7: figuras de desempeño, calibración y grupos.
figura, ejes = plt.subplots(1, 2, figsize=(11, 4.8))  # Crea curvas ROC y precisión-recall.
for nombre, color in [('logistica', AZUL), ('boosting', NARANJA)]:  # Recorre modelos principales.
    p = prueba[f'p_{nombre}'].to_numpy()  # Recupera probabilidades.
    fpr, tpr, _ = roc_curve(y, p, sample_weight=w)  # Calcula curva ROC ponderada.
    precision_curva, recall_curva, _ = precision_recall_curve(y, p, sample_weight=w)  # Calcula curva PR ponderada.
    auc = tabla_global.loc[tabla_global['modelo'] == nombre, 'roc_auc'].iloc[0]  # Recupera AUC.
    pr = tabla_global.loc[tabla_global['modelo'] == nombre, 'pr_auc'].iloc[0]  # Recupera PR-AUC.
    ejes[0].plot(fpr, tpr, color=color, label=f'{nombre.capitalize()} (AUC={auc:.3f})')  # Dibuja ROC.
    ejes[1].plot(recall_curva, precision_curva, color=color, label=f'{nombre.capitalize()} (PR-AUC={pr:.3f})')  # Dibuja PR.
ejes[0].plot([0, 1], [0, 1], '--', color=GRIS, linewidth=1)  # Añade referencia aleatoria.
ejes[0].set(xlabel='1 − especificidad', ylabel='Sensibilidad', title='Curva ROC en prueba reservada')  # Etiqueta ROC.
ejes[1].axhline(media_ponderada(y, w), linestyle='--', color=GRIS, linewidth=1, label='Prevalencia ponderada')  # Añade referencia PR.
ejes[1].set(xlabel='Sensibilidad', ylabel='Precisión', title='Curva precisión–recall en prueba')  # Etiqueta PR.
for eje in ejes:  # Recorre paneles.
    eje.grid(color='#D1D5DB', linewidth=0.6)  # Añade guías.
    eje.legend(frameon=False)  # Identifica modelos.
figura.text(0.01, 0.005, 'Fuente: ENEMDU anual 2025. Evaluación única ponderada en UPM reservadas.', fontsize=7, color='#374151')  # Añade nota.
figura.tight_layout(rect=(0, 0.05, 1, 1))  # Ajusta espacios.
figura.savefig(FIGURAS / '01_curvas_roc_pr.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '01_curvas_roc_pr.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.
figura, eje = plt.subplots(figsize=(6.8, 5.6))  # Crea gráfico de calibración.
for nombre, color, marcador in [('base', GRIS, 's'), ('logistica', AZUL, 'o'), ('boosting', NARANJA, '^')]:  # Recorre modelos.
    datos = tabla_calibracion.loc[tabla_calibracion['modelo'] == nombre]  # Selecciona deciles.
    eje.plot(100 * datos['prediccion_media'], 100 * datos['proporcion_observada'], marker=marcador, color=color, label=nombre.capitalize())  # Dibuja calibración.
eje.plot([0, 100], [0, 100], '--', color='#111827', linewidth=1, label='Ideal')  # Añade diagonal ideal.
eje.set(xlabel='Probabilidad predicha ponderada (%)', ylabel='Proporción observada ponderada (%)', xlim=(0, 100), ylim=(0, 100))  # Define escala.
eje.set_title('Calibración en prueba reservada', loc='left', fontweight='bold')  # Titula la figura.
eje.grid(color='#D1D5DB', linewidth=0.6)  # Añade guías.
eje.legend(frameon=False)  # Identifica modelos.
figura.tight_layout()  # Ajusta espacios.
figura.savefig(FIGURAS / '02_calibracion_prueba.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '02_calibracion_prueba.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.
metricas_panel = ['roc_auc', 'pr_auc', 'brier', 'exactitud_balanceada']  # Define métricas comparables.
figura, ejes = plt.subplots(2, 2, figsize=(9.5, 7.2))  # Crea cuatro paneles con IC.
for eje, metrica in zip(ejes.flat, metricas_panel):  # Recorre paneles.
    datos = tabla_ic.loc[(tabla_ic['metrica'] == metrica) & tabla_ic['modelo'].isin(['logistica', 'boosting'])]  # Selecciona modelos.
    posiciones = np.arange(len(datos))  # Define posiciones.
    errores = np.vstack([datos['estimacion'] - datos['ic95_inferior'], datos['ic95_superior'] - datos['estimacion']])  # Calcula longitudes de IC.
    eje.errorbar(datos['estimacion'], posiciones, xerr=errores, fmt='o', color=AZUL, capsize=3)  # Dibuja puntos e intervalos.
    eje.set_yticks(posiciones, labels=datos['modelo'].str.capitalize())  # Etiqueta modelos.
    eje.set_title(metrica.replace('_', ' ').upper(), loc='left', fontweight='bold')  # Titula el panel.
    eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Añade guías.
figura.suptitle('Desempeño final con IC 95 % por UPM', x=0.01, ha='left', fontweight='bold')  # Titula el conjunto.
figura.tight_layout(rect=(0, 0, 1, 0.95))  # Ajusta espacios.
figura.savefig(FIGURAS / '03_metricas_finales_ic95.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '03_metricas_finales_ic95.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.
datos_sensibilidad = tabla_grupos.loc[tabla_grupos['modelo'].eq('boosting')].copy()  # Selecciona boosting para auditoría visual.
datos_sensibilidad['grupo'] = datos_sensibilidad['variable_grupo'] + '=' + datos_sensibilidad['codigo_grupo'].astype(str)  # Crea etiquetas compactas.
figura, eje = plt.subplots(figsize=(7.8, 4.8))  # Crea gráfico de sensibilidad por grupo.
eje.bar(datos_sensibilidad['grupo'], 100 * datos_sensibilidad['sensibilidad'], color=[AZUL, NARANJA, VERDE, GRIS])  # Dibuja sensibilidad.
eje.set_ylabel('Sensibilidad ponderada (%)')  # Define la métrica.
eje.set_title('Boosting: sensibilidad por sexo y área', loc='left', fontweight='bold')  # Titula la figura.
eje.set_ylim(0, 100)  # Usa escala completa.
eje.grid(axis='y', color='#D1D5DB', linewidth=0.6)  # Añade guías.
figura.text(0.01, 0.005, 'Códigos: p02 1=hombre, 2=mujer; área 1=urbana, 2=rural. Umbral global congelado: 0,705.', fontsize=7, color='#374151')  # Explica categorías.
figura.tight_layout(rect=(0, 0.06, 1, 1))  # Ajusta espacios.
figura.savefig(FIGURAS / '04_sensibilidad_grupos.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '04_sensibilidad_grupos.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.

# BLOQUE 8: resumen, manifiesto y cierre irreversible de la evaluación.
def valor_tabla(tabla, modelo, columna):  # Recupera un escalar de resultados.
    return float(tabla.loc[tabla['modelo'] == modelo, columna].iloc[0])  # Devuelve el valor solicitado.

resumen = {'estado': 'evaluacion_unica_completada', 'fecha': CONFIG['fecha_evaluacion'], 'filas_prueba': len(prueba), 'upm_prueba': prueba['upm'].nunique(), 'prevalencia_ponderada_prueba': media_ponderada(y, w), 'roc_auc_logistica': valor_tabla(tabla_global, 'logistica', 'roc_auc'), 'roc_auc_boosting': valor_tabla(tabla_global, 'boosting', 'roc_auc'), 'diferencia_auc_boosting_menos_logistica': float(tabla_comparacion.loc[tabla_comparacion['metrica'] == 'roc_auc', 'diferencia'].iloc[0]), 'brier_logistica': valor_tabla(tabla_global, 'logistica', 'brier'), 'brier_boosting': valor_tabla(tabla_global, 'boosting', 'brier'), 'replicas_bootstrap_validas': replicas_validas, 'hiperparametros_reajustados': False, 'umbrales_reajustados': False, 'prueba_reservada_evaluada': True}  # Consolida el resultado final.
(SALIDAS / '07_resumen_evaluacion.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el resumen científico.
estado_final = {'estado': 'completada_y_cerrada', 'fecha': CONFIG['fecha_evaluacion'], 'sha256_prueba': sha256(PRUEBA), 'sha256_predicciones': sha256(PREDICCIONES / 'predicciones_prueba_unica.csv.gz'), 'modelos_aplicados': ['logistica_predictiva_congelada.joblib', 'boosting_congelado.joblib'], 'umbrales_aplicados': UMBRALES, 'replicas_bootstrap_validas': replicas_validas, 'se_permite_repetir_puntuacion': False}  # Registra el cierre.
MARCADOR.write_text(json.dumps(estado_final, ensure_ascii=False, indent=2), encoding='utf-8')  # Sustituye el estado iniciado por el cierre completo.
productos = sorted(list(SALIDAS.glob('*.csv')) + list(SALIDAS.glob('*.json')) + list(FIGURAS.glob('*.*')) + [PREDICCIONES / 'predicciones_prueba_unica.csv.gz'])  # Reúne entregables.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Calcula huellas.
manifiesto.to_csv(SALIDAS / '08_manifiesto_productos.csv', index=False, encoding='utf-8-sig')  # Exporta el manifiesto.
assert len(prueba) == 7791  # Exige el tamaño reservado documentado.
assert prueba.groupby('upm')['particion_ml'].nunique().max() == 1  # Reconfirma consistencia por UPM.
assert tabla_ic[['estimacion', 'ic95_inferior', 'ic95_superior']].apply(lambda fila: fila.iloc[1] <= fila.iloc[0] <= fila.iloc[2], axis=1).all()  # Exige puntos dentro de sus IC.
assert not resumen['hiperparametros_reajustados'] and not resumen['umbrales_reajustados']  # Exige decisiones intactas.
print(json.dumps(resumen, ensure_ascii=False, indent=2))  # Presenta el resultado final.
