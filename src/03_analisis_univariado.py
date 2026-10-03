# ETAPA 4 DEL EDA: distribuciones, frecuencias, faltantes y gráficos científicos.
# ARCHIVO: 03_analisis_univariado.py; genera resultados reproducibles sin leer la prueba reservada.
# BLOQUE 1: dependencias, rutas y configuración visual.
import hashlib  # Calcula huellas para verificar los productos.
import json  # Lee decisiones y escribe resúmenes estructurados.
from pathlib import Path  # Construye rutas portables.
import matplotlib  # Configura un motor gráfico que no requiere ventana.
matplotlib.use('Agg')  # Permite crear figuras en ejecución automática.
import matplotlib.pyplot as plt  # Dibuja y exporta las figuras.
import numpy as np  # Realiza cálculos numéricos y ponderados.
import pandas as pd  # Lee, resume y exporta tablas.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la carpeta principal del proyecto.
DATOS = RAIZ / 'data/processed'  # Localiza las bases tratadas.
SALIDAS = RAIZ / 'reports/eda04_univariado'  # Define la carpeta de tablas y controles.
FIGURAS = RAIZ / 'reports/figures/eda04_univariado'  # Define la carpeta de figuras.
SALIDAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de resultados si falta.
FIGURAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de gráficos si falta.
CONFIG = json.loads((RAIZ / 'config/eda04_univariado_v1.json').read_text(encoding='utf-8'))  # Recupera decisiones predefinidas.
ETIQUETAS = json.loads((DATOS / 'etiquetas_oficiales.json').read_text(encoding='utf-8'))  # Recupera categorías oficiales.
AZUL = '#0072B2'  # Usa azul distinguible en una paleta apta para daltonismo.
NARANJA = '#E69F00'  # Usa naranja distinguible para una segunda serie.
VERDE = '#009E73'  # Usa verde distinguible para una tercera serie.
GRIS = '#6B7280'  # Usa gris neutro para referencias.
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 12, 'axes.labelsize': 9})  # Fija un estilo legible y reproducible.

# BLOQUE 2: funciones estadísticas y documentales reutilizables.
def sha256(ruta):  # Calcula la huella de un archivo terminado.
    h = hashlib.sha256()  # Inicializa el algoritmo SHA-256.
    with ruta.open('rb') as archivo:  # Abre el archivo sin modificarlo.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee por bloques para limitar memoria.
            h.update(bloque)  # Incorpora cada bloque a la huella.
    return h.hexdigest()  # Devuelve la huella hexadecimal.

def limpiar_codigo(valor):  # Normaliza códigos para buscar sus etiquetas oficiales.
    texto = str(valor).strip()  # Convierte el valor a texto sin espacios.
    return texto[:-2] if texto.endswith('.0') else texto  # Retira únicamente el decimal artificial .0.

def etiqueta(variable, valor):  # Traduce un código utilizando el catálogo oficial.
    codigo = limpiar_codigo(valor)  # Normaliza el código observado.
    catalogo = ETIQUETAS.get(variable, {})  # Obtiene el catálogo de la variable.
    opciones = [codigo, f'{codigo}.0']  # Considera ambas formas presentes en los metadatos.
    hallada = next((catalogo[opcion] for opcion in opciones if opcion in catalogo), codigo)  # Selecciona etiqueta o conserva código.
    return str(hallada).strip()  # Devuelve una etiqueta sin espacios exteriores.

def cuantiles_ponderados(valores, pesos, probabilidades):  # Calcula cuantiles descriptivos con pesos de encuesta.
    validos = valores.notna() & pesos.notna() & (pesos > 0)  # Conserva pares válidos y pesos positivos.
    x = valores.loc[validos].astype(float).to_numpy()  # Convierte los valores válidos a arreglo.
    w = pesos.loc[validos].astype(float).to_numpy()  # Convierte los pesos correspondientes a arreglo.
    orden = np.argsort(x, kind='mergesort')  # Ordena establemente por valor.
    x = x[orden]  # Aplica el orden a los valores.
    w = w[orden]  # Aplica el mismo orden a los pesos.
    posiciones = (np.cumsum(w) - 0.5 * w) / w.sum()  # Sitúa cada observación en la distribución ponderada.
    return np.interp(probabilidades, posiciones, x, left=x[0], right=x[-1])  # Interpola los cuantiles solicitados.

def frecuencia(tabla, variable):  # Resume una variable categórica con y sin ponderación.
    temporal = tabla[[variable, 'fexp']].copy()  # Selecciona categoría y peso.
    temporal[variable] = temporal[variable].astype('string').fillna('FALTANTE')  # Hace visible la ausencia.
    agrupada = temporal.groupby(variable, dropna=False, observed=True).agg(n=(variable, 'size'), suma_pesos=('fexp', 'sum')).reset_index()  # Agrupa observaciones y pesos.
    agrupada['porcentaje'] = 100 * agrupada['n'] / agrupada['n'].sum()  # Calcula porcentaje muestral.
    agrupada['porcentaje_ponderado'] = 100 * agrupada['suma_pesos'] / agrupada['suma_pesos'].sum()  # Calcula composición ponderada.
    agrupada.insert(0, 'variable', variable)  # Identifica la variable en la tabla apilada.
    agrupada = agrupada.rename(columns={variable: 'codigo'})  # Homogeneiza el nombre de categoría.
    agrupada['etiqueta'] = agrupada['codigo'].map(lambda x: 'Faltante' if x == 'FALTANTE' else etiqueta(variable, x))  # Añade etiquetas comprensibles.
    return agrupada[['variable', 'codigo', 'etiqueta', 'n', 'porcentaje', 'suma_pesos', 'porcentaje_ponderado']]  # Devuelve columnas documentadas.

def faltantes(tabla, variables):  # Resume ausencia para cada campo seleccionado.
    filas = []  # Inicializa una fila por variable.
    total_peso = tabla['fexp'].sum()  # Calcula el denominador ponderado común.
    for variable in variables:  # Recorre las variables preespecificadas.
        mascara = tabla[variable].isna()  # Identifica valores ausentes reales.
        filas.append({'variable': variable, 'n_total': len(tabla), 'n_faltante': int(mascara.sum()), 'porcentaje_faltante': 100 * mascara.mean(), 'suma_pesos_total': total_peso, 'suma_pesos_faltante': tabla.loc[mascara, 'fexp'].sum(), 'porcentaje_ponderado_faltante': 100 * tabla.loc[mascara, 'fexp'].sum() / total_peso})  # Registra conteos y proporciones.
    return pd.DataFrame(filas)  # Convierte la lista en tabla.

def guardar_figura(figura, nombre):  # Exporta cada gráfico en formatos de uso y edición.
    figura.savefig(FIGURAS / f'{nombre}.png', dpi=200, bbox_inches='tight', facecolor='white')  # Guarda PNG nítido.
    figura.savefig(FIGURAS / f'{nombre}.svg', bbox_inches='tight', facecolor='white')  # Guarda SVG editable.
    plt.close(figura)  # Libera memoria gráfica.

def nota_fuente(figura, texto):  # Añade fuente y alcance debajo del gráfico.
    figura.text(0.01, 0.005, texto, ha='left', va='bottom', fontsize=7, color='#374151')  # Escribe una nota uniforme.

def barras_horizontales(tabla, titulo, nombre, max_categorias=None):  # Crea barras ponderadas legibles.
    datos = tabla.sort_values('porcentaje_ponderado', ascending=True).copy()  # Ordena para lectura visual.
    datos = datos.tail(max_categorias) if max_categorias else datos  # Limita categorías solo cuando se solicita.
    alto = max(4.2, 0.32 * len(datos) + 1.6)  # Ajusta la altura al número de categorías.
    figura, eje = plt.subplots(figsize=(8.2, alto))  # Crea un lienzo proporcional.
    eje.barh(datos['etiqueta'], datos['porcentaje_ponderado'], color=AZUL)  # Representa porcentajes ponderados.
    eje.set_xlim(left=0)  # Evita truncar el eje de las barras.
    eje.set_xlabel('Porcentaje ponderado (%)')  # Define la unidad del eje.
    eje.set_title(titulo, loc='left', fontweight='bold')  # Añade un título descriptivo.
    eje.grid(axis='x', color='#D1D5DB', linewidth=0.6, alpha=0.8)  # Facilita comparar longitudes.
    eje.set_axisbelow(True)  # Coloca la cuadrícula detrás de las barras.
    for parche, valor in zip(eje.patches, datos['porcentaje_ponderado']):  # Recorre barras y valores.
        eje.text(valor + 0.2, parche.get_y() + parche.get_height() / 2, f'{valor:.1f}', va='center', fontsize=8)  # Etiqueta cada barra.
    nota_fuente(figura, 'Fuente: ENEMDU anual 2025, dominio de educación superior completada (n=39 551). Ponderación: fexp. Descriptivo; IC pendientes de la etapa inferencial.')  # Declara fuente y límite.
    figura.tight_layout(rect=(0, 0.04, 1, 1))  # Reserva espacio para la nota.
    guardar_figura(figura, nombre)  # Exporta ambos formatos.

# BLOQUE 3: carga controlada; la prueba reservada no aparece en ninguna ruta.
columnas_dominio = ['edad_limite_inferior', 'edad_98_mas', 'p02', 'p06', 'p07', 'p10a', 'p15', 'prov', 'area', 'mes', 'fexp']  # Define las columnas descriptivas necesarias.
dominio = pd.read_csv(DATOS / 'dominio_educacion_superior.csv', usecols=columnas_dominio, encoding='utf-8-sig', dtype={c: 'string' for c in columnas_dominio if c != 'fexp'})  # Lee covariables del dominio completo.
dominio['fexp'] = pd.to_numeric(dominio['fexp'], errors='raise')  # Convierte el ponderador con validación estricta.
dominio['edad_limite_inferior'] = pd.to_numeric(dominio['edad_limite_inferior'], errors='coerce')  # Convierte edad y conserva ausencias.
columnas_modelo = ['y_adecuado', 'fexp']  # Define los únicos campos requeridos de entrenamiento.
entrenamiento = pd.read_csv(DATOS / 'modelado/entrenamiento.csv', usecols=columnas_modelo, encoding='utf-8-sig', dtype={'y_adecuado': 'Int8', 'fexp': 'float64'})  # Lee el resultado solo en entrenamiento.
ingresos = pd.read_csv(DATOS / 'ocupados_ingresos.csv', usecols=['estado_ingreso_laboral', 'ingreso_laboral_monto', 'ingreso_monto_observado', 'fexp'], encoding='utf-8-sig', dtype={'estado_ingreso_laboral': 'string', 'ingreso_monto_observado': 'boolean', 'fexp': 'float64'})  # Lee el producto secundario de ocupados.
ingresos['ingreso_laboral_monto'] = pd.to_numeric(ingresos['ingreso_laboral_monto'], errors='coerce')  # Convierte únicamente el monto analítico.
assert len(dominio) == 39551  # Confirma el dominio previsto.
assert len(entrenamiento) == 31502  # Confirma que se cargó entrenamiento.
assert 'prueba' not in ' '.join(str(x) for x in [DATOS / 'dominio_educacion_superior.csv', DATOS / 'modelado/entrenamiento.csv', DATOS / 'ocupados_ingresos.csv'])  # Documenta que ninguna ruta es la prueba reservada.

# BLOQUE 4: tablas univariadas de covariables, edad y faltantes.
variables = CONFIG['variables_numericas'] + CONFIG['variables_categoricas']  # Une campos numéricos y categóricos.
tabla_faltantes = faltantes(dominio, variables + ['fexp'])  # Calcula ausencia en el dominio completo.
tabla_faltantes.to_csv(SALIDAS / '01_faltantes_covariables_dominio.csv', index=False, encoding='utf-8-sig')  # Exporta faltantes editables.
frecuencias = pd.concat([frecuencia(dominio, variable) for variable in CONFIG['variables_categoricas']], ignore_index=True)  # Apila frecuencias de categorías.
frecuencias.to_csv(SALIDAS / '02_frecuencias_categoricas_dominio.csv', index=False, encoding='utf-8-sig')  # Exporta frecuencias editables.
probabilidades = np.array(CONFIG['cuantiles'], dtype=float)  # Convierte cuantiles configurados a arreglo.
edad_valida = dominio['edad_limite_inferior'].notna()  # Identifica edades utilizables.
edad_cuantiles = cuantiles_ponderados(dominio['edad_limite_inferior'], dominio['fexp'], probabilidades)  # Calcula cuantiles ponderados de edad.
resumen_edad = pd.DataFrame({'medida': ['n_valido', 'n_faltante', 'media', 'desviacion_estandar'] + [f'cuantil_{p:.2f}' for p in probabilidades], 'sin_ponderar': [int(edad_valida.sum()), int((~edad_valida).sum()), dominio.loc[edad_valida, 'edad_limite_inferior'].mean(), dominio.loc[edad_valida, 'edad_limite_inferior'].std(ddof=1)] + dominio.loc[edad_valida, 'edad_limite_inferior'].quantile(probabilidades).tolist(), 'ponderado': [dominio.loc[edad_valida, 'fexp'].sum(), dominio.loc[~edad_valida, 'fexp'].sum(), np.average(dominio.loc[edad_valida, 'edad_limite_inferior'], weights=dominio.loc[edad_valida, 'fexp']), np.sqrt(np.average((dominio.loc[edad_valida, 'edad_limite_inferior'] - np.average(dominio.loc[edad_valida, 'edad_limite_inferior'], weights=dominio.loc[edad_valida, 'fexp'])) ** 2, weights=dominio.loc[edad_valida, 'fexp']))] + edad_cuantiles.tolist()})  # Reúne medidas comparables.
resumen_edad.to_csv(SALIDAS / '03_resumen_edad_dominio.csv', index=False, encoding='utf-8-sig')  # Exporta el resumen de edad.
intervalos_edad = np.array(CONFIG['intervalos_edad'], dtype=float)  # Recupera cortes predefinidos.
etiquetas_edad = [f'{int(a)}–{int(b - 1)}' for a, b in zip(intervalos_edad[:-2], intervalos_edad[1:-1])] + ['98+']  # Construye etiquetas y respeta la categoría abierta.
dominio['grupo_edad'] = pd.cut(dominio['edad_limite_inferior'], bins=intervalos_edad, labels=etiquetas_edad, right=False, include_lowest=True)  # Clasifica la edad sin convertir 98+ en edad exacta.
hist_edad = dominio.groupby('grupo_edad', observed=False).agg(n=('edad_limite_inferior', 'size'), suma_pesos=('fexp', 'sum')).reset_index()  # Resume cada intervalo.
hist_edad['porcentaje'] = 100 * hist_edad['n'] / hist_edad['n'].sum()  # Calcula porcentaje sin ponderar.
hist_edad['porcentaje_ponderado'] = 100 * hist_edad['suma_pesos'] / hist_edad['suma_pesos'].sum()  # Calcula porcentaje ponderado.
hist_edad.to_csv(SALIDAS / '04_distribucion_edad_dominio.csv', index=False, encoding='utf-8-sig')  # Exporta datos del gráfico.

# BLOQUE 5: resultado de entrenamiento e ingresos secundarios.
objetivo = frecuencia(entrenamiento, 'y_adecuado')  # Resume la etiqueta sin consultar prueba.
objetivo['etiqueta'] = objetivo['codigo'].map({'0': 'No adecuado', '1': 'Adecuado'}).fillna(objetivo['etiqueta'])  # Traduce el resultado binario.
objetivo.to_csv(SALIDAS / '05_frecuencia_objetivo_entrenamiento.csv', index=False, encoding='utf-8-sig')  # Exporta el diagnóstico de entrenamiento.
estado_ingresos = frecuencia(ingresos, 'estado_ingreso_laboral')  # Resume estados de observación del ingreso.
estado_ingresos.to_csv(SALIDAS / '06_estado_ingresos_ocupados.csv', index=False, encoding='utf-8-sig')  # Exporta las clases de ausencia y códigos especiales.
montos = ingresos.loc[ingresos['ingreso_monto_observado'] & ingresos['ingreso_laboral_monto'].notna()].copy()  # Conserva montos utilizables, incluido cero.
ingreso_cuantiles = cuantiles_ponderados(montos['ingreso_laboral_monto'], montos['fexp'], probabilidades)  # Calcula cuantiles ponderados de ingreso.
media_ingreso = np.average(montos['ingreso_laboral_monto'], weights=montos['fexp'])  # Calcula media ponderada de ingreso.
resumen_ingreso = pd.DataFrame({'medida': ['n_observado', 'media'] + [f'cuantil_{p:.2f}' for p in probabilidades], 'sin_ponderar': [len(montos), montos['ingreso_laboral_monto'].mean()] + montos['ingreso_laboral_monto'].quantile(probabilidades).tolist(), 'ponderado': [montos['fexp'].sum(), media_ingreso] + ingreso_cuantiles.tolist()})  # Reúne medidas de ingreso.
resumen_ingreso.to_csv(SALIDAS / '07_resumen_ingresos_observados.csv', index=False, encoding='utf-8-sig')  # Exporta el resumen de ingresos.
intervalos_ingreso = np.array(CONFIG['intervalos_ingreso'], dtype=float)  # Recupera tramos monetarios.
etiquetas_ingreso = ['0', '1–99', '100–199', '200–399', '400–599', '600–999', '1 000–1 999', '2 000–4 999', '5 000–9 999', '10 000+']  # Define rótulos claros en dólares.
montos['tramo_ingreso'] = pd.cut(montos['ingreso_laboral_monto'], bins=intervalos_ingreso, labels=etiquetas_ingreso, right=False, include_lowest=True)  # Clasifica montos sin recortarlos.
hist_ingreso = montos.groupby('tramo_ingreso', observed=False).agg(n=('ingreso_laboral_monto', 'size'), suma_pesos=('fexp', 'sum')).reset_index()  # Resume los tramos.
hist_ingreso['porcentaje'] = 100 * hist_ingreso['n'] / hist_ingreso['n'].sum()  # Calcula porcentaje muestral.
hist_ingreso['porcentaje_ponderado'] = 100 * hist_ingreso['suma_pesos'] / hist_ingreso['suma_pesos'].sum()  # Calcula porcentaje ponderado.
hist_ingreso.to_csv(SALIDAS / '08_distribucion_ingresos_observados.csv', index=False, encoding='utf-8-sig')  # Exporta datos del gráfico.

# BLOQUE 6: seis figuras científicas en PNG y SVG.
figura, eje = plt.subplots(figsize=(9, 5))  # Crea el gráfico de edad.
eje.bar(hist_edad['grupo_edad'].astype(str), hist_edad['porcentaje_ponderado'], color=AZUL)  # Dibuja porcentajes ponderados por edad.
eje.set(xlabel='Edad (años; 98+ es categoría abierta)', ylabel='Porcentaje ponderado (%)')  # Define unidades y límite conceptual.
eje.set_title('Distribución por edad', loc='left', fontweight='bold')  # Titula la figura.
eje.tick_params(axis='x', rotation=45)  # Evita superposición de rótulos.
eje.grid(axis='y', color='#D1D5DB', linewidth=0.6)  # Añade guías discretas.
eje.set_axisbelow(True)  # Coloca guías detrás de las barras.
nota_fuente(figura, 'Fuente: ENEMDU anual 2025, dominio de educación superior completada (n=39 551). Ponderación: fexp. Descriptivo; sin IC en esta etapa.')  # Declara fuente.
figura.tight_layout(rect=(0, 0.06, 1, 1))  # Ajusta elementos y nota.
guardar_figura(figura, '01_distribucion_edad')  # Exporta edad.
barras_horizontales(frecuencias.loc[frecuencias['variable'] == 'p10a'], 'Nivel de instrucción reportado', '02_nivel_instruccion')  # Grafica nivel educativo.
barras_horizontales(frecuencias.loc[frecuencias['variable'] == 'p15'], 'Autoidentificación étnica', '03_autoidentificacion_etnica')  # Grafica autoidentificación.
sexo = frecuencias.loc[frecuencias['variable'] == 'p02'].sort_values('codigo')  # Selecciona sexo.
area = frecuencias.loc[frecuencias['variable'] == 'area'].sort_values('codigo')  # Selecciona área.
figura, ejes = plt.subplots(1, 2, figsize=(9, 4.5))  # Crea paneles comparables.
for eje, datos, titulo, color in zip(ejes, [sexo, area], ['Sexo', 'Área de residencia'], [AZUL, VERDE]):  # Recorre ambos paneles.
    eje.bar(datos['etiqueta'], datos['porcentaje_ponderado'], color=color)  # Dibuja la composición ponderada.
    eje.set_ylim(0, max(70, datos['porcentaje_ponderado'].max() * 1.18))  # Mantiene el origen y espacio para etiquetas.
    eje.set_ylabel('Porcentaje ponderado (%)')  # Declara la unidad.
    eje.set_title(titulo, loc='left', fontweight='bold')  # Titula cada panel.
    eje.grid(axis='y', color='#D1D5DB', linewidth=0.6)  # Facilita comparación.
    eje.set_axisbelow(True)  # Coloca guías detrás.
    for parche, valor in zip(eje.patches, datos['porcentaje_ponderado']):  # Recorre barras.
        eje.text(parche.get_x() + parche.get_width() / 2, valor + 1, f'{valor:.1f}', ha='center', fontsize=8)  # Etiqueta porcentajes.
nota_fuente(figura, 'Fuente: ENEMDU anual 2025, dominio de educación superior completada (n=39 551). Ponderación: fexp. Descriptivo; sin IC en esta etapa.')  # Declara fuente.
figura.tight_layout(rect=(0, 0.06, 1, 1))  # Ajusta paneles.
guardar_figura(figura, '04_composicion_sexo_area')  # Exporta panel conjunto.
figura, eje = plt.subplots(figsize=(9, 5))  # Crea el gráfico de ingresos.
eje.bar(hist_ingreso['tramo_ingreso'].astype(str), hist_ingreso['porcentaje_ponderado'], color=NARANJA)  # Dibuja tramos sin ocultar extremos.
eje.set(xlabel='Ingreso laboral mensual observado (USD)', ylabel='Porcentaje ponderado (%)')  # Define unidades.
eje.set_title('Distribución de ingresos laborales observados', loc='left', fontweight='bold')  # Titula la figura.
eje.tick_params(axis='x', rotation=40)  # Hace legibles los tramos.
eje.grid(axis='y', color='#D1D5DB', linewidth=0.6)  # Añade referencias.
eje.set_axisbelow(True)  # Coloca referencias detrás.
nota_fuente(figura, 'Fuente: ENEMDU anual 2025. Ocupados del dominio con monto utilizable (n=35 080); incluye ceros. Ponderación: fexp. Sin imputación ni recorte.')  # Define el denominador.
figura.tight_layout(rect=(0, 0.07, 1, 1))  # Ajusta rótulos y nota.
guardar_figura(figura, '05_distribucion_ingresos')  # Exporta ingresos.
figura, eje = plt.subplots(figsize=(8, 4.6))  # Crea el gráfico de faltantes.
orden_faltantes = tabla_faltantes.sort_values('porcentaje_ponderado_faltante')  # Ordena los campos.
colores = [NARANJA if valor > 0 else GRIS for valor in orden_faltantes['porcentaje_ponderado_faltante']]  # Destaca faltantes positivos.
eje.barh(orden_faltantes['variable'], orden_faltantes['porcentaje_ponderado_faltante'], color=colores)  # Dibuja porcentajes de ausencia.
eje.set(xlabel='Porcentaje ponderado faltante (%)', ylabel='Variable')  # Define ejes.
eje.set_title('Valores faltantes en covariables', loc='left', fontweight='bold')  # Titula el control.
eje.set_xlim(left=0)  # Mantiene el origen real.
eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Añade guía.
eje.set_axisbelow(True)  # Coloca guía detrás.
nota_fuente(figura, 'Fuente: ENEMDU anual 2025, dominio de educación superior completada (n=39 551). Los códigos especiales de ingreso se informan por separado.')  # Aclara el alcance.
figura.tight_layout(rect=(0, 0.06, 1, 1))  # Ajusta elementos.
guardar_figura(figura, '06_faltantes_covariables')  # Exporta faltantes.

# BLOQUE 7: resumen, manifiesto y controles automáticos.
resumen = {'estado': 'completado', 'filas_dominio': len(dominio), 'filas_entrenamiento_objetivo': len(entrenamiento), 'filas_ocupados': len(ingresos), 'ingresos_observados': len(montos), 'variables_categoricas': CONFIG['variables_categoricas'], 'variables_numericas': CONFIG['variables_numericas'], 'maximo_faltante_covariables_porcentaje': float(tabla_faltantes['porcentaje_faltante'].max()), 'edad_media_ponderada': float(resumen_edad.loc[resumen_edad['medida'] == 'media', 'ponderado'].iloc[0]), 'edad_mediana_ponderada': float(resumen_edad.loc[resumen_edad['medida'] == 'cuantil_0.50', 'ponderado'].iloc[0]), 'ingreso_mediano_ponderado_observado': float(resumen_ingreso.loc[resumen_ingreso['medida'] == 'cuantil_0.50', 'ponderado'].iloc[0]), 'prueba_reservada_leida': False, 'nota_inferencia': 'Los porcentajes son descriptivos ponderados; intervalos de confianza y contrastes con diseño se calcularán en una etapa posterior.'}  # Reúne resultados centrales sin evaluar prueba.
(SALIDAS / '00_resumen_eda04.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el resumen estructurado.
productos = sorted(list(SALIDAS.glob('0*.csv')) + list(FIGURAS.glob('*.*')))  # Reúne tablas y figuras finales.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Calcula trazabilidad de cada producto.
manifiesto.to_csv(SALIDAS / '09_manifiesto_productos.csv', index=False, encoding='utf-8-sig')  # Exporta el manifiesto.
assert tabla_faltantes['n_total'].eq(len(dominio)).all()  # Comprueba denominadores de faltantes.
assert np.isclose(frecuencias.groupby('variable')['porcentaje_ponderado'].sum(), 100).all()  # Comprueba totales ponderados categóricos.
assert np.isclose(objetivo['porcentaje_ponderado'].sum(), 100)  # Comprueba el diagnóstico del objetivo.
assert (montos['ingreso_laboral_monto'] >= 0).all()  # Comprueba que los montos sean no negativos.
verificacion = {'estado': 'verificado', 'prueba_reservada_leida': False, 'tablas_csv': len(list(SALIDAS.glob('0*.csv'))), 'figuras_png': len(list(FIGURAS.glob('*.png'))), 'figuras_svg': len(list(FIGURAS.glob('*.svg'))), 'porcentajes_categoricos_suman_100': True, 'ingresos_no_negativos': True, 'manifiesto_sha256': sha256(SALIDAS / '09_manifiesto_productos.csv')}  # Consolida controles de cierre.
(SALIDAS / '10_verificacion_eda04.json').write_text(json.dumps(verificacion, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda evidencia de verificación.
print(json.dumps(resumen, ensure_ascii=False, indent=2))  # Presenta el resultado al ejecutar el programa.
