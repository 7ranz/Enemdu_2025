# ETAPA 7: desarrollo, asociaciones ajustadas y modelado interpretable.
# ARCHIVO: 06_desarrollar_modelos.py; usa solo entrenamiento para la predicción y conserva la prueba cerrada.
# BLOQUE 1: dependencias, rutas y decisiones congeladas.
import hashlib  # Calcula huellas para asegurar trazabilidad.
import json  # Lee la configuración y escribe resultados estructurados.
import platform  # Registra la versión de Python usada.
from pathlib import Path  # Maneja rutas de forma portable.
import joblib  # Guarda los modelos congelados.
import matplotlib  # Configura gráficos sin interfaz.
matplotlib.use('Agg')  # Permite ejecutar el programa automáticamente.
import matplotlib.pyplot as plt  # Genera figuras científicas.
import numpy as np  # Ejecuta álgebra, agregaciones y simulaciones de permutación.
import pandas as pd  # Lee, transforma y exporta los datos tabulares.
from scipy import optimize, stats  # Ajusta calibración y calcula inferencia.
from scipy.special import expit  # Evalúa la función logística de forma estable.
import sklearn  # Registra la versión de la biblioteca de modelado.
from sklearn.compose import ColumnTransformer  # Aplica transformaciones distintas por tipo de variable.
from sklearn.ensemble import HistGradientBoostingClassifier  # Implementa el modelo de árboles boosting.
from sklearn.impute import SimpleImputer  # Define un tratamiento reproducible de faltantes futuros.
from sklearn.linear_model import LogisticRegression  # Implementa la regresión logística predictiva.
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score  # Calcula métricas probabilísticas.
from sklearn.pipeline import Pipeline  # Une preprocesamiento y estimador sin fuga entre pliegues.
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler  # Codifica variables para cada modelo.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto.
CONFIG = json.loads((RAIZ / 'config/modelado_v1.json').read_text(encoding='utf-8'))  # Recupera las decisiones preespecificadas.
ENTRADA = RAIZ / CONFIG['archivo_desarrollo']  # Localiza exclusivamente el archivo de desarrollo.
BASE_COMPLETA = RAIZ / 'data/processed/personas_tratada_completa.csv.gz'  # Localiza la base completa para inferencia de dominio.
SALIDAS = RAIZ / 'reports/eda07_modelado'  # Define la carpeta de tablas y controles.
FIGURAS = RAIZ / 'reports/figures/eda07_modelado'  # Define la carpeta de figuras científicas.
MODELOS = RAIZ / 'models'  # Define la carpeta de modelos congelados.
OOF_DIR = RAIZ / 'data/processed/modelado/desarrollo'  # Define la carpeta protegida de predicciones internas.
for carpeta in [SALIDAS, FIGURAS, MODELOS, OOF_DIR]:  # Recorre todas las carpetas nuevas.
    carpeta.mkdir(parents=True, exist_ok=True)  # Crea cada carpeta si todavía no existe.
SEMILLA = int(CONFIG['semilla'])  # Fija la semilla documentada.
NUMERICAS = CONFIG['predictores_numericos']  # Recupera los predictores numéricos autorizados.
CATEGORICAS = CONFIG['predictores_categoricos']  # Recupera los predictores categóricos autorizados.
PREDICTORES = NUMERICAS + CATEGORICAS  # Construye la lista blanca completa.
AZUL = '#0072B2'  # Define un azul accesible.
NARANJA = '#E69F00'  # Define un naranja accesible.
VERDE = '#009E73'  # Define un verde accesible.
ROJO = '#D55E00'  # Define un rojo accesible.
GRIS = '#6B7280'  # Define un gris de referencia.
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 12, 'axes.labelsize': 9})  # Fija un estilo reproducible.

# BLOQUE 2: funciones generales de integridad, limpieza y métricas ponderadas.
def sha256(ruta):  # Calcula la huella SHA-256 de un archivo permitido.
    objeto = hashlib.sha256()  # Inicializa el algoritmo criptográfico.
    with ruta.open('rb') as archivo:  # Abre el archivo en modo binario.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee bloques sin cargar todo en memoria.
            objeto.update(bloque)  # Incorpora cada bloque a la huella.
    return objeto.hexdigest()  # Devuelve la huella hexadecimal.

def normalizar_codigo(serie):  # Homogeneiza códigos categóricos leídos desde CSV.
    texto = serie.astype('string').str.strip()  # Convierte valores a texto sin espacios laterales.
    return texto.str.replace(r'\.0$', '', regex=True)  # Elimina el decimal artificial de códigos enteros.

def media_ponderada(valores, pesos):  # Calcula una media con factor de expansión.
    return float(np.average(np.asarray(valores, dtype=float), weights=np.asarray(pesos, dtype=float)))  # Devuelve un escalar reproducible.

def metricas_probabilidad(y, p, w):  # Calcula métricas que no requieren umbral.
    y = np.asarray(y, dtype=int)  # Normaliza el objetivo binario.
    p = np.clip(np.asarray(p, dtype=float), 1e-7, 1 - 1e-7)  # Evita logaritmos infinitos.
    w = np.asarray(w, dtype=float)  # Normaliza los pesos.
    return {'roc_auc': roc_auc_score(y, p, sample_weight=w), 'pr_auc': average_precision_score(y, p, sample_weight=w), 'brier': brier_score_loss(y, p, sample_weight=w), 'log_loss': log_loss(y, p, sample_weight=w, labels=[0, 1])}  # Devuelve discriminación y calibración global.

def metricas_umbral(y, p, w, umbral):  # Calcula métricas de clasificación para un umbral congelable.
    y = np.asarray(y, dtype=int)  # Normaliza el objetivo.
    d = np.asarray(p, dtype=float) >= float(umbral)  # Convierte probabilidades en decisiones.
    w = np.asarray(w, dtype=float)  # Normaliza los pesos.
    tp = w[(y == 1) & d].sum()  # Suma verdaderos positivos ponderados.
    fn = w[(y == 1) & ~d].sum()  # Suma falsos negativos ponderados.
    tn = w[(y == 0) & ~d].sum()  # Suma verdaderos negativos ponderados.
    fp = w[(y == 0) & d].sum()  # Suma falsos positivos ponderados.
    sensibilidad = tp / (tp + fn)  # Calcula sensibilidad ponderada.
    especificidad = tn / (tn + fp)  # Calcula especificidad ponderada.
    precision = tp / (tp + fp) if tp + fp > 0 else np.nan  # Calcula precisión positiva ponderada.
    exactitud = (tp + tn) / (tp + tn + fp + fn)  # Calcula exactitud ponderada.
    return {'umbral': float(umbral), 'sensibilidad': sensibilidad, 'especificidad': especificidad, 'precision': precision, 'exactitud': exactitud, 'exactitud_balanceada': (sensibilidad + especificidad) / 2, 'tasa_predicha_positiva': (tp + fp) / (tp + tn + fp + fn)}  # Devuelve métricas de decisión.

def seleccionar_umbral(y, p, w):  # Selecciona el umbral solo con predicciones fuera de pliegue.
    inicio, fin, paso = CONFIG['rejilla_umbral']  # Recupera los límites preespecificados.
    candidatos = np.arange(inicio, fin + paso / 2, paso)  # Construye la rejilla cerrada.
    tabla = pd.DataFrame([metricas_umbral(y, p, w, valor) for valor in candidatos])  # Evalúa todos los umbrales.
    tabla['distancia_05'] = (tabla['umbral'] - 0.5).abs()  # Prepara el desempate más conservador.
    mejor = tabla.sort_values(['exactitud_balanceada', 'distancia_05', 'umbral'], ascending=[False, True, True]).iloc[0]  # Aplica la regla congelada.
    return float(mejor['umbral']), tabla.drop(columns='distancia_05')  # Devuelve umbral y trayectoria auditable.

def calibracion_logistica(y, p, w):  # Estima intercepto y pendiente de calibración ponderados.
    y = np.asarray(y, dtype=float)  # Convierte el objetivo a arreglo.
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)  # Evita logits infinitos.
    w = np.asarray(w, dtype=float)  # Convierte pesos a arreglo.
    z = np.log(p / (1 - p))  # Transforma probabilidades a logits.
    def objetivo(parametros):  # Define la pérdida logística ponderada.
        prediccion = expit(parametros[0] + parametros[1] * z)  # Calcula probabilidad recalibrada.
        return -np.sum(w * (y * np.log(prediccion + 1e-12) + (1 - y) * np.log(1 - prediccion + 1e-12))) / w.sum()  # Devuelve pérdida promedio.
    ajuste = optimize.minimize(objetivo, x0=np.array([0.0, 1.0]), method='BFGS')  # Ajusta dos parámetros sin modificar el modelo.
    return {'intercepto_calibracion': float(ajuste.x[0]), 'pendiente_calibracion': float(ajuste.x[1]), 'convergencia_calibracion': bool(ajuste.success)}  # Devuelve diagnóstico de calibración.

def curva_calibracion(y, p, w, grupos=10):  # Resume calibración en grupos de masa ponderada semejante.
    tabla = pd.DataFrame({'y': np.asarray(y), 'p': np.asarray(p), 'w': np.asarray(w)}).sort_values('p').reset_index(drop=True)  # Ordena predicciones.
    tabla['acumulado'] = tabla['w'].cumsum() / tabla['w'].sum()  # Calcula masa ponderada acumulada.
    tabla['grupo'] = np.minimum((tabla['acumulado'] * grupos).astype(int), grupos - 1) + 1  # Asigna deciles ponderados.
    filas = []  # Reserva resultados por grupo.
    for grupo, bloque in tabla.groupby('grupo', observed=True):  # Recorre los grupos observados.
        filas.append({'grupo': int(grupo), 'n': len(bloque), 'peso': bloque['w'].sum(), 'prediccion_media': media_ponderada(bloque['p'], bloque['w']), 'proporcion_observada': media_ponderada(bloque['y'], bloque['w'])})  # Resume predicción y resultado.
    return pd.DataFrame(filas)  # Devuelve la curva tabular.

# BLOQUE 3: lectura exclusiva de entrenamiento y controles de separación.
tipos_entrenamiento = {columna: 'string' for columna in ['id_persona', 'id_vivienda_sin_mes', 'id_hogar_sin_mes', 'clave_posicion_sin_mes', 'upm', 'estrato', 'particion_ml', 'p02', 'p06', 'p07', 'p10a', 'p15', 'prov', 'area', 'mes']}  # Define tipos de identificadores y categorías.
entrenamiento = pd.read_csv(ENTRADA, dtype=tipos_entrenamiento, encoding='utf-8-sig')  # Lee únicamente desarrollo.
for columna in CATEGORICAS:  # Recorre las variables categóricas autorizadas.
    entrenamiento[columna] = normalizar_codigo(entrenamiento[columna])  # Normaliza cada código.
entrenamiento['mes'] = entrenamiento['mes'].str.zfill(2)  # Conserva el mes con dos dígitos.
entrenamiento['fexp'] = pd.to_numeric(entrenamiento['fexp'], errors='raise')  # Exige pesos numéricos.
entrenamiento['y_adecuado'] = pd.to_numeric(entrenamiento['y_adecuado'], errors='raise').astype(int)  # Exige objetivo binario.
entrenamiento['pliegue_cv'] = pd.to_numeric(entrenamiento['pliegue_cv'], errors='raise').astype(int)  # Exige cinco pliegues enteros.
entrenamiento['edad_limite_inferior'] = pd.to_numeric(entrenamiento['edad_limite_inferior'], errors='raise')  # Convierte edad a número.
entrenamiento['edad_98_mas'] = pd.to_numeric(entrenamiento['edad_98_mas'], errors='raise')  # Convierte la marca abierta a número.
assert set(entrenamiento['particion_ml']) == {'entrenamiento'}  # Impide mezclar otra partición.
assert set(entrenamiento['pliegue_cv']) == set(CONFIG['pliegues'])  # Exige los cinco pliegues previstos.
assert entrenamiento.groupby('upm')['pliegue_cv'].nunique().max() == 1  # Exige que cada UPM pertenezca a un solo pliegue.
assert entrenamiento['fexp'].gt(0).all()  # Exige pesos positivos.
assert set(entrenamiento['y_adecuado']) == {0, 1}  # Exige las dos clases.
assert entrenamiento[PREDICTORES].notna().all().all()  # Exige predictores completos en desarrollo.
X = entrenamiento[PREDICTORES].copy()  # Separa solo la lista blanca de predictores.
y = entrenamiento['y_adecuado'].to_numpy()  # Extrae el objetivo.
w = entrenamiento['fexp'].to_numpy(dtype=float)  # Extrae el factor de expansión.
fold = entrenamiento['pliegue_cv'].to_numpy(dtype=int)  # Extrae el pliegue preasignado.

# BLOQUE 4: constructores de tuberías sin fuga de preprocesamiento.
def construir_logistica(c):  # Construye una regresión logística para un valor de regularización.
    numerico = Pipeline([('imputar', SimpleImputer(strategy='median')), ('escalar', StandardScaler())])  # Prepara variables numéricas dentro de cada pliegue.
    categorico = Pipeline([('imputar', SimpleImputer(strategy='most_frequent')), ('codificar', OneHotEncoder(handle_unknown='ignore', drop='first'))])  # Codifica categorías dentro de cada pliegue.
    preprocesador = ColumnTransformer([('numerico', numerico, NUMERICAS), ('categorico', categorico, CATEGORICAS)])  # Une ambas ramas.
    estimador = LogisticRegression(C=float(c), max_iter=2000, solver='lbfgs', random_state=SEMILLA)  # Define el modelo regularizado.
    return Pipeline([('preprocesar', preprocesador), ('modelo', estimador)])  # Devuelve la tubería completa.

def construir_boosting(parametros):  # Construye el modelo de árboles para un conjunto de hiperparámetros.
    numerico = Pipeline([('imputar', SimpleImputer(strategy='median'))])  # Conserva escalas numéricas originales.
    categorico = Pipeline([('imputar', SimpleImputer(strategy='most_frequent')), ('codificar', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, encoded_missing_value=-1))])  # Codifica categorías sin usar el objetivo.
    preprocesador = ColumnTransformer([('numerico', numerico, NUMERICAS), ('categorico', categorico, CATEGORICAS)], sparse_threshold=0)  # Produce una matriz densa pequeña.
    mascara_categorica = [False] * len(NUMERICAS) + [True] * len(CATEGORICAS)  # Identifica variables categóricas para las particiones.
    estimador = HistGradientBoostingClassifier(**parametros, categorical_features=mascara_categorica, early_stopping=False, random_state=SEMILLA)  # Define boosting reproducible.
    return Pipeline([('preprocesar', preprocesador), ('modelo', estimador)])  # Devuelve la tubería completa.

def ajustar_con_pesos(modelo, x_ajuste, y_ajuste, w_ajuste):  # Ajusta cualquier tubería con pesos normalizados.
    pesos = np.asarray(w_ajuste, dtype=float) / np.mean(w_ajuste)  # Normaliza solo la escala numérica del peso.
    return modelo.fit(x_ajuste, y_ajuste, modelo__sample_weight=pesos)  # Ajusta y devuelve el modelo.

def evaluar_candidato(nombre, identificador, constructor):  # Evalúa un candidato en los cinco pliegues intactos.
    filas = []  # Reserva una fila por pliegue.
    for k in CONFIG['pliegues']:  # Recorre los pliegues preasignados.
        indice_validacion = fold == k  # Selecciona UPM del pliegue de validación.
        indice_ajuste = ~indice_validacion  # Selecciona los otros cuatro pliegues.
        modelo = construir_logistica(constructor) if nombre == 'logistica' else construir_boosting(constructor)  # Construye desde cero dentro del pliegue.
        ajustar_con_pesos(modelo, X.loc[indice_ajuste], y[indice_ajuste], w[indice_ajuste])  # Ajusta sin observar validación.
        probabilidad = modelo.predict_proba(X.loc[indice_validacion])[:, 1]  # Predice el pliegue excluido.
        fila = {'modelo': nombre, 'candidato': identificador, 'pliegue': k, 'n_validacion': int(indice_validacion.sum()), 'upm_validacion': int(entrenamiento.loc[indice_validacion, 'upm'].nunique())}  # Registra soporte independiente.
        fila.update(metricas_probabilidad(y[indice_validacion], probabilidad, w[indice_validacion]))  # Añade métricas ponderadas.
        filas.append(fila)  # Conserva la fila.
    return filas  # Devuelve los cinco resultados.

# BLOQUE 5: selección interna de hiperparámetros.
resultados_cv = []  # Inicializa el registro completo de candidatos.
for c in CONFIG['candidatos_logistica_C']:  # Recorre la rejilla logística.
    resultados_cv.extend(evaluar_candidato('logistica', f'C={c:g}', c))  # Evalúa el candidato en cinco pliegues.
for numero, parametros in enumerate(CONFIG['candidatos_boosting'], start=1):  # Recorre la rejilla de boosting.
    resultados_cv.extend(evaluar_candidato('boosting', f'B{numero}', parametros))  # Evalúa el candidato en cinco pliegues.
tabla_cv = pd.DataFrame(resultados_cv)  # Convierte todos los resultados a tabla.
tabla_cv.to_csv(SALIDAS / '01_resultados_cv_por_pliegue.csv', index=False, encoding='utf-8-sig')  # Exporta la evidencia detallada.
resumen_cv = tabla_cv.groupby(['modelo', 'candidato'], as_index=False).agg(roc_auc_media=('roc_auc', 'mean'), roc_auc_de=('roc_auc', 'std'), pr_auc_media=('pr_auc', 'mean'), brier_medio=('brier', 'mean'), log_loss_medio=('log_loss', 'mean'))  # Resume desempeño y variabilidad.
resumen_cv['rango_modelo'] = resumen_cv.groupby('modelo')['roc_auc_media'].rank(method='first', ascending=False).astype(int)  # Calcula rango preliminar por AUC.
seleccionados = {}  # Reserva el identificador ganador por modelo.
for nombre in ['logistica', 'boosting']:  # Recorre las dos familias.
    bloque = resumen_cv.loc[resumen_cv['modelo'] == nombre].sort_values(['roc_auc_media', 'brier_medio', 'candidato'], ascending=[False, True, True])  # Aplica selección y desempate.
    seleccionados[nombre] = bloque.iloc[0]['candidato']  # Congela el candidato ganador.
    resumen_cv.loc[resumen_cv['modelo'] == nombre, 'seleccionado'] = resumen_cv.loc[resumen_cv['modelo'] == nombre, 'candidato'].eq(seleccionados[nombre])  # Marca el ganador.
resumen_cv.to_csv(SALIDAS / '02_resumen_seleccion_hiperparametros.csv', index=False, encoding='utf-8-sig')  # Exporta la selección.
mejor_c = float(seleccionados['logistica'].split('=')[1])  # Recupera el C ganador.
indice_boosting = int(seleccionados['boosting'][1:]) - 1  # Recupera la posición del boosting ganador.
mejor_boosting = CONFIG['candidatos_boosting'][indice_boosting]  # Recupera sus hiperparámetros completos.

# BLOQUE 6: predicciones OOF definitivas y permutación de variables originales.
predicciones = pd.DataFrame({'id_persona': entrenamiento['id_persona'], 'upm': entrenamiento['upm'], 'estrato': entrenamiento['estrato'], 'pliegue_cv': fold, 'y_adecuado': y, 'fexp': w})  # Inicializa el archivo interno auditable.
predicciones['p_base'] = np.nan  # Reserva la probabilidad del modelo base.
predicciones['p_logistica'] = np.nan  # Reserva la probabilidad logística.
predicciones['p_boosting'] = np.nan  # Reserva la probabilidad de boosting.
importancias = []  # Reserva caídas de AUC por permutación.
for k in CONFIG['pliegues']:  # Recorre cada validación interna una sola vez más.
    indice_validacion = fold == k  # Identifica el pliegue excluido.
    indice_ajuste = ~indice_validacion  # Identifica los cuatro pliegues de ajuste.
    predicciones.loc[indice_validacion, 'p_base'] = media_ponderada(y[indice_ajuste], w[indice_ajuste])  # Predice prevalencia de ajuste.
    modelos_pliegue = {'logistica': construir_logistica(mejor_c), 'boosting': construir_boosting(mejor_boosting)}  # Construye los dos ganadores.
    for nombre, modelo in modelos_pliegue.items():  # Recorre los modelos seleccionados.
        ajustar_con_pesos(modelo, X.loc[indice_ajuste], y[indice_ajuste], w[indice_ajuste])  # Ajusta con cuatro pliegues.
        x_validacion = X.loc[indice_validacion].copy()  # Copia las covariables de validación.
        probabilidad = modelo.predict_proba(x_validacion)[:, 1]  # Obtiene predicciones OOF.
        predicciones.loc[indice_validacion, f'p_{nombre}'] = probabilidad  # Coloca cada predicción en su fila original.
        auc_original = roc_auc_score(y[indice_validacion], probabilidad, sample_weight=w[indice_validacion])  # Calcula AUC de referencia.
        for variable in PREDICTORES:  # Recorre variables originales, no columnas ficticias.
            for repeticion in range(CONFIG['repeticiones_permutacion']):  # Repite para estabilizar la importancia.
                generador = np.random.default_rng(SEMILLA + 10000 * k + 100 * PREDICTORES.index(variable) + repeticion)  # Crea una permutación reproducible.
                x_permutada = x_validacion.copy()  # Conserva intactos los datos originales.
                x_permutada[variable] = generador.permutation(x_permutada[variable].to_numpy())  # Rompe solo la asociación de una variable.
                probabilidad_permutada = modelo.predict_proba(x_permutada)[:, 1]  # Predice después de la permutación.
                auc_permutada = roc_auc_score(y[indice_validacion], probabilidad_permutada, sample_weight=w[indice_validacion])  # Evalúa la pérdida de discriminación.
                importancias.append({'modelo': nombre, 'pliegue': k, 'variable': variable, 'repeticion': repeticion + 1, 'auc_original': auc_original, 'auc_permutada': auc_permutada, 'caida_auc': auc_original - auc_permutada})  # Registra la importancia OOF.
assert predicciones[['p_base', 'p_logistica', 'p_boosting']].notna().all().all()  # Exige una predicción externa para cada fila.
predicciones.to_csv(OOF_DIR / 'predicciones_oof.csv.gz', index=False, encoding='utf-8-sig', compression='gzip')  # Guarda predicciones internas fuera de pliegue.
tabla_importancias = pd.DataFrame(importancias)  # Convierte permutaciones a tabla.
tabla_importancias.to_csv(SALIDAS / '07_importancia_permutacion_detalle.csv', index=False, encoding='utf-8-sig')  # Exporta evidencia completa.
resumen_importancias = tabla_importancias.groupby(['modelo', 'variable'], as_index=False).agg(caida_auc_media=('caida_auc', 'mean'), caida_auc_de=('caida_auc', 'std'), minimo=('caida_auc', 'min'), maximo=('caida_auc', 'max'))  # Resume importancia en validación.
resumen_importancias.to_csv(SALIDAS / '08_importancia_permutacion_resumen.csv', index=False, encoding='utf-8-sig')  # Exporta resumen interpretable.

# BLOQUE 7: métricas OOF, umbrales y diagnóstico entre grupos.
filas_metricas = []  # Reserva métricas globales.
umbrales = {}  # Reserva umbrales congelados.
curvas = []  # Reserva curvas de calibración.
trayectorias = []  # Reserva evaluación de umbrales.
for nombre in ['base', 'logistica', 'boosting']:  # Recorre la referencia y los dos modelos.
    probabilidad = predicciones[f'p_{nombre}'].to_numpy()  # Recupera la probabilidad OOF.
    umbral, trayectoria = seleccionar_umbral(y, probabilidad, w)  # Selecciona el punto de operación con desarrollo.
    umbrales[nombre] = umbral  # Congela el umbral.
    trayectoria.insert(0, 'modelo', nombre)  # Identifica el modelo en la trayectoria.
    trayectorias.append(trayectoria)  # Conserva la trayectoria.
    fila = {'modelo': nombre, 'n': len(y), 'upm': entrenamiento['upm'].nunique()}  # Registra soporte.
    fila.update(metricas_probabilidad(y, probabilidad, w))  # Añade métricas probabilísticas.
    fila.update(calibracion_logistica(y, probabilidad, w))  # Añade intercepto y pendiente.
    fila.update(metricas_umbral(y, probabilidad, w, umbral))  # Añade métricas de clasificación.
    filas_metricas.append(fila)  # Conserva el resultado.
    curva = curva_calibracion(y, probabilidad, w)  # Calcula deciles ponderados.
    curva.insert(0, 'modelo', nombre)  # Identifica el modelo.
    curvas.append(curva)  # Conserva la curva.
tabla_metricas = pd.DataFrame(filas_metricas)  # Consolida métricas globales.
tabla_metricas.to_csv(SALIDAS / '03_metricas_oof_globales.csv', index=False, encoding='utf-8-sig')  # Exporta el comparador interno.
pd.concat(trayectorias, ignore_index=True).to_csv(SALIDAS / '04_trayectoria_umbrales_oof.csv', index=False, encoding='utf-8-sig')  # Exporta la selección de umbrales.
tabla_calibracion = pd.concat(curvas, ignore_index=True)  # Consolida curvas.
tabla_calibracion.to_csv(SALIDAS / '05_calibracion_oof_deciles.csv', index=False, encoding='utf-8-sig')  # Exporta calibración tabular.
filas_grupos = []  # Reserva auditoría de desempeño por sexo y área.
for nombre in ['logistica', 'boosting']:  # Recorre modelos candidatos finales.
    for variable in ['p02', 'area']:  # Recorre los grupos prioritarios.
        for codigo, indices in entrenamiento.groupby(variable, observed=True).groups.items():  # Recorre categorías observadas.
            posiciones = entrenamiento.index.isin(indices)  # Convierte índices a máscara alineada.
            fila = {'modelo': nombre, 'variable_grupo': variable, 'codigo_grupo': codigo, 'n': int(posiciones.sum()), 'upm': int(entrenamiento.loc[posiciones, 'upm'].nunique())}  # Registra soporte del grupo.
            fila.update(metricas_probabilidad(y[posiciones], predicciones.loc[posiciones, f'p_{nombre}'], w[posiciones]))  # Añade métricas probabilísticas.
            fila.update(metricas_umbral(y[posiciones], predicciones.loc[posiciones, f'p_{nombre}'], w[posiciones], umbrales[nombre]))  # Añade métricas con el umbral global congelado.
            filas_grupos.append(fila)  # Conserva el grupo.
tabla_grupos = pd.DataFrame(filas_grupos)  # Consolida auditoría.
tabla_grupos.to_csv(SALIDAS / '06_metricas_oof_por_grupo.csv', index=False, encoding='utf-8-sig')  # Exporta diferencias descriptivas de desempeño.

# BLOQUE 8: ajuste final en desarrollo y congelación de artefactos predictivos.
modelo_logistico_final = construir_logistica(mejor_c)  # Reconstruye la logística ganadora.
modelo_boosting_final = construir_boosting(mejor_boosting)  # Reconstruye el boosting ganador.
ajustar_con_pesos(modelo_logistico_final, X, y, w)  # Ajusta la logística con todo desarrollo.
ajustar_con_pesos(modelo_boosting_final, X, y, w)  # Ajusta boosting con todo desarrollo.
joblib.dump(modelo_logistico_final, MODELOS / 'logistica_predictiva_congelada.joblib')  # Guarda la logística sin aplicar a prueba.
joblib.dump(modelo_boosting_final, MODELOS / 'boosting_congelado.joblib')  # Guarda boosting sin aplicar a prueba.

# BLOQUE 9: regresión logística de asociaciones con covarianza por diseño.
columnas_inferencia = ['estrato', 'upm', 'fexp', 'en_modelo_principal', 'y_adecuado', 'edad_limite_inferior', 'p02', 'p06', 'p07', 'p10a', 'p15', 'prov', 'area', 'mes']  # Limita la lectura a variables necesarias.
tipos_inferencia = {columna: 'string' for columna in ['estrato', 'upm', 'en_modelo_principal', 'p02', 'p06', 'p07', 'p10a', 'p15', 'prov', 'area', 'mes']}  # Conserva códigos exactos.
completa = pd.read_csv(BASE_COMPLETA, usecols=columnas_inferencia, dtype=tipos_inferencia, encoding='utf-8-sig')  # Lee todas las filas para conservar el diseño.
for columna in CATEGORICAS:  # Recorre categorías del modelo ajustado.
    completa[columna] = normalizar_codigo(completa[columna])  # Homogeneiza códigos.
completa['mes'] = completa['mes'].str.zfill(2)  # Conserva formato mensual.
completa['fexp'] = pd.to_numeric(completa['fexp'], errors='raise')  # Convierte pesos.
completa['edad_limite_inferior'] = pd.to_numeric(completa['edad_limite_inferior'], errors='coerce')  # Convierte edad.
indicador_dominio = completa['en_modelo_principal'].str.lower().eq('true')  # Identifica el dominio analítico completo.
dominio = completa.loc[indicador_dominio].copy()  # Extrae filas para estimar coeficientes.
dominio['y_adecuado'] = pd.to_numeric(dominio['y_adecuado'], errors='raise').astype(int)  # Recupera el objetivo binario.
dominio['edad_decadas_c40'] = (dominio['edad_limite_inferior'] - 40) / 10  # Centra edad y expresa décadas.
dominio['edad_decadas_c40_cuadrado'] = dominio['edad_decadas_c40'] ** 2  # Permite curvatura preespecificada.
matriz = pd.DataFrame({'Intercepto': np.ones(len(dominio)), 'edad_decadas_c40': dominio['edad_decadas_c40'].to_numpy(), 'edad_decadas_c40_cuadrado': dominio['edad_decadas_c40_cuadrado'].to_numpy()}, index=dominio.index)  # Inicia la matriz de diseño.
grupos_terminos = {'edad': ['edad_decadas_c40', 'edad_decadas_c40_cuadrado']}  # Inicia términos para pruebas globales.
for variable in ['p02', 'area', 'p10a', 'p06', 'p07', 'p15', 'prov', 'mes']:  # Recorre factores ajustados.
    referencia = CONFIG['referencias_asociaciones'][variable]  # Recupera la referencia documentada.
    niveles = sorted(dominio[variable].dropna().unique(), key=lambda valor: int(valor))  # Ordena códigos numéricamente.
    assert referencia in niveles  # Exige que la referencia exista.
    grupos_terminos[variable] = []  # Reserva términos del factor.
    for nivel in niveles:  # Recorre niveles observados.
        if nivel != referencia:  # Omite el nivel de referencia.
            nombre = f'{variable}[{nivel}]'  # Crea un nombre trazable.
            matriz[nombre] = dominio[variable].eq(nivel).astype(float)  # Añade la variable indicadora.
            grupos_terminos[variable].append(nombre)  # Conserva el término para Wald.
X_asoc = matriz.to_numpy(dtype=float)  # Convierte la matriz a arreglo.
y_asoc = dominio['y_adecuado'].to_numpy(dtype=float)  # Convierte el objetivo a arreglo.
w_asoc = dominio['fexp'].to_numpy(dtype=float)  # Recupera pesos del dominio.
w_asoc = w_asoc / w_asoc.mean()  # Normaliza escala sin cambiar estimadores.
beta = np.zeros(X_asoc.shape[1])  # Inicializa coeficientes.
convergencia = False  # Inicializa indicador de convergencia.
for iteracion in range(100):  # Ejecuta Newton-Raphson con máximo explícito.
    probabilidad = expit(X_asoc @ beta)  # Calcula probabilidades actuales.
    gradiente = X_asoc.T @ (w_asoc * (y_asoc - probabilidad))  # Calcula el vector de puntuación.
    informacion = X_asoc.T @ ((w_asoc * probabilidad * (1 - probabilidad))[:, None] * X_asoc)  # Calcula información observada.
    paso = np.linalg.pinv(informacion) @ gradiente  # Resuelve incluso ante condicionamiento moderado.
    beta_nuevo = beta + paso  # Actualiza coeficientes.
    if np.max(np.abs(paso)) < 1e-8:  # Comprueba convergencia estricta.
        beta = beta_nuevo  # Conserva la solución final.
        convergencia = True  # Marca convergencia.
        break  # Finaliza las iteraciones.
    beta = beta_nuevo  # Continúa desde el nuevo punto.
assert convergencia  # Exige convergencia antes de informar asociaciones.
probabilidad_asoc = expit(X_asoc @ beta)  # Calcula probabilidades finales.
informacion = X_asoc.T @ ((w_asoc * probabilidad_asoc * (1 - probabilidad_asoc))[:, None] * X_asoc)  # Recalcula la información final.
pan = np.linalg.pinv(informacion)  # Calcula el pan del estimador sándwich.
puntajes = (w_asoc * (y_asoc - probabilidad_asoc))[:, None] * X_asoc  # Calcula puntuación por persona del dominio.
puntajes_df = pd.DataFrame(puntajes, index=dominio.index, columns=matriz.columns)  # Alinea puntuaciones con identificadores.
puntajes_df['estrato'] = dominio['estrato']  # Añade estrato.
puntajes_df['upm'] = dominio['upm']  # Añade UPM.
totales_dominio = puntajes_df.groupby(['estrato', 'upm'], observed=True)[matriz.columns].sum()  # Agrega puntuaciones por UPM.
pares_completos = completa[['estrato', 'upm']].drop_duplicates().sort_values(['estrato', 'upm'])  # Enumera UPM de toda la muestra.
indice_completo = pd.MultiIndex.from_frame(pares_completos)  # Crea el índice completo.
totales_upm = totales_dominio.reindex(indice_completo, fill_value=0).to_numpy()  # Asigna cero a UPM sin casos del dominio.
estratos_upm = pares_completos['estrato'].to_numpy()  # Recupera estrato de cada UPM.
carne = np.zeros((X_asoc.shape[1], X_asoc.shape[1]))  # Inicializa la carne del sándwich.
for estrato in np.unique(estratos_upm):  # Recorre estratos completos.
    bloque = totales_upm[estratos_upm == estrato]  # Selecciona UPM del estrato.
    centrado = bloque - bloque.mean(axis=0, keepdims=True)  # Centra puntuaciones dentro del estrato.
    carne += len(bloque) / (len(bloque) - 1) * centrado.T @ centrado  # Aplica corrección por UPM muestreadas.
covarianza = pan @ carne @ pan  # Forma la covarianza robusta por diseño.
errores = np.sqrt(np.maximum(np.diag(covarianza), 0))  # Obtiene errores estándar.
grados_libertad = len(pares_completos) - completa['estrato'].nunique()  # Calcula UPM menos estratos.
t_critico = stats.t.ppf(0.975, df=grados_libertad)  # Obtiene el cuantil para IC de 95 %.
estadisticos = beta / errores  # Calcula estadísticos t.
valores_p = 2 * stats.t.sf(np.abs(estadisticos), df=grados_libertad)  # Calcula valores p bilaterales.
tabla_asociaciones = pd.DataFrame({'termino': matriz.columns, 'coeficiente_logit': beta, 'error_estandar': errores, 'estadistico_t': estadisticos, 'grados_libertad': grados_libertad, 'valor_p': valores_p, 'razon_momios': np.exp(beta), 'ic95_inferior': np.exp(beta - t_critico * errores), 'ic95_superior': np.exp(beta + t_critico * errores)})  # Construye tabla científica.
tabla_asociaciones.to_csv(SALIDAS / '09_asociaciones_ajustadas_or.csv', index=False, encoding='utf-8-sig')  # Exporta todas las asociaciones.
filas_wald = []  # Reserva pruebas conjuntas.
for variable, terminos in grupos_terminos.items():  # Recorre bloques de coeficientes.
    posiciones = [matriz.columns.get_loc(termino) for termino in terminos]  # Localiza posiciones del bloque.
    b = beta[posiciones]  # Extrae coeficientes del bloque.
    v = covarianza[np.ix_(posiciones, posiciones)]  # Extrae covarianza conjunta.
    rango = int(np.linalg.matrix_rank(v))  # Calcula grados efectivos.
    wald = float(b.T @ np.linalg.pinv(v) @ b)  # Calcula estadístico de Wald.
    filas_wald.append({'variable': variable, 'terminos': len(terminos), 'grados_libertad_prueba': rango, 'estadistico_wald': wald, 'valor_p': stats.chi2.sf(wald, df=rango)})  # Registra la prueba global.
tabla_wald = pd.DataFrame(filas_wald)  # Consolida pruebas globales.
tabla_wald.to_csv(SALIDAS / '10_pruebas_wald_ajustadas.csv', index=False, encoding='utf-8-sig')  # Exporta pruebas.

# BLOQUE 10: figuras científicas de desarrollo e interpretación.
figura, ejes = plt.subplots(1, 2, figsize=(11, 4.5))  # Crea el comparador de selección.
for nombre, color in [('logistica', AZUL), ('boosting', NARANJA)]:  # Recorre familias.
    datos = resumen_cv.loc[resumen_cv['modelo'] == nombre]  # Selecciona candidatos.
    ejes[0].errorbar(datos['candidato'], datos['roc_auc_media'], yerr=datos['roc_auc_de'], fmt='o', color=color, capsize=3, label=nombre.capitalize())  # Dibuja AUC media y dispersión.
    ejes[1].plot(datos['candidato'], datos['brier_medio'], 'o', color=color, label=nombre.capitalize())  # Dibuja Brier.
ejes[0].set_title('Selección interna: ROC-AUC', loc='left', fontweight='bold')  # Titula el primer panel.
ejes[0].set_ylabel('ROC-AUC ponderada media ± DE')  # Etiqueta la métrica.
ejes[1].set_title('Selección interna: Brier', loc='left', fontweight='bold')  # Titula el segundo panel.
ejes[1].set_ylabel('Brier ponderado medio (menor es mejor)')  # Etiqueta la métrica.
for eje in ejes:  # Recorre paneles.
    eje.tick_params(axis='x', rotation=30)  # Facilita lectura de candidatos.
    eje.grid(axis='y', color='#D1D5DB', linewidth=0.6)  # Añade guías discretas.
    eje.legend(frameon=False)  # Identifica familias.
figura.text(0.01, 0.005, 'Fuente: ENEMDU anual 2025. Cinco pliegues internos separados por UPM; ponderación fexp. La prueba reservada no interviene.', fontsize=7, color='#374151')  # Añade nota.
figura.tight_layout(rect=(0, 0.05, 1, 1))  # Reserva espacio inferior.
figura.savefig(FIGURAS / '01_seleccion_modelos.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '01_seleccion_modelos.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.
figura, eje = plt.subplots(figsize=(6.8, 5.6))  # Crea el gráfico de calibración.
for nombre, color, marcador in [('base', GRIS, 's'), ('logistica', AZUL, 'o'), ('boosting', NARANJA, '^')]:  # Recorre modelos.
    datos = tabla_calibracion.loc[tabla_calibracion['modelo'] == nombre]  # Selecciona deciles.
    eje.plot(100 * datos['prediccion_media'], 100 * datos['proporcion_observada'], marker=marcador, color=color, label=nombre.capitalize())  # Dibuja predicho frente a observado.
eje.plot([0, 100], [0, 100], '--', color='#111827', linewidth=1, label='Calibración ideal')  # Añade diagonal ideal.
eje.set(xlabel='Probabilidad predicha ponderada (%)', ylabel='Proporción observada ponderada (%)', xlim=(0, 100), ylim=(0, 100))  # Define escalas completas.
eje.set_title('Calibración interna fuera de pliegue', loc='left', fontweight='bold')  # Titula la figura.
eje.grid(color='#D1D5DB', linewidth=0.6)  # Añade cuadrícula.
eje.legend(frameon=False)  # Identifica curvas.
figura.text(0.01, 0.005, 'Diagnóstico de desarrollo en deciles de masa ponderada. No corresponde al resultado final en prueba.', fontsize=7, color='#374151')  # Aclara alcance.
figura.tight_layout(rect=(0, 0.05, 1, 1))  # Ajusta espacios.
figura.savefig(FIGURAS / '02_calibracion_oof.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '02_calibracion_oof.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.
figura, ejes = plt.subplots(1, 2, figsize=(11, 5.8), sharex=True)  # Crea paneles de importancia.
for eje, (nombre, color) in zip(ejes, [('logistica', AZUL), ('boosting', NARANJA)]):  # Recorre modelos.
    datos = resumen_importancias.loc[resumen_importancias['modelo'] == nombre].sort_values('caida_auc_media')  # Ordena variables.
    eje.barh(datos['variable'], datos['caida_auc_media'], xerr=datos['caida_auc_de'], color=color, alpha=0.85)  # Dibuja caída de AUC.
    eje.axvline(0, color='#111827', linewidth=0.8)  # Marca ausencia de importancia.
    eje.set_title(nombre.capitalize(), loc='left', fontweight='bold')  # Titula el panel.
    eje.set_xlabel('Caída de ROC-AUC al permutar')  # Explica la escala.
    eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Añade guías.
figura.suptitle('Importancia por permutación fuera de pliegue', x=0.01, ha='left', fontweight='bold')  # Titula la figura.
figura.text(0.01, 0.005, 'Media y DE de 25 estimaciones por variable (cinco repeticiones en cada uno de cinco pliegues). Importancia predictiva, no causal.', fontsize=7, color='#374151')  # Añade interpretación.
figura.tight_layout(rect=(0, 0.05, 1, 0.95))  # Ajusta espacios.
figura.savefig(FIGURAS / '03_importancia_permutacion.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '03_importancia_permutacion.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.
terminos_focales = ['p02[2]', 'area[2]', 'p10a[8]', 'p10a[10]', 'edad_decadas_c40', 'edad_decadas_c40_cuadrado']  # Define asociaciones principales para visualización.
datos_or = tabla_asociaciones.loc[tabla_asociaciones['termino'].isin(terminos_focales)].copy()  # Selecciona términos focales.
datos_or['etiqueta'] = datos_or['termino'].map({'p02[2]': 'Mujer vs. hombre', 'area[2]': 'Rural vs. urbana', 'p10a[8]': 'Superior no universitaria vs. universitaria', 'p10a[10]': 'Posgrado vs. universitaria', 'edad_decadas_c40': 'Edad: término lineal por década', 'edad_decadas_c40_cuadrado': 'Edad: término cuadrático'})  # Traduce términos.
datos_or = datos_or.iloc[::-1]  # Ordena para lectura superior.
figura, eje = plt.subplots(figsize=(8.5, 5.2))  # Crea el bosque de razones de momios.
posiciones = np.arange(len(datos_or))  # Define posiciones verticales.
errores_or = np.vstack([datos_or['razon_momios'] - datos_or['ic95_inferior'], datos_or['ic95_superior'] - datos_or['razon_momios']])  # Calcula longitudes asimétricas.
eje.errorbar(datos_or['razon_momios'], posiciones, xerr=errores_or, fmt='o', color=AZUL, ecolor=AZUL, capsize=3)  # Dibuja puntos e IC.
eje.axvline(1, color='#111827', linewidth=0.9)  # Marca la ausencia de asociación.
eje.set_yticks(posiciones, labels=datos_or['etiqueta'])  # Etiqueta comparaciones.
eje.set_xscale('log')  # Usa escala natural para razones.
eje.set_xlabel('Razón de momios ajustada e IC 95 % (escala logarítmica)')  # Define la métrica.
eje.set_title('Asociaciones ajustadas con empleo adecuado', loc='left', fontweight='bold')  # Titula la figura.
eje.grid(axis='x', color='#D1D5DB', linewidth=0.6, which='both')  # Añade guías.
figura.text(0.01, 0.005, 'Modelo ponderado; covarianza robusta por estrato y UPM del diseño completo. Asociación condicional, no efecto causal.', fontsize=7, color='#374151')  # Añade nota metodológica.
figura.tight_layout(rect=(0, 0.05, 1, 1))  # Ajusta espacios.
figura.savefig(FIGURAS / '04_asociaciones_ajustadas.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '04_asociaciones_ajustadas.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.

# BLOQUE 11: metadatos congelados, manifiesto y controles automáticos.
metadatos = {'estado': 'congelado_sin_evaluar_prueba', 'fecha_congelacion': CONFIG['fecha_congelacion'], 'sha256_entrenamiento': sha256(ENTRADA), 'filas_entrenamiento': len(entrenamiento), 'upm_entrenamiento': entrenamiento['upm'].nunique(), 'pliegues': CONFIG['pliegues'], 'predictores': PREDICTORES, 'seleccionados': {'logistica': {'candidato': seleccionados['logistica'], 'C': mejor_c}, 'boosting': {'candidato': seleccionados['boosting'], 'hiperparametros': mejor_boosting}}, 'umbrales_oof': umbrales, 'versiones': {'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__, 'scikit_learn': sklearn.__version__, 'joblib': joblib.__version__}, 'asociaciones': {'filas_dominio': len(dominio), 'filas_diseno_completo': len(completa), 'upm_diseno': len(pares_completos), 'estratos_diseno': completa['estrato'].nunique(), 'grados_libertad': grados_libertad, 'convergencia': convergencia, 'iteraciones': iteracion + 1}, 'prueba_reservada': {'ruta_declarada': CONFIG['archivo_prueba_reservada'], 'leida': False, 'evaluada': False}}  # Consolida todo lo necesario para la evaluación única posterior.
(MODELOS / 'metadatos_modelos_congelados.json').write_text(json.dumps(metadatos, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el contrato de evaluación.
productos = sorted(list(SALIDAS.glob('*.csv')) + list(FIGURAS.glob('*.*')) + list(MODELOS.glob('*')))  # Reúne productos sin incluir la prueba.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Calcula integridad de entregables.
manifiesto.to_csv(SALIDAS / '11_manifiesto_productos.csv', index=False, encoding='utf-8-sig')  # Exporta el manifiesto.
assert len(predicciones) == len(entrenamiento)  # Exige cobertura OOF completa.
assert predicciones.groupby('upm')['pliegue_cv'].nunique().max() == 1  # Reconfirma separación por UPM.
assert tabla_metricas['roc_auc'].between(0, 1).all()  # Exige AUC válidas.
assert tabla_metricas['brier'].between(0, 1).all()  # Exige Brier válidos.
assert np.isfinite(tabla_asociaciones[['coeficiente_logit', 'error_estandar', 'razon_momios']]).all().all()  # Exige asociaciones finitas.
resumen = {'estado': 'completado_y_congelado', 'modelo_logistico': seleccionados['logistica'], 'modelo_boosting': seleccionados['boosting'], 'roc_auc_oof_logistica': float(tabla_metricas.loc[tabla_metricas['modelo'] == 'logistica', 'roc_auc'].iloc[0]), 'roc_auc_oof_boosting': float(tabla_metricas.loc[tabla_metricas['modelo'] == 'boosting', 'roc_auc'].iloc[0]), 'diferencia_auc_boosting_menos_logistica': float(tabla_metricas.loc[tabla_metricas['modelo'] == 'boosting', 'roc_auc'].iloc[0] - tabla_metricas.loc[tabla_metricas['modelo'] == 'logistica', 'roc_auc'].iloc[0]), 'prueba_reservada_evaluada': False, 'asociaciones_ajustadas_estimadas': True, 'modelado_interpretable_preparado': True}  # Resume la etapa sin anticipar prueba.
(SALIDAS / '00_resumen_modelado.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el resumen.
print(json.dumps(resumen, ensure_ascii=False, indent=2))  # Presenta los resultados esenciales.
