# ETAPA 9: verificación automática del dashboard profesional.
# ARCHIVO: 08a_verificar_dashboard.py; prueba datos, motor estadístico e interfaz sin intervención manual.
# BLOQUE 1: dependencias y rutas.
import ast  # Verifica sintaxis Python.
import hashlib  # Calcula huellas de integridad.
import json  # Lee configuración y escribe controles.
import sys  # Añade el módulo del dashboard a la ruta de importación.
from pathlib import Path  # Maneja rutas portables.
import pandas as pd  # Lee archivos analíticos.
from streamlit.testing.v1 import AppTest  # Ejecuta la aplicación sin navegador.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
DASHBOARD = RAIZ / 'dashboard'  # Localiza el código de interfaz.
REPORTES = RAIZ / 'reports/dashboard'  # Localiza controles.
sys.path.insert(0, str(DASHBOARD))  # Permite importar el motor estadístico.
from metricas import contrastar_grupos, estimar_tasa, preparar_diseno  # Importa funciones después de ajustar la ruta.

# BLOQUE 2: privacidad, diseño y reproducción de resultados científicos.
datos = pd.read_parquet(RAIZ / 'data/dashboard/observatorio_enemdu_2025.parquet')  # Lee la base sin identificadores.
pares = pd.read_parquet(RAIZ / 'data/dashboard/diseno_upm.parquet')  # Lee el diseño completo.
prohibidos = {'id_persona', 'id_hogar', 'id_vivienda', 'id_hogar_sin_mes', 'id_vivienda_sin_mes', 'clave_posicion_sin_mes'}  # Enumera identificadores prohibidos.
assert prohibidos.isdisjoint(datos.columns)  # Exige privacidad estructural.
assert len(datos) == 39551 and len(pares) == 7780 and pares['estrato'].nunique() == 150  # Exige dimensiones auditadas.
assert int(datos['ingreso_monto_observado'].fillna(False).astype(bool).sum()) == 35080  # Exige ingresos observados reconciliados.
diseno = preparar_diseno(pares)  # Prepara el diseño.
tasa = estimar_tasa(datos, diseno, 'adecuado_descriptivo')  # Reproduce la tasa nacional.
brecha = contrastar_grupos(datos, diseno, 'adecuado_descriptivo', 'sexo', 'Mujer', 'Hombre')  # Reproduce la brecha principal.
assert abs(tasa['porcentaje'] - 68.85345472865704) < 1e-10  # Exige coincidencia con EDA 06.
assert abs(brecha['diferencia_pp'] - (-5.909736144772921)) < 1e-10  # Exige coincidencia con EDA 06.
assert tasa['ic95_inferior'] <= tasa['porcentaje'] <= tasa['ic95_superior']  # Exige intervalo ordenado.

# BLOQUE 3: sintaxis y contenido funcional de la aplicación.
codigo_app = (DASHBOARD / 'app.py').read_text(encoding='utf-8')  # Lee la interfaz.
codigo_metricas = (DASHBOARD / 'metricas.py').read_text(encoding='utf-8')  # Lee el motor.
ast.parse(codigo_app)  # Exige sintaxis válida de la interfaz.
ast.parse(codigo_metricas)  # Exige sintaxis válida del motor.
for seccion in ['Panorama', 'Brechas', 'Ingresos', 'Asociaciones', 'Modelos', 'Metodología']:  # Recorre pestañas obligatorias.
    assert seccion in codigo_app  # Exige cada sección.
assert 'id_persona' not in codigo_app and 'predict_proba' not in codigo_app  # Impide exponer identificadores o repuntuar la prueba.

# BLOQUE 4: prueba integral de Streamlit y respuesta a filtros vacíos.
aplicacion = AppTest.from_file(str(DASHBOARD / 'app.py'), default_timeout=120)  # Construye la prueba de interfaz.
aplicacion.run(timeout=120)  # Ejecuta el estado inicial.
assert len(aplicacion.exception) == 0  # Exige cero excepciones.
assert len(aplicacion.metric) >= 11 and len(aplicacion.get('plotly_chart')) >= 10 and len(aplicacion.dataframe) >= 4  # Exige componentes principales.
assert any(metrica.label == 'Empleo adecuado' and metrica.value == '68,9%' for metrica in aplicacion.metric)  # Exige el indicador central visible.
metricas_iniciales = len(aplicacion.metric)  # Conserva el inventario antes de cambiar filtros.
graficos_iniciales = len(aplicacion.get('plotly_chart'))  # Conserva el inventario de gráficos.
aplicacion.multiselect[0].set_value([])  # Vacía el filtro de sexo.
aplicacion.run(timeout=120)  # Ejecuta el estado sin categoría.
assert len(aplicacion.exception) == 0 and any('Seleccione al menos una categoría' in aviso.value for aviso in aplicacion.warning)  # Exige manejo amable del filtro vacío.

# BLOQUE 5: manifiesto y resultado final.
def sha256(ruta):  # Calcula la huella SHA-256.
    objeto = hashlib.sha256()  # Inicializa el algoritmo.
    with ruta.open('rb') as archivo:  # Abre el archivo en bytes.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee por bloques.
            objeto.update(bloque)  # Incorpora contenido.
    return objeto.hexdigest()  # Devuelve la huella.

productos = [DASHBOARD / 'app.py', DASHBOARD / 'metricas.py', RAIZ / 'config/dashboard_v1.json', RAIZ / '.streamlit/config.toml', RAIZ / 'data/dashboard/observatorio_enemdu_2025.parquet', RAIZ / 'data/dashboard/diseno_upm.parquet', RAIZ / 'data/dashboard/etiquetas_dashboard.json', RAIZ / 'iniciar_dashboard.ps1', RAIZ / 'iniciar_dashboard.bat', RAIZ / 'docs/15_guia_dashboard.md']  # Enumera productos editables y datos.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Registra integridad.
manifiesto.to_csv(REPORTES / '03_manifiesto_dashboard.csv', index=False, encoding='utf-8-sig')  # Exporta el manifiesto.
verificacion = {'estado': 'verificado', 'filas_dashboard': len(datos), 'columnas_dashboard': len(datos.columns), 'upm_diseno': len(pares), 'identificadores_personales': 0, 'ingresos_observados': 35080, 'tasa_nacional_reconciliada': True, 'brecha_sexo_reconciliada': True, 'excepciones_estado_inicial': 0, 'componentes_metricas': metricas_iniciales, 'componentes_graficos': graficos_iniciales, 'filtro_vacio_controlado': True, 'pestañas': 6, 'interfaz_repuntua_prueba': False}  # Consolida controles.
(REPORTES / '04_verificacion_dashboard.json').write_text(json.dumps(verificacion, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda la evidencia.
print(json.dumps(verificacion, ensure_ascii=False, indent=2))  # Presenta el resultado.
