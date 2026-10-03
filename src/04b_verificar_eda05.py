# ETAPA 5 DEL EDA: verificar tablas, diseño, figuras y cuaderno bivariado.
# ARCHIVO: 04b_verificar_eda05.py; produce evidencia independiente de cierre.
# BLOQUE 1: dependencias y rutas.
import ast  # Comprueba sintaxis Python.
import hashlib  # Recalcula huellas.
import json  # Lee y escribe controles.
from pathlib import Path  # Maneja rutas portables.
import nbformat  # Inspecciona el cuaderno.
import numpy as np  # Compara resultados con tolerancia.
import pandas as pd  # Lee productos tabulares.
from PIL import Image  # Revisa dimensiones de PNG.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
REPORTES = RAIZ / 'reports/eda05_bivariado'  # Localiza tablas.
FIGURAS = RAIZ / 'reports/figures/eda05_bivariado'  # Localiza figuras.
DISENO = RAIZ / 'data/processed/inferencia/diseno_bivariado.csv.gz'  # Localiza la muestra para inferencia.
CUADERNO = RAIZ / 'notebooks/05_analisis_bivariado.ipynb'  # Localiza el cuaderno ejecutado.

# BLOQUE 2: función de integridad y manifiesto.
def sha256(ruta):  # Calcula SHA-256 sin modificar el archivo.
    h = hashlib.sha256()  # Inicializa el algoritmo.
    with ruta.open('rb') as archivo:  # Abre bytes en modo lectura.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee bloques pequeños.
            h.update(bloque)  # Incorpora cada bloque.
    return h.hexdigest()  # Devuelve la huella.

manifiesto = pd.read_csv(REPORTES / '05_manifiesto_productos.csv')  # Lee el inventario.
for fila in manifiesto.itertuples(index=False):  # Recorre cada producto registrado.
    ruta = RAIZ / fila.archivo  # Reconstruye la ruta.
    assert ruta.exists()  # Exige que exista.
    assert ruta.stat().st_size == fila.bytes  # Exige el tamaño registrado.
    assert sha256(ruta) == fila.sha256  # Exige contenido idéntico.

# BLOQUE 3: recálculo independiente desde el archivo de diseño.
columnas = ['dominio_estudio', 'adecuado_descriptivo', 'fexp', 'p02', 'area', 'estrato', 'upm']  # Selecciona campos para control.
base = pd.read_csv(DISENO, usecols=columnas, dtype={'dominio_estudio': 'boolean', 'adecuado_descriptivo': 'Int8', 'fexp': 'float64', 'p02': 'string', 'area': 'string', 'estrato': 'string', 'upm': 'string'}, encoding='utf-8-sig')  # Lee el producto preparado.
dominio = base.loc[base['dominio_estudio']].copy()  # Recupera el dominio solo para contrastar puntos.
tasas = pd.read_csv(REPORTES / '01_tasas_empleo_adecuado_grupos.csv', dtype={'codigo': 'string'})  # Lee resultados publicados.
def tasa(tabla):  # Recalcula una proporción ponderada.
    return 100 * (tabla['fexp'] * tabla['adecuado_descriptivo']).sum() / tabla['fexp'].sum()  # Divide total ponderado adecuado para total ponderado.

assert len(base) == 334786  # Exige todas las filas originales.
assert len(dominio) == 39551  # Reconcilia el dominio.
assert base['estrato'].nunique() == 150 and base['upm'].nunique() == 7780  # Reconcilia el diseño.
for variable in ['p02', 'area']:  # Recalcula comparaciones principales.
    for codigo, grupo in dominio.groupby(variable, observed=True):  # Recorre sus categorías.
        publicado = tasas.loc[(tasas['variable'] == variable) & (tasas['codigo'] == str(codigo)), 'porcentaje_ponderado'].iloc[0]  # Recupera el resultado exportado.
        assert np.isclose(tasa(grupo), publicado, rtol=0, atol=1e-10)  # Exige igualdad numérica.
assert tasas['porcentaje_ponderado'].between(0, 100).all()  # Exige tasas válidas.
assert tasas.loc[tasas['variable'] == 'total', 'n'].iloc[0] == len(dominio)  # Exige denominador total.

# BLOQUE 4: figuras, programas y cuaderno.
nombres = ['01_empleo_adecuado_sexo', '02_empleo_adecuado_area', '03_empleo_adecuado_edad', '04_empleo_adecuado_educacion', '05_empleo_adecuado_provincia', '06_brechas_sexo_area']  # Enumera figuras esperadas.
for nombre in nombres:  # Recorre cada figura.
    png = FIGURAS / f'{nombre}.png'  # Localiza PNG.
    svg = FIGURAS / f'{nombre}.svg'  # Localiza SVG.
    assert png.exists() and svg.exists()  # Exige ambos formatos.
    with Image.open(png) as imagen:  # Abre la figura rasterizada.
        assert imagen.width >= 1200 and imagen.height >= 700  # Exige resolución suficiente.
    assert '<svg' in svg.read_text(encoding='utf-8')  # Exige formato vectorial real.
programas = sorted(RAIZ.glob('src/04*.py'))  # Reúne programas de la etapa.
for programa in programas:  # Recorre programas.
    contenido = programa.read_text(encoding='utf-8-sig')  # Lee el código.
    ast.parse(contenido)  # Exige sintaxis válida.
    assert '# ETAPA 5' in contenido and '# ARCHIVO:' in contenido and '# BLOQUE' in contenido  # Exige comentarios estructurales.
cuaderno = nbformat.read(CUADERNO, as_version=4)  # Lee el cuaderno.
celdas_codigo = [celda for celda in cuaderno.cells if celda.cell_type == 'code']  # Selecciona código.
assert all(celda.execution_count is not None for celda in celdas_codigo)  # Exige ejecución completa.
assert not any(salida.output_type == 'error' for celda in celdas_codigo for salida in celda.outputs)  # Exige cero errores.
assert all(all((not linea.strip()) or linea.lstrip().startswith('#') or '#' in linea for linea in celda.source.splitlines()) for celda in celdas_codigo)  # Exige comentarios por línea ejecutable.
assert 'prueba_reservada.csv' not in (RAIZ / 'src/04_analisis_bivariado.py').read_text(encoding='utf-8-sig')  # Confirma que no se abre el archivo predictivo.

# BLOQUE 5: acta final.
resultado = {'estado': 'verificado', 'productos_manifestados': len(manifiesto), 'filas_diseno': len(base), 'filas_dominio': len(dominio), 'estratos': base['estrato'].nunique(), 'upm': base['upm'].nunique(), 'grados_libertad_diseno': base['upm'].nunique() - base['estrato'].nunique(), 'tasas_principales_recalculadas': True, 'figuras_png': len(list(FIGURAS.glob('*.png'))), 'figuras_svg': len(list(FIGURAS.glob('*.svg'))), 'celdas_cuaderno': len(cuaderno.cells), 'celdas_codigo_ejecutadas': len(celdas_codigo), 'errores_cuaderno': 0, 'intervalos_confianza_calculados': False, 'prueba_predictiva_evaluada': False, 'programas_sintaxis_valida': [programa.name for programa in programas]}  # Consolida los controles.
(REPORTES / '07_verificacion_entrega.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda evidencia final.
print(json.dumps(resultado, ensure_ascii=False, indent=2))  # Presenta el cierre.
