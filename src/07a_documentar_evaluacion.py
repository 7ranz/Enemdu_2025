# ETAPA 8: documentación reproducible posterior a la puntuación única.
# ARCHIVO: 07a_documentar_evaluacion.py; trabaja solo con resultados guardados, sin abrir la prueba.
# BLOQUE 1: dependencias y rutas.
from pathlib import Path  # Maneja rutas portables.
import matplotlib  # Configura figuras automáticas.
matplotlib.use('Agg')  # Evita depender de una ventana.
import matplotlib.pyplot as plt  # Genera la figura de brechas.
import nbformat as nbf  # Crea un cuaderno editable.
import pandas as pd  # Lee únicamente tablas ya calculadas.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
SALIDAS = RAIZ / 'reports/eda08_evaluacion'  # Localiza resultados cerrados.
FIGURAS = RAIZ / 'reports/figures/eda08_evaluacion'  # Localiza figuras finales.
CUADERNO = RAIZ / 'notebooks/08_evaluacion_unica_prueba.ipynb'  # Define el cuaderno de lectura.
AZUL = '#0072B2'  # Define azul accesible.
NARANJA = '#E69F00'  # Define naranja accesible.
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 12, 'axes.labelsize': 9})  # Fija estilo reproducible.

# BLOQUE 2: figura científica de brechas con intervalos.
brechas = pd.read_csv(SALIDAS / '06_brechas_desempeno_ic95.csv')  # Lee brechas ya estimadas.
datos = brechas.loc[brechas['metrica'].eq('sensibilidad')].copy()  # Selecciona sensibilidad.
datos['etiqueta'] = datos['modelo'].str.capitalize() + ' · ' + datos['brecha']  # Construye una etiqueta explícita.
datos = datos.iloc[::-1]  # Ordena para lectura superior.
figura, eje = plt.subplots(figsize=(9.2, 5.0))  # Crea el lienzo.
posiciones = range(len(datos))  # Define posiciones verticales.
errores = [100 * (datos['diferencia'] - datos['ic95_inferior']), 100 * (datos['ic95_superior'] - datos['diferencia'])]  # Calcula longitudes de intervalo.
colores = [AZUL if modelo == 'logistica' else NARANJA for modelo in datos['modelo']]  # Distingue modelos.
for posicion, (_, fila), color in zip(posiciones, datos.iterrows(), colores):  # Recorre brechas.
    eje.errorbar(100 * fila['diferencia'], posicion, xerr=[[100 * (fila['diferencia'] - fila['ic95_inferior'])], [100 * (fila['ic95_superior'] - fila['diferencia'])]], fmt='o', color=color, ecolor=color, capsize=4)  # Dibuja punto e IC.
eje.axvline(0, color='#111827', linewidth=0.9)  # Marca igualdad de sensibilidad.
eje.set_yticks(list(posiciones), labels=datos['etiqueta'])  # Etiqueta comparaciones.
eje.set_xlabel('Diferencia de sensibilidad (puntos porcentuales) e IC 95 %')  # Define la métrica.
eje.set_title('Brechas de sensibilidad en la prueba reservada', loc='left', fontweight='bold')  # Titula la figura.
eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Añade guías.
figura.text(0.01, 0.005, 'Diferencias negativas indican menor sensibilidad para mujeres o área rural. Bootstrap de UPM dentro de estrato, 1.000 réplicas.', fontsize=7, color='#374151')  # Añade interpretación.
figura.tight_layout(rect=(0, 0.06, 1, 1))  # Ajusta espacios.
figura.savefig(FIGURAS / '04_brechas_sensibilidad_ic95.png', dpi=200, bbox_inches='tight', facecolor='white')  # Exporta PNG.
figura.savefig(FIGURAS / '04_brechas_sensibilidad_ic95.svg', bbox_inches='tight', facecolor='white')  # Exporta SVG editable.
plt.close(figura)  # Libera memoria.

# BLOQUE 3: cuaderno que documenta resultados sin repetir la puntuación.
cuaderno = nbf.v4.new_notebook()  # Crea un cuaderno vacío.
cuaderno['cells'].append(nbf.v4.new_markdown_cell('# Etapa 8 · Evaluación única en prueba reservada\n\nLa puntuación se ejecutó una sola vez con modelos y umbrales congelados. Este cuaderno **no abre la prueba ni vuelve a ejecutar los modelos**; únicamente lee los resultados cerrados para hacerlos auditables.'))  # Añade portada y regla.
celda_rutas = """# ARCHIVO: cuaderno de lectura de la evaluación cerrada.\n# BLOQUE 1: dependencias y rutas.\nfrom pathlib import Path  # Maneja rutas portables.\nimport json  # Lee el estado cerrado.\nimport pandas as pd  # Lee tablas finales.\nfrom IPython.display import display, Markdown  # Presenta resultados.\nRAIZ = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()  # Localiza la raíz al ejecutar desde proyecto o notebooks.\nSALIDAS = RAIZ / 'reports/eda08_evaluacion'  # Localiza resultados sin acceder a la prueba.\nestado = json.loads((SALIDAS / '00_estado_evaluacion.json').read_text(encoding='utf-8'))  # Lee el cierre persistente.\nassert estado['estado'] == 'completada_y_cerrada'  # Exige que la evaluación esté cerrada.\ndisplay(estado)  # Muestra la evidencia de cierre.\n"""  # Define la primera celda comentada.
cuaderno['cells'].append(nbf.v4.new_markdown_cell('## 1. Evidencia de cierre\n\nComprueba fecha, huellas, modelos y umbrales aplicados.'))  # Explica la primera lectura.
cuaderno['cells'].append(nbf.v4.new_code_cell(celda_rutas))  # Añade la celda.
celda_global = """# BLOQUE 2: desempeño global e intervalos.\nglobales = pd.read_csv(SALIDAS / '01_metricas_prueba_globales.csv')  # Lee estimaciones puntuales.\nintervalos = pd.read_csv(SALIDAS / '02_metricas_prueba_ic95.csv')  # Lee intervalos por UPM.\nseleccion = intervalos.loc[intervalos['metrica'].isin(['roc_auc', 'pr_auc', 'brier', 'exactitud_balanceada'])]  # Selecciona resultados principales.\ndisplay(globales.round(4))  # Presenta todas las métricas.\ndisplay(seleccion.round(4))  # Presenta estimaciones e IC.\n"""  # Define la segunda celda comentada.
cuaderno['cells'].append(nbf.v4.new_markdown_cell('## 2. Desempeño fuera de muestra\n\nCompara prevalencia, logística y boosting con ponderación anual.'))  # Explica métricas.
cuaderno['cells'].append(nbf.v4.new_code_cell(celda_global))  # Añade métricas.
celda_comparacion = """# BLOQUE 3: comparación pareada.\ncomparacion = pd.read_csv(SALIDAS / '03_comparacion_pareada_modelos.csv')  # Lee boosting menos logística.\ndisplay(comparacion.round(4))  # Presenta diferencias y sus IC.\n"""  # Define la tercera celda.
cuaderno['cells'].append(nbf.v4.new_markdown_cell('## 3. ¿Mejora el modelo de árboles?\n\nLos intervalos pareados permiten distinguir una ventaja puntual de una mejora respaldada por la prueba.'))  # Explica la comparación.
cuaderno['cells'].append(nbf.v4.new_code_cell(celda_comparacion))  # Añade comparación.
celda_grupos = """# BLOQUE 4: auditoría por sexo y área.\ngrupos = pd.read_csv(SALIDAS / '05_metricas_prueba_por_grupo.csv')  # Lee desempeño por grupo.\nbrechas = pd.read_csv(SALIDAS / '06_brechas_desempeno_ic95.csv')  # Lee diferencias pareadas.\ndisplay(grupos.round(4))  # Presenta métricas de cada grupo.\ndisplay(brechas.round(4))  # Presenta brechas e IC.\n"""  # Define la cuarta celda.
cuaderno['cells'].append(nbf.v4.new_markdown_cell('## 4. Diferencias entre grupos\n\nSe revisan discriminación, error probabilístico, sensibilidad y especificidad con el mismo umbral global congelado.'))  # Explica auditoría.
cuaderno['cells'].append(nbf.v4.new_code_cell(celda_grupos))  # Añade auditoría.
cuaderno['cells'].append(nbf.v4.new_markdown_cell('## 5. Conclusión\n\nEl boosting muestra una ventaja puntual pequeña en discriminación, pero su intervalo pareado incluye cero. La logística conserva mejor calibración y mayor exactitud balanceada. Ambos modelos presentan menor sensibilidad para mujeres y personas del área rural con los umbrales globales congelados.'))  # Añade conclusión científica.
cuaderno['metadata']['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}  # Declara el kernel.
cuaderno['metadata']['language_info'] = {'name': 'python', 'version': '3.12'}  # Declara el lenguaje.
nbf.write(cuaderno, CUADERNO)  # Guarda el cuaderno editable.
print(f'Documentación creada sin reabrir la prueba: {CUADERNO}')  # Informa el resultado.
