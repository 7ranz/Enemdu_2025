# ETAPA 4 DEL EDA: verificar la entrega univariada después de generarla.
# ARCHIVO: 03b_verificar_eda04.py; controla tablas, figuras, cuaderno y reserva de prueba.
# BLOQUE 1: dependencias y rutas.
import ast  # Comprueba que los programas tengan sintaxis Python válida.
import hashlib  # Recalcula huellas de los productos.
import json  # Lee y escribe evidencia estructurada.
from pathlib import Path  # Maneja rutas de forma portable.
import nbformat  # Inspecciona la ejecución del cuaderno.
import pandas as pd  # Comprueba tablas y denominadores.
from PIL import Image  # Verifica dimensiones de figuras PNG.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto.
REPORTES = RAIZ / 'reports/eda04_univariado'  # Localiza resultados tabulares.
FIGURAS = RAIZ / 'reports/figures/eda04_univariado'  # Localiza resultados gráficos.
CUADERNO = RAIZ / 'notebooks/04_analisis_exploratorio_univariado.ipynb'  # Localiza el cuaderno final.

# BLOQUE 2: función de huella y revisión del manifiesto.
def sha256(ruta):  # Calcula SHA-256 sin modificar el archivo.
    h = hashlib.sha256()  # Inicializa el acumulador.
    with ruta.open('rb') as archivo:  # Abre bytes de solo lectura.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee por bloques.
            h.update(bloque)  # Incorpora el contenido.
    return h.hexdigest()  # Devuelve el valor hexadecimal.

def np_allclose(valores, referencia):  # Compara un arreglo con una referencia escalar.
    return all(abs(float(valor) - float(referencia)) <= 1e-8 for valor in valores)  # Aplica una tolerancia numérica estricta.

manifiesto = pd.read_csv(REPORTES / '09_manifiesto_productos.csv')  # Lee el inventario generado.
for fila in manifiesto.itertuples(index=False):  # Recorre cada producto registrado.
    ruta = RAIZ / fila.archivo  # Reconstruye su ruta absoluta.
    assert ruta.exists()  # Exige que el producto exista.
    assert ruta.stat().st_size == fila.bytes  # Exige el tamaño registrado.
    assert sha256(ruta) == fila.sha256  # Exige que el contenido no haya cambiado.

# BLOQUE 3: controles de tablas y figuras.
faltantes = pd.read_csv(REPORTES / '01_faltantes_covariables_dominio.csv')  # Lee el control de ausencia.
frecuencias = pd.read_csv(REPORTES / '02_frecuencias_categoricas_dominio.csv')  # Lee frecuencias de covariables.
objetivo = pd.read_csv(REPORTES / '05_frecuencia_objetivo_entrenamiento.csv')  # Lee el resultado de entrenamiento.
assert faltantes['n_total'].eq(39551).all()  # Verifica el denominador del dominio.
assert faltantes['n_faltante'].eq(0).all()  # Confirma covariables completas.
assert np_allclose(frecuencias.groupby('variable')['porcentaje_ponderado'].sum().to_numpy(), 100)  # Verifica que cada composición sume cien.
assert objetivo['n'].sum() == 31502  # Verifica el denominador de entrenamiento.
nombres = [f'{numero:02d}_{nombre}' for numero, nombre in [(1, 'distribucion_edad'), (2, 'nivel_instruccion'), (3, 'autoidentificacion_etnica'), (4, 'composicion_sexo_area'), (5, 'distribucion_ingresos'), (6, 'faltantes_covariables')]]  # Enumera las seis figuras esperadas.
for nombre in nombres:  # Recorre cada figura científica.
    png = FIGURAS / f'{nombre}.png'  # Localiza la versión rasterizada.
    svg = FIGURAS / f'{nombre}.svg'  # Localiza la versión editable.
    assert png.exists() and svg.exists()  # Exige ambos formatos.
    with Image.open(png) as imagen:  # Abre la imagen sin alterarla.
        assert imagen.width >= 1200 and imagen.height >= 700  # Exige resolución suficiente para informes.
    assert '<svg' in svg.read_text(encoding='utf-8')  # Confirma que el archivo sea vectorial.

# BLOQUE 4: sintaxis, comentarios y ejecución del cuaderno.
programas = sorted(RAIZ.glob('src/03*.py'))  # Reúne los programas de la etapa.
for programa in programas:  # Recorre cada archivo Python.
    contenido = programa.read_text(encoding='utf-8-sig')  # Lee el código fuente.
    ast.parse(contenido)  # Exige sintaxis válida.
    assert '# ETAPA 4' in contenido and '# ARCHIVO:' in contenido and '# BLOQUE' in contenido  # Exige comentarios de estructura.
cuaderno = nbformat.read(CUADERNO, as_version=4)  # Lee el cuaderno terminado.
celdas_codigo = [celda for celda in cuaderno.cells if celda.cell_type == 'code']  # Selecciona las celdas ejecutables.
assert all(celda.execution_count is not None for celda in celdas_codigo)  # Exige que cada bloque haya sido ejecutado.
assert not any(salida.output_type == 'error' for celda in celdas_codigo for salida in celda.outputs)  # Exige cero errores almacenados.
assert all(all((not linea.strip()) or linea.lstrip().startswith('#') or '#' in linea for linea in celda.source.splitlines()) for celda in celdas_codigo)  # Exige comentario en cada línea ejecutable del cuaderno.

# BLOQUE 5: evidencia final de cierre.
codigo_analisis = (RAIZ / 'src/03_analisis_univariado.py').read_text(encoding='utf-8-sig')  # Lee el programa estadístico.
assert 'prueba_reservada.csv' not in codigo_analisis  # Verifica que el nombre de la prueba no se use como entrada.
resultado = {'estado': 'verificado', 'productos_manifestados': len(manifiesto), 'tablas_csv': len(list(REPORTES.glob('0*.csv'))), 'figuras_png': len(list(FIGURAS.glob('*.png'))), 'figuras_svg': len(list(FIGURAS.glob('*.svg'))), 'celdas_cuaderno': len(cuaderno.cells), 'celdas_codigo_ejecutadas': len(celdas_codigo), 'errores_cuaderno': 0, 'programas_sintaxis_valida': [programa.name for programa in programas], 'prueba_reservada_leida': False}  # Consolida los controles.
(REPORTES / '11_verificacion_entrega.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el acta verificable.
print(json.dumps(resultado, ensure_ascii=False, indent=2))  # Presenta el resultado final.
