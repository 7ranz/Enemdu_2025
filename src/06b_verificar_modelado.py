# ETAPA 7: verificación independiente de productos congelados.
# ARCHIVO: 06b_verificar_modelado.py; comprueba coherencia sin abrir la prueba reservada.
# BLOQUE 1: dependencias y rutas.
import ast  # Inspecciona que el programa sea sintácticamente válido.
import json  # Lee y escribe resultados estructurados.
from pathlib import Path  # Maneja rutas portables.
import joblib  # Carga los modelos congelados.
import nbformat  # Valida la estructura del cuaderno.
import numpy as np  # Comprueba probabilidades numéricas.
import pandas as pd  # Lee tablas de resultados y una muestra de entrenamiento.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
SALIDAS = RAIZ / 'reports/eda07_modelado'  # Localiza los reportes.
MODELOS = RAIZ / 'models'  # Localiza los objetos congelados.
FUENTE = RAIZ / 'src/06_desarrollar_modelos.py'  # Localiza el programa principal.
CUADERNO = RAIZ / 'notebooks/07_desarrollo_modelos_interpretables.ipynb'  # Localiza el cuaderno.

# BLOQUE 2: estructura, cobertura y reglas de integridad.
texto_fuente = FUENTE.read_text(encoding='utf-8')  # Lee el programa sin ejecutarlo.
ast.parse(texto_fuente)  # Exige sintaxis válida del programa principal.
lecturas_principales = [linea.strip() for linea in texto_fuente.splitlines() if 'pd.read_csv(' in linea]  # Enumera todas las lecturas tabulares del desarrollo.
assert len(lecturas_principales) == 2 and any('ENTRADA' in linea for linea in lecturas_principales) and any('BASE_COMPLETA' in linea for linea in lecturas_principales)  # Exige que solo se lean entrenamiento y diseño completo.
cuaderno = nbformat.read(CUADERNO, as_version=4)  # Lee el cuaderno sin ejecutarlo.
for celda in [celda for celda in cuaderno.cells if celda.cell_type == 'code']:  # Recorre celdas ejecutables.
    compile(celda.source, str(CUADERNO), 'exec')  # Exige sintaxis válida en cada celda.
config = json.loads((RAIZ / 'config/modelado_v1.json').read_text(encoding='utf-8'))  # Lee la lista blanca.
prohibidos = set(json.loads((RAIZ / 'config/preparacion_v1.json').read_text(encoding='utf-8'))['prohibidos_como_predictores'])  # Lee la lista de fuga.
assert not set(config['predictores_numericos'] + config['predictores_categoricos']) & prohibidos  # Exige cero predictores prohibidos.
predicciones = pd.read_csv(RAIZ / 'data/processed/modelado/desarrollo/predicciones_oof.csv.gz', dtype={'id_persona': 'string', 'upm': 'string'})  # Lee solo predicciones internas.
metricas = pd.read_csv(SALIDAS / '03_metricas_oof_globales.csv')  # Lee métricas globales.
asociaciones = pd.read_csv(SALIDAS / '09_asociaciones_ajustadas_or.csv')  # Lee inferencia ajustada.
metadatos = json.loads((MODELOS / 'metadatos_modelos_congelados.json').read_text(encoding='utf-8'))  # Lee el contrato congelado.
assert len(predicciones) == 31502  # Exige cobertura completa de entrenamiento.
assert predicciones['id_persona'].is_unique  # Exige una predicción por registro anual.
assert predicciones.groupby('upm')['pliegue_cv'].nunique().max() == 1  # Exige separación de UPM.
assert predicciones[['p_base', 'p_logistica', 'p_boosting']].apply(lambda columna: columna.between(0, 1).all()).all()  # Exige probabilidades válidas.
assert set(metricas['modelo']) == {'base', 'logistica', 'boosting'}  # Exige los tres comparadores.
assert asociaciones['razon_momios'].gt(0).all()  # Exige razones de momios positivas.
assert (asociaciones['ic95_inferior'] <= asociaciones['razon_momios']).all() and (asociaciones['razon_momios'] <= asociaciones['ic95_superior']).all()  # Exige orden correcto de IC.
assert metadatos['prueba_reservada']['leida'] is False and metadatos['prueba_reservada']['evaluada'] is False  # Exige el estado cerrado de prueba.

# BLOQUE 3: carga funcional de los dos modelos sin usar prueba.
tipos = {columna: 'string' for columna in config['predictores_categoricos']}  # Conserva códigos categóricos.
muestra = pd.read_csv(RAIZ / config['archivo_desarrollo'], nrows=25, dtype=tipos, encoding='utf-8-sig')  # Lee una muestra permitida de desarrollo.
muestra['mes'] = muestra['mes'].str.zfill(2)  # Homogeneiza mes.
for columna in config['predictores_categoricos']:  # Recorre variables categóricas.
    muestra[columna] = muestra[columna].str.replace(r'\.0$', '', regex=True)  # Homogeneiza códigos.
x_muestra = muestra[config['predictores_numericos'] + config['predictores_categoricos']]  # Aplica la lista blanca.
for archivo in ['logistica_predictiva_congelada.joblib', 'boosting_congelado.joblib']:  # Recorre artefactos.
    modelo = joblib.load(MODELOS / archivo)  # Carga el modelo serializado.
    probabilidades = modelo.predict_proba(x_muestra)[:, 1]  # Predice exclusivamente sobre desarrollo.
    assert len(probabilidades) == len(x_muestra) and np.isfinite(probabilidades).all() and ((probabilidades >= 0) & (probabilidades <= 1)).all()  # Exige funcionamiento válido.

# BLOQUE 4: inventario y resultado final.
esperados = ['00_resumen_modelado.json', '01_resultados_cv_por_pliegue.csv', '02_resumen_seleccion_hiperparametros.csv', '03_metricas_oof_globales.csv', '04_trayectoria_umbrales_oof.csv', '05_calibracion_oof_deciles.csv', '06_metricas_oof_por_grupo.csv', '07_importancia_permutacion_detalle.csv', '08_importancia_permutacion_resumen.csv', '09_asociaciones_ajustadas_or.csv', '10_pruebas_wald_ajustadas.csv', '11_manifiesto_productos.csv']  # Enumera tablas obligatorias.
assert all((SALIDAS / nombre).exists() for nombre in esperados)  # Exige todos los reportes.
assert len(list((RAIZ / 'reports/figures/eda07_modelado').glob('*.png'))) == 4  # Exige cuatro figuras PNG.
assert len(list((RAIZ / 'reports/figures/eda07_modelado').glob('*.svg'))) == 4  # Exige cuatro figuras editables SVG.
verificacion = {'estado': 'verificado', 'filas_oof': len(predicciones), 'upm_oof': predicciones['upm'].nunique(), 'cobertura_oof_completa': True, 'upm_en_un_pliegue': True, 'probabilidades_validas': True, 'predictores_prohibidos': 0, 'lecturas_programa_principal': ['entrenamiento', 'base_completa_para_diseno'], 'modelos_cargan_y_predicen': True, 'coeficientes_ajustados': len(asociaciones), 'cuaderno_celdas_codigo': len([celda for celda in cuaderno.cells if celda.cell_type == 'code']), 'figuras_png': 4, 'figuras_svg': 4, 'prueba_reservada_leida': False, 'prueba_reservada_evaluada': False}  # Consolida la evidencia.
(SALIDAS / '12_verificacion_entrega.json').write_text(json.dumps(verificacion, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el control independiente.
print(json.dumps(verificacion, ensure_ascii=False, indent=2))  # Presenta el resultado.
