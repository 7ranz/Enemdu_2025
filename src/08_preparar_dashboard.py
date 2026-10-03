# ETAPA 9: preparación segura y ligera de datos para el dashboard.
# ARCHIVO: 08_preparar_dashboard.py; elimina identificadores y reúne productos científicos congelados.
# BLOQUE 1: dependencias y rutas.
import hashlib  # Calcula huellas de integridad.
import json  # Lee configuración y escribe metadatos.
from pathlib import Path  # Maneja rutas portables.
import pandas as pd  # Lee y exporta datos analíticos.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto.
FUENTE = RAIZ / 'data/processed/personas_tratada_completa.csv.gz'  # Localiza la base tratada.
SALIDA = RAIZ / 'data/dashboard'  # Define la carpeta de datos del tablero.
REPORTES = RAIZ / 'reports/dashboard'  # Define controles del tablero.
SALIDA.mkdir(parents=True, exist_ok=True)  # Crea la carpeta analítica.
REPORTES.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de controles.

# BLOQUE 2: lectura mínima y selección del universo.
columnas = ['estrato', 'upm', 'fexp', 'dominio_estudio', 'p02', 'area', 'edad_limite_inferior', 'edad_98_mas', 'p10a', 'prov', 'mes', 'adecuado_descriptivo', 'subempleo_descriptivo', 'desempleo_descriptivo', 'dominio_ingresos', 'ingreso_laboral_monto', 'ingreso_monto_observado', 'sexo_etiqueta', 'nivel_reportado_etiqueta', 'provincia_etiqueta', 'area_etiqueta']  # Limita campos a visualización y diseño.
tipos = {columna: 'string' for columna in ['estrato', 'upm', 'dominio_estudio', 'p02', 'area', 'p10a', 'prov', 'mes', 'dominio_ingresos']}  # Conserva códigos exactos.
base = pd.read_csv(FUENTE, usecols=columnas, dtype=tipos, encoding='utf-8-sig')  # Lee únicamente columnas necesarias.
pares = base[['estrato', 'upm']].drop_duplicates().sort_values(['estrato', 'upm']).reset_index(drop=True)  # Conserva todas las UPM del diseño.
dominio = base.loc[base['dominio_estudio'].str.lower().eq('true')].copy()  # Selecciona el universo del observatorio.
for columna in ['p02', 'area', 'p10a', 'prov']:  # Recorre códigos categóricos.
    dominio[columna] = dominio[columna].str.replace(r'\.0$', '', regex=True)  # Elimina decimales artificiales.
dominio['mes'] = dominio['mes'].str.replace(r'\.0$', '', regex=True).str.zfill(2)  # Normaliza el mes.
for columna in ['fexp', 'edad_limite_inferior', 'edad_98_mas', 'adecuado_descriptivo', 'subempleo_descriptivo', 'desempleo_descriptivo', 'ingreso_laboral_monto']:  # Recorre campos numéricos.
    dominio[columna] = pd.to_numeric(dominio[columna], errors='coerce')  # Convierte a número preservando faltantes.

# BLOQUE 3: etiquetas limpias y controles de privacidad.
mapa_sexo = {'1': 'Hombre', '2': 'Mujer'}  # Define etiquetas oficiales limpias.
mapa_area = {'1': 'Urbana', '2': 'Rural'}  # Define etiquetas de área.
mapa_educacion = {'8': 'Superior no universitaria', '9': 'Superior universitaria', '10': 'Posgrado'}  # Define niveles reportados.
mapa_provincia = {'1': 'Azuay', '2': 'Bolívar', '3': 'Cañar', '4': 'Carchi', '5': 'Cotopaxi', '6': 'Chimborazo', '7': 'El Oro', '8': 'Esmeraldas', '9': 'Guayas', '10': 'Imbabura', '11': 'Loja', '12': 'Los Ríos', '13': 'Manabí', '14': 'Morona Santiago', '15': 'Napo', '16': 'Pastaza', '17': 'Pichincha', '18': 'Tungurahua', '19': 'Zamora Chinchipe', '20': 'Galápagos', '21': 'Sucumbíos', '22': 'Orellana', '23': 'Santo Domingo de los Tsáchilas', '24': 'Santa Elena'}  # Define provincias observadas.
mapa_mes = {'01': 'Enero', '02': 'Febrero', '03': 'Marzo', '04': 'Abril', '05': 'Mayo', '06': 'Junio', '07': 'Julio', '08': 'Agosto', '09': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'}  # Define meses.
dominio['sexo'] = dominio['p02'].map(mapa_sexo)  # Añade sexo legible.
dominio['area_residencia'] = dominio['area'].map(mapa_area)  # Añade área legible.
dominio['nivel_educativo'] = dominio['p10a'].map(mapa_educacion)  # Añade educación legible.
dominio['provincia'] = dominio['prov'].map(mapa_provincia)  # Añade provincia legible.
dominio['nombre_mes'] = dominio['mes'].map(mapa_mes)  # Añade mes legible.
dominio = dominio.drop(columns=['dominio_estudio', 'sexo_etiqueta', 'nivel_reportado_etiqueta', 'provincia_etiqueta', 'area_etiqueta'])  # Elimina campos redundantes.
prohibidos = {'id_persona', 'id_hogar', 'id_vivienda', 'id_hogar_sin_mes', 'id_vivienda_sin_mes', 'clave_posicion_sin_mes'}  # Enumera identificadores prohibidos.
assert prohibidos.isdisjoint(dominio.columns)  # Exige ausencia de identificadores personales y domésticos.
assert len(dominio) == 39551  # Exige el universo documentado.
assert len(pares) == 7780  # Exige todas las UPM del diseño.

# BLOQUE 4: exportación columnar y catálogo de etiquetas.
dominio.to_parquet(SALIDA / 'observatorio_enemdu_2025.parquet', index=False, compression='zstd')  # Guarda microdatos analíticos sin identificadores.
pares.to_parquet(SALIDA / 'diseno_upm.parquet', index=False, compression='zstd')  # Guarda el esqueleto completo del diseño.
etiquetas = {'sexo': mapa_sexo, 'area': mapa_area, 'educacion': mapa_educacion, 'provincia': mapa_provincia, 'mes': mapa_mes}  # Consolida catálogos.
(SALIDA / 'etiquetas_dashboard.json').write_text(json.dumps(etiquetas, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda etiquetas.

# BLOQUE 5: integridad, diccionario y resumen.
def sha256(ruta):  # Calcula una huella SHA-256.
    objeto = hashlib.sha256()  # Inicializa el algoritmo.
    with ruta.open('rb') as archivo:  # Abre el archivo en bytes.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee por bloques.
            objeto.update(bloque)  # Incorpora cada bloque.
    return objeto.hexdigest()  # Devuelve la huella.

diccionario = pd.DataFrame([{'variable': 'estrato', 'descripcion': 'Estrato del diseño anual', 'rol': 'diseño'}, {'variable': 'upm', 'descripcion': 'Unidad primaria de muestreo, no identifica personas', 'rol': 'diseño'}, {'variable': 'fexp', 'descripcion': 'Factor de expansión anual', 'rol': 'peso'}, {'variable': 'edad_limite_inferior', 'descripcion': 'Edad; 98 representa 98 años o más', 'rol': 'filtro'}, {'variable': 'adecuado_descriptivo', 'descripcion': '1 si condact=1 dentro del dominio', 'rol': 'indicador'}, {'variable': 'subempleo_descriptivo', 'descripcion': '1 si condact=2 o 3 dentro del dominio', 'rol': 'indicador'}, {'variable': 'desempleo_descriptivo', 'descripcion': '1 si condact=7 u 8 dentro del dominio', 'rol': 'indicador'}, {'variable': 'ingreso_laboral_monto', 'descripcion': 'Ingreso laboral utilizable entre ocupados; sin imputación', 'rol': 'resultado secundario'}, {'variable': 'ingreso_monto_observado', 'descripcion': 'Bandera de disponibilidad del monto dentro del dominio de ingresos', 'rol': 'control'}])  # Documenta campos centrales.
diccionario.to_csv(REPORTES / '01_diccionario_dashboard.csv', index=False, encoding='utf-8-sig')  # Exporta el diccionario.
productos = [SALIDA / 'observatorio_enemdu_2025.parquet', SALIDA / 'diseno_upm.parquet', SALIDA / 'etiquetas_dashboard.json']  # Enumera productos.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'filas': len(dominio) if 'observatorio' in ruta.name else (len(pares) if 'diseno_upm' in ruta.name else None), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Registra tamaño e integridad.
manifiesto.to_csv(REPORTES / '02_manifiesto_datos_dashboard.csv', index=False, encoding='utf-8-sig')  # Exporta el manifiesto.
resumen = {'estado': 'completado', 'filas_observatorio': len(dominio), 'upm_diseno': len(pares), 'estratos_diseno': pares['estrato'].nunique(), 'columnas_observatorio': len(dominio.columns), 'identificadores_personales': 0, 'ingresos_observados': int(dominio['ingreso_monto_observado'].fillna(False).astype(bool).sum())}  # Consolida el resultado.
(REPORTES / '00_resumen_preparacion_dashboard.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el resumen.
print(json.dumps(resumen, ensure_ascii=False, indent=2))  # Presenta el resultado.
