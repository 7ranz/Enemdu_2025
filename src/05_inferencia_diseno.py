# ETAPA 6: inferencia para tasas y diferencias con el diseño complejo de ENEMDU.
# ARCHIVO: 05_inferencia_diseno.py; aplica linealización de Taylor y actualiza gráficos.
# BLOQUE 1: dependencias, rutas y decisiones.
import hashlib  # Calcula huellas de integridad.
import json  # Lee configuración y escribe resúmenes.
from pathlib import Path  # Maneja rutas portables.
import matplotlib  # Configura gráficos sin ventana.
matplotlib.use('Agg')  # Permite ejecución automática.
import matplotlib.pyplot as plt  # Genera figuras científicas.
import numpy as np  # Realiza álgebra y agregación numérica.
import pandas as pd  # Lee y exporta tablas.
from scipy import stats  # Obtiene cuantiles t y probabilidades de contraste.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
DATOS = RAIZ / 'data/processed'  # Localiza productos tratados.
ENTRADA = DATOS / 'inferencia/diseno_bivariado.csv.gz'  # Localiza la muestra completa de diseño.
SALIDAS = RAIZ / 'reports/eda06_inferencia'  # Define tablas de salida.
FIGURAS = RAIZ / 'reports/figures/eda06_inferencia'  # Define figuras de salida.
SALIDAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de tablas.
FIGURAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de figuras.
CONFIG = json.loads((RAIZ / 'config/inferencia_v1.json').read_text(encoding='utf-8'))  # Recupera decisiones preespecificadas.
TASAS_EDA05 = pd.read_csv(RAIZ / 'reports/eda05_bivariado/01_tasas_empleo_adecuado_grupos.csv', dtype={'codigo': 'string'})  # Recupera puntos y etiquetas auditados.
AZUL = '#0072B2'  # Usa azul accesible.
NARANJA = '#E69F00'  # Usa naranja accesible.
VERDE = '#009E73'  # Usa verde accesible.
ROJO = '#D55E00'  # Usa rojo accesible.
GRIS = '#6B7280'  # Usa gris para referencias.
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 12, 'axes.labelsize': 9})  # Fija estilo reproducible.

# BLOQUE 2: lectura de diseño y estructuras para UPM y estratos.
tipos = {'estrato': 'string', 'upm': 'string', 'fexp': 'float64', 'dominio_estudio': 'boolean', 'adecuado_descriptivo': 'Int8', 'p02': 'string', 'area': 'string', 'edad_limite_inferior': 'Int16', 'p10a': 'string', 'prov': 'string', 'grupo_edad': 'string', 'numerador_adecuado': 'Int8', 'denominador_dominio': 'Int8'}  # Define tipos explícitos.
base = pd.read_csv(ENTRADA, dtype=tipos, encoding='utf-8-sig')  # Lee las 334 786 filas sin filtrar dominios.
assert len(base) == 334786  # Exige la muestra completa.
assert base['fexp'].gt(0).all()  # Exige pesos positivos.
base['dominio'] = base['denominador_dominio'].eq(1)  # Recupera el indicador de dominio.
base['y'] = base['numerador_adecuado'].astype(float)  # Recupera el numerador binario ya validado.
pares = base[['estrato', 'upm']].drop_duplicates().sort_values(['estrato', 'upm']).reset_index(drop=True)  # Enumera las UPM del diseño.
mapa_upm = pd.Series(np.arange(len(pares)), index=pd.MultiIndex.from_frame(pares[['estrato', 'upm']]))  # Asigna un índice entero por UPM.
indice_filas = pd.MultiIndex.from_frame(base[['estrato', 'upm']])  # Construye claves UPM para cada fila.
codigo_upm = mapa_upm.loc[indice_filas].to_numpy(dtype=int)  # Traduce cada fila a su UPM.
codigos_estrato, niveles_estrato = pd.factorize(pares['estrato'], sort=True)  # Traduce el estrato de cada UPM.
n_upm_estrato = np.bincount(codigos_estrato)  # Cuenta UPM completas dentro de cada estrato.
assert len(pares) == 7780 and len(niveles_estrato) == 150  # Reconcilia diseño auditado.
assert n_upm_estrato.min() >= 2  # Exige al menos dos UPM por estrato en la muestra completa.
GL = len(pares) - len(niveles_estrato)  # Calcula grados de libertad del diseño.
ALFA = 1 - CONFIG['nivel_confianza']  # Calcula la cola total.
T_CRITICO = stats.t.ppf(1 - ALFA / 2, df=GL)  # Obtiene el cuantil t bilateral.

# BLOQUE 3: funciones de linealización y covarianza.
def sha256(ruta):  # Calcula la huella SHA-256 de un archivo.
    h = hashlib.sha256()  # Inicializa el algoritmo.
    with ruta.open('rb') as archivo:  # Abre bytes sin modificar.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee por bloques.
            h.update(bloque)  # Incorpora el contenido.
    return h.hexdigest()  # Devuelve la huella.

def varianza_desde_upm(totales_upm):  # Estima covarianza con UPM centradas dentro de estratos.
    matriz = np.asarray(totales_upm, dtype=float)  # Convierte a matriz numérica.
    matriz = matriz[:, None] if matriz.ndim == 1 else matriz  # Admite un estimador o varios.
    covarianza = np.zeros((matriz.shape[1], matriz.shape[1]), dtype=float)  # Inicializa la covarianza.
    for h in range(len(niveles_estrato)):  # Recorre los estratos completos.
        bloque = matriz[codigos_estrato == h]  # Selecciona todas sus UPM, incluso aportes cero.
        centrado = bloque - bloque.mean(axis=0, keepdims=True)  # Centra totales de UPM.
        covarianza += bloque.shape[0] / (bloque.shape[0] - 1) * centrado.T @ centrado  # Aplica la aproximación con reemplazo.
    return covarianza  # Devuelve varianzas y covarianzas.

def estimar_indicador(indicador):  # Estima una proporción de dominio y su influencia.
    indicador = np.asarray(indicador, dtype=bool)  # Normaliza la pertenencia al grupo.
    x = base['fexp'].to_numpy() * indicador  # Construye contribución al denominador.
    z = base['fexp'].to_numpy() * indicador * base['y'].to_numpy()  # Construye contribución al numerador.
    total_x = x.sum()  # Suma el denominador ponderado.
    total_z = z.sum()  # Suma el numerador ponderado.
    proporcion = total_z / total_x  # Calcula la razón de totales.
    linealizada = (z - proporcion * x) / total_x  # Calcula la influencia de cada fila.
    influencia_upm = np.bincount(codigo_upm, weights=linealizada, minlength=len(pares))  # Agrega influencias por UPM.
    varianza = varianza_desde_upm(influencia_upm)[0, 0]  # Obtiene la varianza de Taylor.
    error = np.sqrt(max(varianza, 0))  # Obtiene un error estándar no negativo.
    if 0 < proporcion < 1 and error > 0:  # Usa logit cuando la estimación está dentro del intervalo.
        error_logit = error / (proporcion * (1 - proporcion))  # Aplica delta para la escala logit.
        centro_logit = np.log(proporcion / (1 - proporcion))  # Transforma el punto.
        inferior = 1 / (1 + np.exp(-(centro_logit - T_CRITICO * error_logit)))  # Regresa el límite inferior.
        superior = 1 / (1 + np.exp(-(centro_logit + T_CRITICO * error_logit)))  # Regresa el límite superior.
    else:  # Define respaldo para estimaciones en límites.
        inferior = max(0, proporcion - T_CRITICO * error)  # Trunca el límite inferior lineal.
        superior = min(1, proporcion + T_CRITICO * error)  # Trunca el límite superior lineal.
    return {'proporcion': proporcion, 'varianza': varianza, 'error': error, 'inferior': inferior, 'superior': superior, 'influencia_upm': influencia_upm, 'total_peso': total_x, 'total_peso_adecuado': total_z, 'n': int(indicador.sum()), 'upm_casos': int(base.loc[indicador, 'upm'].nunique()), 'estratos_casos': int(base.loc[indicador, 'estrato'].nunique())}  # Devuelve resultados y soporte.

def ajuste_holm(valores):  # Ajusta una familia pequeña de valores p con Holm.
    valores = np.asarray(valores, dtype=float)  # Convierte valores a arreglo.
    orden = np.argsort(valores)  # Ordena de menor a mayor.
    ajustados_orden = np.maximum.accumulate((len(valores) - np.arange(len(valores))) * valores[orden])  # Impone monotonía secuencial.
    ajustados = np.empty_like(ajustados_orden)  # Reserva el orden original.
    ajustados[orden] = np.minimum(ajustados_orden, 1)  # Devuelve probabilidades válidas.
    return ajustados  # Retorna ajustes en el orden recibido.

# BLOQUE 4: estimaciones de tasa para total y categorías.
estimaciones = {}  # Conserva cada punto e influencia por clave.
filas_tasas = []  # Conserva filas para publicación.
variables = ['p02', 'area', 'grupo_edad', 'p10a', 'prov']  # Define dimensiones bivariadas.
total_resultado = estimar_indicador(base['dominio'].to_numpy())  # Estima la tasa total del dominio.
estimaciones[('total', 'total')] = total_resultado  # Guarda el total.
categorias = [('total', 'total', 'Total del dominio')]  # Inicializa el catálogo de resultados.
for variable in variables:  # Recorre dimensiones.
    fuente = TASAS_EDA05.loc[TASAS_EDA05['variable'] == variable, ['codigo', 'etiqueta']]  # Conserva códigos observados y etiquetas verificadas.
    categorias.extend([(variable, str(fila.codigo), fila.etiqueta) for fila in fuente.itertuples(index=False)])  # Añade categorías al catálogo.
for variable, codigo, etiqueta_grupo in categorias:  # Recorre total y categorías.
    indicador = base['dominio'].to_numpy() if variable == 'total' else (base['dominio'] & base[variable].eq(codigo)).to_numpy()  # Construye dominio o subgrupo sin filtrar filas.
    resultado = total_resultado if variable == 'total' else estimar_indicador(indicador)  # Estima o reutiliza total.
    estimaciones[(variable, codigo)] = resultado  # Guarda influencia para contrastes.
    cv = 100 * resultado['error'] / resultado['proporcion'] if resultado['proporcion'] != 0 else np.nan  # Calcula coeficiente de variación.
    filas_tasas.append({'variable': variable, 'codigo': codigo, 'etiqueta': etiqueta_grupo, 'n': resultado['n'], 'upm_con_casos': resultado['upm_casos'], 'estratos_con_casos': resultado['estratos_casos'], 'suma_pesos': resultado['total_peso'], 'porcentaje': 100 * resultado['proporcion'], 'error_estandar_pp': 100 * resultado['error'], 'ic95_inferior': 100 * resultado['inferior'], 'ic95_superior': 100 * resultado['superior'], 'cv_porcentaje': cv, 'grados_libertad': GL, 'metodo_ic': 'Taylor y logit', 'alerta_n_menor_100': resultado['n'] < 100})  # Registra la tabla científica.
tabla_tasas = pd.DataFrame(filas_tasas)  # Convierte resultados en tabla.
tabla_tasas.to_csv(SALIDAS / '01_tasas_con_ic95.csv', index=False, encoding='utf-8-sig')  # Exporta tasas e intervalos.

# BLOQUE 5: contrastes primarios con covarianza y ajuste de Holm.
filas_contrastes = []  # Inicializa contrastes preespecificados.
for contraste in CONFIG['contrastes_primarios']:  # Recorre los cuatro contrastes.
    clave_a = (contraste['variable'], contraste['a'])  # Define el primer grupo.
    clave_b = (contraste['variable'], contraste['b'])  # Define la referencia.
    resultado_a = estimaciones[clave_a]  # Recupera estimación e influencia A.
    resultado_b = estimaciones[clave_b]  # Recupera estimación e influencia B.
    diferencia = resultado_a['proporcion'] - resultado_b['proporcion']  # Calcula A menos B.
    influencia_diferencia = resultado_a['influencia_upm'] - resultado_b['influencia_upm']  # Conserva la covarianza compartida.
    varianza_diferencia = varianza_desde_upm(influencia_diferencia)[0, 0]  # Calcula varianza conjunta.
    error_diferencia = np.sqrt(max(varianza_diferencia, 0))  # Calcula error estándar.
    estadistico = diferencia / error_diferencia if error_diferencia > 0 else np.nan  # Calcula estadístico t.
    valor_p = 2 * stats.t.sf(abs(estadistico), df=GL) if np.isfinite(estadistico) else np.nan  # Calcula probabilidad bilateral.
    etiqueta_a = tabla_tasas.loc[(tabla_tasas['variable'] == clave_a[0]) & (tabla_tasas['codigo'] == clave_a[1]), 'etiqueta'].iloc[0]  # Recupera nombre A.
    etiqueta_b = tabla_tasas.loc[(tabla_tasas['variable'] == clave_b[0]) & (tabla_tasas['codigo'] == clave_b[1]), 'etiqueta'].iloc[0]  # Recupera nombre B.
    filas_contrastes.append({'contraste': contraste['id'], 'variable': contraste['variable'], 'grupo_a': etiqueta_a, 'grupo_b': etiqueta_b, 'tasa_a': 100 * resultado_a['proporcion'], 'tasa_b': 100 * resultado_b['proporcion'], 'diferencia_pp': 100 * diferencia, 'error_estandar_pp': 100 * error_diferencia, 'ic95_inferior': 100 * (diferencia - T_CRITICO * error_diferencia), 'ic95_superior': 100 * (diferencia + T_CRITICO * error_diferencia), 'estadistico_t': estadistico, 'grados_libertad': GL, 'valor_p': valor_p})  # Registra contraste.
tabla_contrastes = pd.DataFrame(filas_contrastes)  # Convierte contrastes en tabla.
tabla_contrastes['valor_p_holm'] = ajuste_holm(tabla_contrastes['valor_p'])  # Ajusta la familia primaria.
tabla_contrastes['significativo_holm_005'] = tabla_contrastes['valor_p_holm'] < 0.05  # Marca evidencia después del ajuste.
tabla_contrastes.to_csv(SALIDAS / '02_contrastes_primarios_ic95.csv', index=False, encoding='utf-8-sig')  # Exporta contrastes científicos.

# BLOQUE 6: pruebas globales de Wald por dimensión.
filas_globales = []  # Inicializa pruebas globales.
for variable in CONFIG['pruebas_globales']:  # Recorre cada dimensión.
    claves = [(variable, codigo) for codigo in tabla_tasas.loc[tabla_tasas['variable'] == variable, 'codigo']]  # Recupera categorías presentes.
    referencia = claves[0]  # Usa la primera categoría solo para construir un sistema de contrastes.
    diferencias = np.array([estimaciones[clave]['proporcion'] - estimaciones[referencia]['proporcion'] for clave in claves[1:]])  # Construye diferencias contra referencia.
    influencias = np.column_stack([estimaciones[clave]['influencia_upm'] - estimaciones[referencia]['influencia_upm'] for clave in claves[1:]])  # Construye influencias conjuntas.
    covarianza = varianza_desde_upm(influencias)  # Estima matriz de covarianza.
    rango = int(np.linalg.matrix_rank(covarianza))  # Determina grados de libertad efectivos.
    wald = float(diferencias.T @ np.linalg.pinv(covarianza) @ diferencias) if rango > 0 else np.nan  # Calcula estadístico global.
    valor_p = stats.chi2.sf(wald, df=rango) if rango > 0 else np.nan  # Calcula probabilidad chi-cuadrado.
    filas_globales.append({'variable': variable, 'categorias': len(claves), 'grados_libertad_prueba': rango, 'estadistico_wald': wald, 'valor_p': valor_p, 'evidencia_global_005': bool(valor_p < 0.05) if np.isfinite(valor_p) else False, 'referencia_computacional': tabla_tasas.loc[(tabla_tasas['variable'] == referencia[0]) & (tabla_tasas['codigo'] == referencia[1]), 'etiqueta'].iloc[0]})  # Registra la prueba.
tabla_globales = pd.DataFrame(filas_globales)  # Convierte pruebas en tabla.
tabla_globales.to_csv(SALIDAS / '03_pruebas_globales_wald.csv', index=False, encoding='utf-8-sig')  # Exporta pruebas globales.

# BLOQUE 7: gráficos con intervalos de confianza.
def grafico_intervalos(variable, titulo, nombre, color=AZUL, ordenar=False, alto=None):  # Dibuja estimaciones e IC de 95 %.
    datos = tabla_tasas.loc[tabla_tasas['variable'] == variable].copy()  # Selecciona una dimensión.
    datos = datos.sort_values('porcentaje') if ordenar else datos.iloc[::-1]  # Define el orden visual.
    altura = alto if alto else max(4.2, 0.4 * len(datos) + 1.8)  # Ajusta altura al contenido.
    figura, eje = plt.subplots(figsize=(8.8, altura))  # Crea el lienzo.
    posiciones = np.arange(len(datos))  # Define posiciones verticales.
    errores = np.vstack([datos['porcentaje'] - datos['ic95_inferior'], datos['ic95_superior'] - datos['porcentaje']])  # Calcula distancias asimétricas.
    eje.errorbar(datos['porcentaje'], posiciones, xerr=errores, fmt='o', color=color, ecolor=color, capsize=3, markersize=5, linewidth=1.2)  # Dibuja puntos e intervalos.
    eje.axvline(100 * total_resultado['proporcion'], color=GRIS, linestyle='--', linewidth=1, label=f'Total: {100 * total_resultado["proporcion"]:.1f}%')  # Añade referencia global.
    eje.set_yticks(posiciones, labels=datos['etiqueta'])  # Etiqueta categorías.
    eje.set_xlim(0, 100)  # Usa escala completa de porcentaje.
    eje.set_xlabel('Empleo adecuado ponderado (%) e IC 95 %')  # Declara unidad e incertidumbre.
    eje.set_title(titulo, loc='left', fontweight='bold')  # Titula la figura.
    eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Añade guías discretas.
    eje.set_axisbelow(True)  # Coloca guías detrás.
    eje.legend(frameon=False, loc='lower right')  # Identifica el total.
    nota = 'Fuente: ENEMDU anual 2025. Taylor: estrato, UPM y fexp; IC 95 % logit, sin FPC. PEA de 15+ con nivel superior y título.'  # Define la nota metodológica.
    figura.text(0.01, 0.005, nota, ha='left', va='bottom', fontsize=7, color='#374151')  # Añade fuente y método.
    figura.tight_layout(rect=(0, 0.045, 1, 1))  # Reserva espacio para la nota.
    figura.savefig(FIGURAS / f'{nombre}.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
    figura.savefig(FIGURAS / f'{nombre}.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
    plt.close(figura)  # Libera memoria.

grafico_intervalos('p02', 'Empleo adecuado por sexo', '01_ic_sexo', AZUL)  # Actualiza sexo.
grafico_intervalos('area', 'Empleo adecuado por área', '02_ic_area', VERDE)  # Actualiza área.
grafico_intervalos('grupo_edad', 'Empleo adecuado por edad', '03_ic_edad', NARANJA, alto=7.2)  # Actualiza edad.
grafico_intervalos('p10a', 'Empleo adecuado por nivel educativo reportado', '04_ic_educacion', ROJO)  # Actualiza educación.
grafico_intervalos('prov', 'Empleo adecuado por provincia', '05_ic_provincia', AZUL, ordenar=True, alto=9.4)  # Actualiza territorio.
figura, eje = plt.subplots(figsize=(8.8, 4.8))  # Crea el gráfico de contrastes.
orden_contrastes = tabla_contrastes.iloc[::-1].copy()  # Ordena para lectura superior a inferior.
posiciones = np.arange(len(orden_contrastes))  # Define posiciones.
errores = np.vstack([orden_contrastes['diferencia_pp'] - orden_contrastes['ic95_inferior'], orden_contrastes['ic95_superior'] - orden_contrastes['diferencia_pp']])  # Calcula errores asimétricos.
colores = [VERDE if valor >= 0 else ROJO for valor in orden_contrastes['diferencia_pp']]  # Distingue signos.
for posicion, (_, fila), color in zip(posiciones, orden_contrastes.iterrows(), colores):  # Recorre contrastes.
    eje.errorbar(fila['diferencia_pp'], posicion, xerr=[[fila['diferencia_pp'] - fila['ic95_inferior']], [fila['ic95_superior'] - fila['diferencia_pp']]], fmt='o', color=color, ecolor=color, capsize=4)  # Dibuja el contraste y su IC.
eje.axvline(0, color='#111827', linewidth=0.9)  # Marca la hipótesis nula.
eje.set_yticks(posiciones, labels=[f'{fila.grupo_a} − {fila.grupo_b}' for fila in orden_contrastes.itertuples()])  # Explicita el orden de resta.
eje.set_xlabel('Diferencia en empleo adecuado (puntos porcentuales) e IC 95 %')  # Define la métrica.
eje.set_title('Contrastes primarios con diseño muestral', loc='left', fontweight='bold')  # Titula la figura.
eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Añade guías.
eje.set_axisbelow(True)  # Coloca guías detrás.
figura.text(0.01, 0.005, 'Fuente: ENEMDU anual 2025. IC 95 % de Taylor; valores p ajustados por Holm en la tabla científica.', ha='left', va='bottom', fontsize=7, color='#374151')  # Añade nota.
figura.tight_layout(rect=(0, 0.06, 1, 1))  # Ajusta el contenido.
figura.savefig(FIGURAS / '06_ic_contrastes_primarios.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '06_ic_contrastes_primarios.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG.
plt.close(figura)  # Libera memoria.

# BLOQUE 8: resumen, manifiesto y controles finales.
def valor_contraste(nombre, columna):  # Recupera un resultado por identificador.
    return float(tabla_contrastes.loc[tabla_contrastes['contraste'] == nombre, columna].iloc[0])  # Devuelve un escalar JSON-compatible.

resumen = {'estado': 'completado', 'metodo': CONFIG['metodo_varianza'], 'grados_libertad': GL, 't_critico_95': T_CRITICO, 'tasa_total': 100 * total_resultado['proporcion'], 'ic95_total': [100 * total_resultado['inferior'], 100 * total_resultado['superior']], 'brecha_mujeres_hombres_pp': valor_contraste('mujeres_menos_hombres', 'diferencia_pp'), 'ic95_mujeres_hombres': [valor_contraste('mujeres_menos_hombres', 'ic95_inferior'), valor_contraste('mujeres_menos_hombres', 'ic95_superior')], 'p_holm_mujeres_hombres': valor_contraste('mujeres_menos_hombres', 'valor_p_holm'), 'brecha_rural_urbana_pp': valor_contraste('rural_menos_urbana', 'diferencia_pp'), 'ic95_rural_urbana': [valor_contraste('rural_menos_urbana', 'ic95_inferior'), valor_contraste('rural_menos_urbana', 'ic95_superior')], 'p_holm_rural_urbana': valor_contraste('rural_menos_urbana', 'valor_p_holm'), 'prueba_predictiva_evaluada': False}  # Resume resultados centrales.
(SALIDAS / '00_resumen_inferencia.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el resumen estructurado.
productos = sorted(list(SALIDAS.glob('0*.csv')) + list(FIGURAS.glob('*.*')))  # Reúne tablas y figuras.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Calcula trazabilidad.
manifiesto.to_csv(SALIDAS / '04_manifiesto_productos.csv', index=False, encoding='utf-8-sig')  # Exporta el manifiesto.
assert GL == CONFIG['grados_libertad']  # Verifica grados de libertad preespecificados.
assert tabla_tasas[['ic95_inferior', 'porcentaje', 'ic95_superior']].apply(lambda fila: fila.iloc[0] <= fila.iloc[1] <= fila.iloc[2], axis=1).all()  # Verifica orden de intervalos.
assert tabla_tasas['ic95_inferior'].ge(0).all() and tabla_tasas['ic95_superior'].le(100).all()  # Verifica límites de proporciones.
assert np.allclose(tabla_contrastes['diferencia_pp'], tabla_contrastes['tasa_a'] - tabla_contrastes['tasa_b'])  # Verifica diferencias.
verificacion = {'estado': 'verificado', 'filas_muestra_completa': len(base), 'upm': len(pares), 'estratos': len(niveles_estrato), 'grados_libertad': GL, 'estimaciones_con_ic': len(tabla_tasas), 'contrastes_primarios': len(tabla_contrastes), 'pruebas_globales': len(tabla_globales), 'intervalos_proporcion_en_rango': True, 'diferencias_reconciliadas': True, 'figuras_png': len(list(FIGURAS.glob('*.png'))), 'figuras_svg': len(list(FIGURAS.glob('*.svg'))), 'prueba_predictiva_evaluada': False}  # Consolida controles.
(SALIDAS / '05_verificacion_inferencia.json').write_text(json.dumps(verificacion, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda evidencia automática.
print(json.dumps(resumen, ensure_ascii=False, indent=2))  # Presenta el resultado.
