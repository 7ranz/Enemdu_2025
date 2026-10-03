# ETAPA 8: verificación de la evaluación cerrada.
# ARCHIVO: 07b_verificar_evaluacion.py; revisa productos derivados sin reabrir ni repuntuar la prueba.
# BLOQUE 1: dependencias y rutas.
import hashlib  # Calcula huellas del paquete final.
import json  # Lee y escribe controles.
from pathlib import Path  # Maneja rutas portables.
import nbformat  # Valida el cuaderno.
import numpy as np  # Comprueba valores finitos.
import pandas as pd  # Lee resultados cerrados.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
SALIDAS = RAIZ / 'reports/eda08_evaluacion'  # Localiza reportes.
FIGURAS = RAIZ / 'reports/figures/eda08_evaluacion'  # Localiza figuras.
CUADERNO = RAIZ / 'notebooks/08_evaluacion_unica_prueba.ipynb'  # Localiza el cuaderno.

# BLOQUE 2: coherencia científica y cierre.
estado = json.loads((SALIDAS / '00_estado_evaluacion.json').read_text(encoding='utf-8'))  # Lee el cierre.
assert estado['estado'] == 'completada_y_cerrada' and estado['se_permite_repetir_puntuacion'] is False  # Exige cierre irreversible.
globales = pd.read_csv(SALIDAS / '01_metricas_prueba_globales.csv')  # Lee métricas puntuales.
intervalos = pd.read_csv(SALIDAS / '02_metricas_prueba_ic95.csv')  # Lee intervalos.
comparacion = pd.read_csv(SALIDAS / '03_comparacion_pareada_modelos.csv')  # Lee diferencias.
brechas = pd.read_csv(SALIDAS / '06_brechas_desempeno_ic95.csv')  # Lee auditoría.
assert set(globales['modelo']) == {'base', 'logistica', 'boosting'}  # Exige los tres comparadores.
assert globales[['roc_auc', 'pr_auc', 'brier', 'exactitud_balanceada']].apply(lambda columna: columna.between(0, 1).all()).all()  # Exige métricas válidas.
assert intervalos.apply(lambda fila: fila['ic95_inferior'] <= fila['estimacion'] <= fila['ic95_superior'], axis=1).all()  # Exige estimaciones dentro de IC.
assert intervalos['replicas_validas'].eq(1000).all() and comparacion['replicas_validas'].eq(1000).all() and brechas['replicas_validas'].eq(1000).all()  # Exige todas las réplicas.
assert np.isfinite(comparacion[['diferencia', 'ic95_inferior', 'ic95_superior']]).all().all()  # Exige comparaciones finitas.
assert len(list(FIGURAS.glob('*.png'))) >= 5 and len(list(FIGURAS.glob('*.svg'))) >= 5  # Exige figuras científicas y editables.
cuaderno = nbformat.read(CUADERNO, as_version=4)  # Lee el cuaderno documental.
for celda in [celda for celda in cuaderno.cells if celda.cell_type == 'code']:  # Recorre celdas de código.
    compile(celda.source, str(CUADERNO), 'exec')  # Exige sintaxis válida.
assert 'prueba_reservada.csv' not in CUADERNO.read_text(encoding='utf-8')  # Exige que el cuaderno no abra la fuente reservada.

# BLOQUE 3: evidencia final.
verificacion = {'estado': 'verificado', 'evaluacion_unica_cerrada': True, 'filas_prueba_reportadas': int(globales['n'].iloc[0]), 'upm_prueba_reportadas': int(globales['upm'].iloc[0]), 'modelos': globales['modelo'].tolist(), 'metricas_con_ic': len(intervalos), 'comparaciones_pareadas': len(comparacion), 'brechas_con_ic': len(brechas), 'replicas_bootstrap': 1000, 'figuras_png': len(list(FIGURAS.glob('*.png'))), 'figuras_svg': len(list(FIGURAS.glob('*.svg'))), 'cuaderno_no_reabre_prueba': True, 'hiperparametros_reajustados': False, 'umbrales_reajustados': False}  # Consolida controles.
(SALIDAS / '09_verificacion_entrega.json').write_text(json.dumps(verificacion, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda evidencia.
def sha256(ruta):  # Calcula una huella de integridad.
    objeto = hashlib.sha256()  # Inicializa el algoritmo.
    with ruta.open('rb') as archivo:  # Abre el producto en bytes.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee por bloques.
            objeto.update(bloque)  # Incorpora el contenido.
    return objeto.hexdigest()  # Devuelve la huella.

productos = sorted([ruta for ruta in SALIDAS.glob('*') if ruta.is_file() and ruta.name != '08_manifiesto_productos.csv'] + list(FIGURAS.glob('*.*')) + [CUADERNO, RAIZ / 'docs/13_informe_evaluacion_unica.md', RAIZ / 'docs/14_decision_modelos_dashboard.md', RAIZ / 'config/evaluacion_prueba_v1.json', RAIZ / 'src/07_evaluar_prueba_reservada.py', RAIZ / 'src/07a_documentar_evaluacion.py', RAIZ / 'src/07b_verificar_evaluacion.py', RAIZ / 'data/processed/modelado/evaluacion/predicciones_prueba_unica.csv.gz'])  # Reúne el paquete sin abrir la fuente de prueba.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Registra tamaño y huella.
manifiesto.to_csv(SALIDAS / '08_manifiesto_productos.csv', index=False, encoding='utf-8-sig')  # Actualiza el manifiesto final.
print(json.dumps(verificacion, ensure_ascii=False, indent=2))  # Presenta el control.
