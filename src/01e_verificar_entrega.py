# ETAPA 2 DEL EDA: comprobar coherencia de las salidas antes de entregar la auditoría.
# ARCHIVO: 01e_verificar_entrega.py. Valida informes y cuaderno; no modifica microdatos.
# BLOQUE 1: herramientas y rutas.
import ast  # Comprueba sintaxis Python sin ejecutar los programas.
import hashlib  # Calcula las huellas de fuentes y programas.
import json  # Lee resultados y guarda el acta de verificación.
from pathlib import Path  # Maneja rutas portables.
import nbformat  # Comprueba el formato y las salidas del cuaderno.
import pandas as pd  # Verifica conciliaciones entre tablas de reporte.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
SALIDA = RAIZ / 'reports/calidad'  # Ubica las salidas que se comprobarán.
resumen = json.loads((SALIDA / '00_resumen_auditoria.json').read_text(encoding='utf-8'))  # Lee el resumen definitivo.
original = json.loads((RAIZ / 'reports/00_verificacion_fuentes.json').read_text(encoding='utf-8'))  # Lee el inventario de la primera etapa.
mensual = pd.read_csv(SALIDA / '10_cobertura_mensual.csv')  # Lee recuentos por mes.
reglas = pd.read_csv(SALIDA / '03_reglas_calidad.csv', dtype={'mes': str})  # Lee controles y ámbitos.
perfil = pd.read_csv(SALIDA / '01_perfil_variables_mes.csv', dtype={'mes': str})  # Lee el perfil independiente de los controles lógicos.
codigos = pd.read_csv(SALIDA / '15_validacion_codigos_spss.csv', dtype={'mes': str})  # Lee validación con etiquetas oficiales.
formularios = json.loads((SALIDA / 'formularios_mensuales.json').read_text(encoding='utf-8'))  # Lee evidencia de los doce formularios.

# BLOQUE 2: comprobar conciliaciones que detectan archivos desactualizados o resultados truncados.
assert resumen['filas_personas'] == original['registros_personas'] == int(mensual['registros'].sum())  # Concilia tres salidas obtenidas en fases diferentes.
assert resumen['sha256_original'] == original['sha256_zip']  # Verifica que las etapas utilizan exactamente la misma base.
assert hashlib.sha256((RAIZ / 'data/raw/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip').read_bytes()).hexdigest() == resumen['sha256_original']  # Comprueba también la fuente actual, no solo los reportes.
assert resumen['candidatos_edad_conocida'] == int(mensual['candidatos'].sum())  # Concilia el dominio del estudio.
assert reglas['regla'].nunique() == resumen['reglas_distintas']  # Comprueba el inventario de reglas.
assert len(reglas) == resumen['reglas_distintas'] * 13  # Exige cada regla en el año y los doce meses.
assert len(perfil) == (resumen['columnas_personas'] + resumen['columnas_vivienda_hogar']) * 13  # Verifica cobertura de todos los campos y meses.
assert codigos.loc[codigos['mes'].eq('ANUAL'), 'n_no_etiquetados'].sum() == 0  # Confirma el hallazgo anunciado sobre códigos.
assert len(formularios) == 12 and all(f['estado']=='pregunta_localizada' and f['pregunta12_si1_no2'] for f in formularios)  # Verifica cobertura documental positiva, sin confundir errores con ausencia de cambios.
assert len({f['pregunta10_sha256_texto'] for f in formularios}) == 1 and all(f['pregunta10_sha256_texto'] for f in formularios)  # Exige coincidencia de fragmentos encontrados, no de valores vacíos.
assert len({f['pregunta12_sha256_fragmento'] for f in formularios}) == 1  # Comprueba la igualdad de titulación entre meses.
for fuente in formularios:  # Comprueba que cada PDF guardado corresponde a su evidencia.
    assert hashlib.sha256((RAIZ / fuente['archivo']).read_bytes()).hexdigest() == fuente['sha256']  # Detecta sustituciones de documentos.

# BLOQUE 3: verificar sintaxis de programas y ejecución real de las celdas.
programas = sorted((RAIZ / 'src').glob('01*.py'))  # Localiza los programas de la etapa.
for programa in programas:  # Examina cada fuente entregada.
    ast.parse(programa.read_text(encoding='utf-8'))  # Falla si encuentra sintaxis Python inválida.
cuaderno = nbformat.read(RAIZ / 'notebooks/02_calidad_identificadores_meses.ipynb', as_version=4)  # Lee el cuaderno final guardado.
nbformat.validate(cuaderno)  # Comprueba el estándar de archivo Jupyter.
celdas = [celda for celda in cuaderno.cells if celda.cell_type == 'code']  # Selecciona las celdas ejecutables.
assert all(celda.execution_count is not None for celda in celdas)  # Exige que todas hayan sido ejecutadas.
assert not any(salida.output_type == 'error' for celda in celdas for salida in celda.outputs)  # Exige ausencia de errores guardados.

# BLOQUE 4: conservar evidencia de fuentes locales y resultado de las comprobaciones.
archivos = sorted((RAIZ / 'data/raw').rglob('*'))  # Enumera los originales conservados localmente.
manifiesto = [{'archivo': str(ruta.relative_to(RAIZ)), 'bytes': ruta.stat().st_size, 'sha256': hashlib.sha256(ruta.read_bytes()).hexdigest()} for ruta in archivos if ruta.is_file()]  # Calcula huellas sin sobrescribir fuentes.
pd.DataFrame(manifiesto).to_csv(SALIDA / '19_manifiesto_fuentes.csv', index=False, encoding='utf-8-sig')  # Guarda trazabilidad de todas las copias locales.
acta = {'estado': 'comprobaciones_superadas', 'base_original_sin_cambios': True, 'reglas': resumen['reglas_distintas'], 'perfiles_variable_periodo': len(perfil), 'variables_categoricas': int(codigos['variable'].nunique()), 'formularios_verificados': len(formularios), 'programas_con_sintaxis_valida': len(programas), 'celdas_codigo_ejecutadas_sin_error': len(celdas), 'sha256_programas': {ruta.name: hashlib.sha256(ruta.read_bytes()).hexdigest() for ruta in programas}}  # Resume exclusivamente verificaciones realizadas.
(SALIDA / '20_verificacion_entrega.json').write_text(json.dumps(acta, ensure_ascii=False, indent=2), encoding='utf-8')  # Conserva el acta reproducible.
print(json.dumps(acta, ensure_ascii=False, indent=2))  # Informa la cobertura final de las comprobaciones.
