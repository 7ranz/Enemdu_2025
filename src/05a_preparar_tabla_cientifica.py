# ETAPA 6: preparar tablas editables para publicación y para el libro Excel.
# ARCHIVO: 05a_preparar_tabla_cientifica.py; reúne resultados verificados sin recalcular la inferencia.
# BLOQUE 1: dependencias y rutas.
import json  # Escribe un intercambio tipado para el generador del libro.
from pathlib import Path  # Maneja rutas portables.
import pandas as pd  # Selecciona y organiza las tablas.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
REPORTES = RAIZ / 'reports/eda06_inferencia'  # Localiza resultados inferenciales.
TASAS = pd.read_csv(REPORTES / '01_tasas_con_ic95.csv', dtype={'codigo': 'string'})  # Lee tasas e intervalos.
CONTRASTES = pd.read_csv(REPORTES / '02_contrastes_primarios_ic95.csv')  # Lee diferencias primarias.
GLOBALES = pd.read_csv(REPORTES / '03_pruebas_globales_wald.csv')  # Lee pruebas globales.

# BLOQUE 2: tabla científica principal en formato largo.
orden_variables = ['total', 'p02', 'area', 'p10a']  # Prioriza total, hipótesis y educación.
principal = TASAS.loc[TASAS['variable'].isin(orden_variables)].copy()  # Selecciona estimaciones principales.
principal['orden_variable'] = principal['variable'].map({valor: indice for indice, valor in enumerate(orden_variables)})  # Define el orden editorial.
principal = principal.sort_values(['orden_variable', 'codigo']).drop(columns='orden_variable')  # Aplica el orden y retira el auxiliar.
principal = principal[['variable', 'codigo', 'etiqueta', 'n', 'upm_con_casos', 'estratos_con_casos', 'porcentaje', 'error_estandar_pp', 'ic95_inferior', 'ic95_superior', 'cv_porcentaje', 'grados_libertad', 'alerta_n_menor_100']]  # Conserva columnas publicables.
principal.to_csv(REPORTES / '06_tabla_cientifica_principal.csv', index=False, encoding='utf-8-sig')  # Exporta una tabla editable y compacta.

# BLOQUE 3: paquete JSON tipado para Excel.
resumen = json.loads((REPORTES / '00_resumen_inferencia.json').read_text(encoding='utf-8'))  # Recupera resultados centrales.
metodo = [{'campo': 'Población', 'valor': 'PEA de 15 años o más con nivel superior reportado y título'}, {'campo': 'Resultado', 'valor': 'Empleo adecuado según adecuado_descriptivo'}, {'campo': 'Diseño', 'valor': '150 estratos, 7 780 UPM y fexp anual'}, {'campo': 'Varianza', 'valor': 'Linealización de Taylor, aproximación con reemplazo y sin FPC'}, {'campo': 'IC de tasas', 'valor': '95 %, escala logit y transformación inversa'}, {'campo': 'IC de diferencias', 'valor': '95 %, escala lineal y distribución t con 7 630 gl'}, {'campo': 'Multiplicidad', 'valor': 'Holm para los cuatro contrastes primarios'}, {'campo': 'Fuente de microdatos', 'valor': 'https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip'}, {'campo': 'Guía oficial', 'valor': 'https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Guia_de_usuario_BDD_ENEMDU_anual_2025.pdf'}, {'campo': 'Nota', 'valor': 'Asociaciones observacionales; no demuestran efectos causales. La prueba predictiva no se evaluó.'}]  # Documenta método, fuentes y límite.
paquete = {'resumen': resumen, 'principal': json.loads(principal.to_json(orient='records')), 'tasas': json.loads(TASAS.to_json(orient='records')), 'contrastes': json.loads(CONTRASTES.to_json(orient='records')), 'globales': json.loads(GLOBALES.to_json(orient='records')), 'metodo': metodo}  # Reúne matrices tipadas.
(REPORTES / 'tabla_cientifica_datos.json').write_text(json.dumps(paquete, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el intercambio reproducible.
print(json.dumps({'estado': 'preparado', 'filas_principal': len(principal), 'filas_tasas': len(TASAS), 'contrastes': len(CONTRASTES), 'pruebas_globales': len(GLOBALES)}, ensure_ascii=False))  # Presenta el inventario.
