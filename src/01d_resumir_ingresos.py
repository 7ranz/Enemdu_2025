# ETAPA 2 DEL EDA: interpretar ausencias y códigos de ingreso antes de preparar la base.
# ARCHIVO: 01d_resumir_ingresos.py. Genera un cruce de calidad, no estimaciones de ingreso poblacional.
# BLOQUE 1: herramientas y origen inalterado.
from pathlib import Path  # Construye rutas portables.
from zipfile import ZipFile  # Abre el contenedor oficial sin modificarlo.
import pandas as pd  # Resume categorías y conteos.

RAIZ = Path(__file__).resolve().parents[1]  # Ubica el proyecto.
with ZipFile(RAIZ / 'data/raw/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip') as archivo:  # Abre la fuente de personas.
    datos = pd.read_csv(archivo.open('BDDenemdu_personas_2025_anual.csv'), sep=';', encoding='utf-8-sig', dtype=str, keep_default_na=False, usecols=['p03', 'p10a', 'p12a', 'ingrl', 'condact'])  # Lee solo variables necesarias.
datos = datos.apply(lambda columna: columna.str.strip())  # Reconoce los espacios como vacíos en la copia de trabajo.

# BLOQUE 2: población ocupada candidata y estados del ingreso, manteniendo cada significado.
edad = pd.to_numeric(datos['p03'], errors='coerce')  # Interpreta edad sin sustituir valores desconocidos.
elegible = edad.between(15, 98) & datos['p10a'].isin(['8', '9', '10']) & datos['p12a'].eq('1') & datos['condact'].isin(['1', '2', '3', '4', '5', '6'])  # Selecciona ocupados del dominio educativo.
datos = datos.loc[elegible].copy()  # Crea una vista independiente de la población secundaria.
ingreso = pd.to_numeric(datos['ingrl'].str.replace(',', '.', regex=False), errors='coerce')  # Interpreta el ingreso en una columna auxiliar.
datos['estado_ingreso'] = 'valor_no_negativo'  # Inicia la clasificación para cantidades ordinarias.
datos.loc[datos['ingrl'].eq(''), 'estado_ingreso'] = 'vacio'  # Mantiene ausencia física como categoría separada.
datos.loc[ingreso.eq(-1), 'estado_ingreso'] = 'gasta_mas_de_lo_que_gana'  # Usa la etiqueta oficial de -1.
datos.loc[ingreso.eq(999999), 'estado_ingreso'] = 'no_informa'  # Usa la etiqueta oficial de no respuesta.
datos.loc[ingreso.lt(0) & ingreso.ne(-1), 'estado_ingreso'] = 'otro_negativo_revisar'  # Expone otros negativos si existieran.
datos.loc[ingreso.isna() & datos['ingrl'].ne(''), 'estado_ingreso'] = 'no_numerico_revisar'  # Separa texto inválido de vacío.

# BLOQUE 3: reporte agregado y verificación de conciliación.
cruce = pd.crosstab(datos['condact'], datos['estado_ingreso'])  # Cruza clase laboral y disponibilidad de ingreso.
assert int(cruce.to_numpy().sum()) == len(datos)  # Comprueba que ningún registro se perdió al clasificar.
cruce.reset_index().to_csv(RAIZ / 'reports/calidad/18_ingresos_por_condicion.csv', index=False, encoding='utf-8-sig')  # Guarda evidencia editable sin personas identificables.
print(cruce.to_string())  # Muestra el resumen de calidad.
