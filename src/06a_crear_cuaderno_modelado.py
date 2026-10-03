# ETAPA 7: construcción del cuaderno reproducible de modelado.
# ARCHIVO: 06a_crear_cuaderno_modelado.py; convierte el programa auditado en un recorrido didáctico.
# BLOQUE 1: dependencias y rutas.
from pathlib import Path  # Maneja rutas portables.
import nbformat as nbf  # Crea el cuaderno Jupyter en formato estándar.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto.
FUENTE = RAIZ / 'src/06_desarrollar_modelos.py'  # Localiza el programa validado.
SALIDA = RAIZ / 'notebooks/07_desarrollo_modelos_interpretables.ipynb'  # Define el cuaderno final.

# BLOQUE 2: lectura y división por bloques comentados.
lineas = FUENTE.read_text(encoding='utf-8').splitlines()  # Lee todas las líneas del programa.
indices = [indice for indice, linea in enumerate(lineas) if linea.startswith('# BLOQUE ')]  # Localiza los encabezados de bloque.
indices.append(len(lineas))  # Añade el final para cerrar el último bloque.
bloques = []  # Reserva los bloques ejecutables.
for posicion in range(len(indices) - 1):  # Recorre pares de límites.
    inicio = 0 if posicion == 0 else indices[posicion]  # Incluye encabezados generales en el primer bloque.
    fin = indices[posicion + 1]  # Define el final exclusivo.
    bloques.append('\n'.join(lineas[inicio:fin]).strip() + '\n')  # Conserva comentarios y código íntegros.

# BLOQUE 3: estructura pedagógica del cuaderno.
titulos = [  # Define una explicación antes de cada bloque.
    ('1. Preparación reproducible', 'Carga bibliotecas, rutas, colores y la configuración congelada. Este cuaderno no abre el archivo de prueba reservada.'),  # Explica el bloque 1.
    ('2. Funciones de apoyo', 'Define integridad, métricas ponderadas, selección de umbral y diagnóstico de calibración.'),  # Explica el bloque 2.
    ('3. Lectura y controles de entrenamiento', 'Lee solo entrenamiento, aplica la lista blanca y verifica que cada UPM permanezca en un único pliegue.'),  # Explica el bloque 3.
    ('4. Tuberías de modelado', 'Encapsula imputación, codificación y ajuste para impedir que el preprocesamiento observe el pliegue de validación.'),  # Explica el bloque 4.
    ('5. Selección de hiperparámetros', 'Compara candidatos con los cinco pliegues internos y aplica la regla AUC/Brier preespecificada.'),  # Explica el bloque 5.
    ('6. Predicciones fuera de pliegue e interpretación', 'Genera una predicción independiente por persona y calcula importancia por permutación en las variables originales.'),  # Explica el bloque 6.
    ('7. Umbrales, calibración y grupos', 'Congela puntos de operación con OOF y audita métricas por sexo y área.'),  # Explica el bloque 7.
    ('8. Congelación predictiva', 'Reajusta los candidatos ganadores con todo entrenamiento y guarda los objetos sin aplicarlos a prueba.'),  # Explica el bloque 8.
    ('9. Asociaciones ajustadas', 'Estima razones de momios ponderadas y covarianza robusta con estratos y UPM de la muestra completa.'),  # Explica el bloque 9.
    ('10. Gráficos científicos', 'Produce figuras editables en SVG y copias de alta resolución en PNG.'),  # Explica el bloque 10.
    ('11. Contrato de evaluación', 'Registra versiones, hiperparámetros, umbrales, huellas y controles antes de la evaluación única en prueba.')  # Explica el bloque 11.
]  # Cierra el catálogo pedagógico.
assert len(titulos) == len(bloques)  # Exige una explicación por bloque.
cuaderno = nbf.v4.new_notebook()  # Crea un cuaderno vacío.
cuaderno['cells'].append(nbf.v4.new_markdown_cell('# Etapa 7 · Desarrollo de modelos e interpretación\n\n**Objetivo.** Desarrollar y congelar la regresión logística y el boosting mediante cinco pliegues internos separados por UPM; estimar asociaciones ajustadas y preparar interpretación.\n\n> Regla de integridad: la prueba reservada no se lee ni se evalúa en este cuaderno. Las métricas mostradas son de desarrollo fuera de pliegue.'))  # Añade portada y advertencia.
for (titulo, descripcion), bloque in zip(titulos, bloques):  # Recorre la secuencia didáctica.
    cuaderno['cells'].append(nbf.v4.new_markdown_cell(f'## {titulo}\n\n{descripcion}'))  # Añade la explicación de etapa.
    cuaderno['cells'].append(nbf.v4.new_code_cell(bloque))  # Añade código con comentarios línea por línea.
cuaderno['metadata']['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}  # Declara el kernel.
cuaderno['metadata']['language_info'] = {'name': 'python', 'version': '3.12'}  # Declara el lenguaje.
nbf.write(cuaderno, SALIDA)  # Guarda el cuaderno editable.
print(f'Cuaderno creado: {SALIDA}')  # Informa la ubicación.
