# ETAPA 2 DEL EDA: validar códigos contra las etiquetas del archivo SPSS oficial de 2025.
# ARCHIVO: 01c_validar_etiquetas_oficiales.py. Complementa el diccionario Excel, que no enumera todos los valores.
# BLOQUE 1: herramientas, rutas y lector especializado de metadatos.
import hashlib  # Calcula huellas de los originales consultados.
import json  # Conserva etiquetas y procedencia de forma editable.
import sys  # Permite usar una dependencia local si no está instalada en el entorno.
from pathlib import Path  # Construye rutas portables.
from zipfile import ZipFile  # Abre los contenedores oficiales en modo lectura.
import pandas as pd  # Cuenta valores por variable y mes.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la carpeta del proyecto.
try:  # Prefiere una instalación normal de pyreadstat.
    import pyreadstat  # Lee metadatos y etiquetas de archivos SAV.
except ImportError:  # Contempla la dependencia aislada utilizada en esta ejecución.
    sys.path.insert(0, str(RAIZ / '.runtime'))  # Añade únicamente la carpeta local de bibliotecas del proyecto.
    import pyreadstat  # Importa el lector desde esa carpeta si está disponible.

SALIDA = RAIZ / 'reports/calidad'  # Define dónde guardar evidencia agregada.
SALIDA.mkdir(parents=True, exist_ok=True)  # Prepara la carpeta de salidas.
SPSS = RAIZ / 'data/raw/1_BDD_ENEMDU_2025_SPSS.zip'  # Señala el contenedor oficial con etiquetas.
CSV = RAIZ / 'data/raw/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip'  # Señala los datos que realmente analizamos.
TEMPORAL = RAIZ / '.build_eda'  # Separa copias de lectura de los datos originales.
TEMPORAL.mkdir(parents=True, exist_ok=True)  # Prepara la carpeta auxiliar.

# BLOQUE 2: leer etiquetas y comprobar integridad del contenedor.
with ZipFile(SPSS) as archivo:  # Abre el ZIP de SPSS sin modificarlo.
    if archivo.testzip() is not None:  # Valida todos los miembros antes de leer metadatos.
        raise ValueError('ZIP SPSS con problemas de integridad')  # Evita usar etiquetas de una descarga dañada.
    ruta_sav = TEMPORAL / 'personas_oficial_2025.sav'  # Define una copia temporal con nombre controlado.
    ruta_sav.write_bytes(archivo.read('BDDenemdu_personas_2025_anual.sav'))  # Copia el miembro observado sin extraer rutas arbitrarias.
_, metadata = pyreadstat.read_sav(str(ruta_sav), metadataonly=True)  # Lee únicamente el esquema y las etiquetas.
etiquetas = metadata.variable_value_labels  # Recupera las categorías publicadas por el INEC.
catalogo = {'fuente': 'https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/1_BDD_ENEMDU_2025_SPSS.zip', 'sha256': hashlib.sha256(SPSS.read_bytes()).hexdigest(), 'archivo': 'BDDenemdu_personas_2025_anual.sav', 'columnas': metadata.column_names, 'etiquetas_variables': metadata.column_names_to_labels, 'etiquetas_valores': etiquetas, 'rangos_missing': metadata.missing_ranges, 'pyreadstat_version': pyreadstat.__version__}  # Documenta procedencia y versión.
(SALIDA / '14_catalogo_spss_oficial.json').write_text(json.dumps(catalogo, ensure_ascii=False, indent=2), encoding='utf-8')  # Conserva un catálogo completo y auditable.

# BLOQUE 3: contrastar dominios categóricos; no aplicar etiquetas especiales como rangos de ingresos.
categoricas = ['area', 'p02', 'p04', 'p05a', 'p05b', 'p06', 'p07', 'p08', 'p09', 'p10a', 'p11', 'p12a', 'p15', 'p15aa', 'p20', 'p21', 'p22', 'p23', 'p25', 'p26', 'p27', 'p28', 'p30', 'p31', 'p32', 'p34', 'p35', 'p36', 'p37', 'p38', 'p42', 'p42a', 'p43', 'p46', 'p47a', 'p48', 'p49', 'p54', 'p54a', 'p55', 'p56a', 'p57', 'p58', 'p61b1', 'p64a', 'p68a', 'p70a', 'p71a', 'p72a', 'p73a', 'p74a', 'p75', 'p77', 'sd01', 'sd03', 'ced01a', 'nnivins', 'condact', 'empleo', 'desempleo', 'secemp', 'grupo1', 'rama1', 'prov', 'dominio', 'pobreza', 'epobreza']  # Define preguntas y clasificaciones nominales, no cantidades.
categoricas += [f'p44{letra}' for letra in 'abcdefghijk'] + [f'sd02{i}' for i in range(1, 12)]  # Añade preguntas binarias de prestaciones y desempleo.
with ZipFile(CSV) as archivo:  # Abre el archivo que sustenta todos los análisis del proyecto.
    datos = pd.read_csv(archivo.open('BDDenemdu_personas_2025_anual.csv'), sep=';', encoding='utf-8-sig', dtype=str, keep_default_na=False)  # Conserva códigos como texto.
datos = datos.apply(lambda columna: columna.str.strip())  # Reconoce vacíos guardados como espacios, solo en memoria.
controles = []  # Almacena resultados mensuales y anuales de los códigos.
sin_catalogo = []  # Registra campos para los que no puede certificar un dominio completo.
for campo in categoricas:  # Revisa cada campo categórico predefinido.
    if campo not in datos or campo not in etiquetas or not etiquetas[campo]:  # Evita inferir categorías ausentes del catálogo.
        sin_catalogo.append(campo)  # Deja visible la falta de etiquetas.
        continue  # Pasa al siguiente campo sin afirmar validación.
    valores = pd.to_numeric(datos[campo].replace('', float('nan')), errors='coerce')  # Convierte códigos numéricos de la copia.
    informados = datos[campo].ne('')  # Excluye vacíos del contraste de códigos.
    fuera = informados & ~valores.isin(etiquetas[campo].keys())  # Detecta valores no enumerados en las etiquetas oficiales.
    for mes in ['ANUAL'] + sorted(datos['mes'].unique().tolist()):  # Localiza resultados también por mes.
        mascara = pd.Series(True, index=datos.index) if mes == 'ANUAL' else datos['mes'].eq(mes)  # Define el corte temporal.
        controles.append({'variable': campo, 'mes': mes, 'n_informados': int((informados & mascara).sum()), 'n_no_etiquetados': int((fuera & mascara).sum()), 'codigos_no_etiquetados': '|'.join(sorted(datos.loc[fuera & mascara, campo].unique()))})  # Conserva los códigos que requieren revisión, no registros individuales.
pd.DataFrame(controles).to_csv(SALIDA / '15_validacion_codigos_spss.csv', index=False, encoding='utf-8-sig')  # Guarda la validación de categorías.

# BLOQUE 4: precisar las divergencias territoriales observadas en UPM.
prefijo = datos['upm'].str[:6]  # Recupera la parte geográfica del identificador UPM.
ciudad = datos['ciudad'].str.zfill(6)  # Normaliza a seis dígitos la columna de ciudad para comparar.
geografia = datos.loc[prefijo.ne(ciudad), ['ciudad', 'prov', 'mes']].copy()  # Selecciona divergencias para revisión, sin corregirlas.
geografia['prefijo_upm'] = prefijo.loc[geografia.index]  # Añade el prefijo observado en la UPM.
geografia.groupby(['ciudad', 'prov', 'prefijo_upm', 'mes']).size().rename('n').reset_index().to_csv(SALIDA / '16_revision_geografia_upm.csv', index=False, encoding='utf-8-sig')  # Exporta únicamente conteos por códigos geográficos.
resumen = {'variables_categoricas_validadas': len(set(r['variable'] for r in controles)), 'sin_catalogo': sin_catalogo, 'alertas_anuales': [r for r in controles if r['mes']=='ANUAL' and r['n_no_etiquetados']>0], 'columnas_sav_no_csv': sorted(set(metadata.column_names)-set(datos.columns)), 'columnas_csv_no_sav': sorted(set(datos.columns)-set(metadata.column_names)), 'ingrl_etiquetas': etiquetas.get('ingrl'), 'edad_etiquetas': etiquetas.get('p03'), 'filas_prefijo_upm_distinto_ciudad': int(prefijo.ne(ciudad).sum()), 'filas_prefijo_upm_distinto_conglomerado': int(prefijo.ne(datos['conglomerado']).sum()), 'filas_provincia_prefijo_upm_distinta_prov': int(pd.to_numeric(prefijo.str[:2]).ne(pd.to_numeric(datos['prov'])).sum()), 'limite': 'Un código no etiquetado es una señal de revisión; no se elimina automáticamente. Las categorías no prueban todos los saltos del cuestionario.'}  # Resume alcance, semántica e identificadores.
(SALIDA / '17_resumen_etiquetas.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el resumen verificable.
print(json.dumps(resumen, ensure_ascii=False, indent=2))  # Presenta únicamente resultados agregados.
