# ETAPA 6: construir el cuaderno didáctico de inferencia con diseño muestral.
# ARCHIVO: 05b_crear_cuaderno_inferencia.py; genera un cuaderno editable y ejecutable.
# BLOQUE 1: dependencia, ubicación y metadatos.
from pathlib import Path  # Maneja rutas portables.
import nbformat as nbf  # Construye cuadernos Jupyter.
RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
nb = nbf.v4.new_notebook()  # Inicializa el cuaderno.
nb.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}  # Define el núcleo.
nb.metadata['language_info'] = {'name': 'python', 'version': '3.12'}  # Documenta el lenguaje.
celdas = []  # Reúne celdas en orden pedagógico.

# BLOQUE 2: narrativa y código comentado línea por línea.
celdas.append(nbf.v4.new_markdown_cell('''# EDA 06 — Intervalos de confianza con diseño muestral

**Objetivo:** incorporar estratos, UPM y `fexp` para cuantificar la precisión de las tasas y de cuatro contrastes primarios.

La tasa de cada grupo es una razón de totales ponderados. Su varianza se estima mediante linealización de Taylor, agregando influencias por UPM y centrándolas dentro de estratos. Se conservan las 334 786 filas para que una UPM sin casos del dominio aporte cero en lugar de desaparecer.

Los intervalos de tasas usan escala logit; los de diferencias, escala lineal y distribución t con 7 630 grados de libertad. Los cuatro valores p primarios se ajustan con Holm.'''))  # Introduce el método.
celdas.append(nbf.v4.new_code_cell('''# ETAPA 6 / ARCHIVO: cuaderno 06 / BLOQUE 1: localizar resultados verificados.
from pathlib import Path  # Representa carpetas y archivos.
import json  # Lee resúmenes estructurados.
import pandas as pd  # Trabaja con tablas.
from IPython.display import SVG, display  # Presenta tablas y figuras vectoriales.
RAIZ = Path.cwd() if (Path.cwd() / 'reports/eda06_inferencia').exists() else Path.cwd().parent  # Admite iniciar en proyecto o notebooks.
REPORTES = RAIZ / 'reports/eda06_inferencia'  # Localiza tablas inferenciales.
FIGURAS = RAIZ / 'reports/figures/eda06_inferencia'  # Localiza gráficos.
resumen = json.loads((REPORTES / '00_resumen_inferencia.json').read_text(encoding='utf-8'))  # Recupera resultados centrales.
verificacion = json.loads((REPORTES / '05_verificacion_inferencia.json').read_text(encoding='utf-8'))  # Recupera controles del cálculo.
assert verificacion['estado'] == 'verificado'  # Exige una ejecución válida.
assert verificacion['prueba_predictiva_evaluada'] is False  # Confirma la separación de la prueba de modelos.
display(pd.Series(resumen, name='valor').to_frame())  # Presenta el resumen.'''))  # Agrega el bloque inicial.
celdas.append(nbf.v4.new_markdown_cell('''## 1. Tasa total y precisión

La tasa total es 68,85 % (IC 95 %: 67,54–70,13). El error estándar es 0,66 puntos porcentuales. El intervalo representa incertidumbre del diseño bajo las decisiones declaradas; no cubre errores de medición o clasificación.'''))  # Interpreta el total.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 2: consultar la estimación total.
tasas = pd.read_csv(REPORTES / '01_tasas_con_ic95.csv', dtype={'codigo': 'string'})  # Lee las 47 estimaciones.
total = tasas.loc[tasas['variable'] == 'total']  # Selecciona el dominio completo.
display(total[['etiqueta', 'n', 'upm_con_casos', 'porcentaje', 'error_estandar_pp', 'ic95_inferior', 'ic95_superior', 'cv_porcentaje']])  # Presenta punto y precisión.'''))  # Agrega la tasa total.
celdas.append(nbf.v4.new_markdown_cell('''## 2. Sexo y área

La diferencia mujeres menos hombres es −5,91 puntos porcentuales (−8,01 a −3,81). La diferencia rural menos urbana es −10,97 puntos (−14,90 a −7,05). Ambas permanecen por debajo de cero después de considerar el diseño y sus valores p de Holm son menores que 0,001.

Esto respalda diferencias observadas, no efectos causales. Todavía falta el ajuste simultáneo mediante regresión.'''))  # Interpreta las hipótesis principales.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 3: revisar sexo, área y contrastes.
contrastes = pd.read_csv(REPORTES / '02_contrastes_primarios_ic95.csv')  # Lee las cuatro comparaciones preespecificadas.
display(contrastes[['grupo_a', 'grupo_b', 'diferencia_pp', 'error_estandar_pp', 'ic95_inferior', 'ic95_superior', 'valor_p_holm', 'significativo_holm_005']])  # Presenta magnitud, precisión y evidencia.
display(SVG(filename=str(FIGURAS / '01_ic_sexo.svg')))  # Presenta tasas por sexo.
display(SVG(filename=str(FIGURAS / '02_ic_area.svg')))  # Presenta tasas por área.
display(SVG(filename=str(FIGURAS / '06_ic_contrastes_primarios.svg')))  # Presenta diferencias frente a cero.'''))  # Agrega resultados principales.
celdas.append(nbf.v4.new_markdown_cell('''## 3. Educación

Superior no universitaria menos universitaria es −2,37 puntos (−5,42 a 0,67; p de Holm=0,127). El intervalo incluye cero. Posgrado menos universitaria es +19,31 puntos (16,84 a 21,77; p de Holm<0,001). La diferencia observada puede estar confundida por otras características.'''))  # Interpreta educación.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 4: revisar tasas educativas e intervalos.
educacion = tasas.loc[tasas['variable'] == 'p10a']  # Selecciona nivel reportado.
display(educacion[['etiqueta', 'n', 'porcentaje', 'error_estandar_pp', 'ic95_inferior', 'ic95_superior', 'cv_porcentaje']])  # Presenta precisión educativa.
display(SVG(filename=str(FIGURAS / '04_ic_educacion.svg')))  # Presenta el gráfico educativo.'''))  # Agrega educación.
celdas.append(nbf.v4.new_markdown_cell('''## 4. Edad y grupos pequeños

La prueba global detecta heterogeneidad por edad. Las categorías de 15–19, 80–84 y 85–89 tienen menos de 100 registros. Sus intervalos son amplios y los CV alcanzan valores muy altos. Antes de publicar comparaciones por edad se deberá justificar una agrupación más estable.'''))  # Advierte sobre precisión.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 5: revisar edad y alertas de tamaño.
edad = tasas.loc[tasas['variable'] == 'grupo_edad']  # Selecciona grupos etarios.
display(edad[['etiqueta', 'n', 'porcentaje', 'ic95_inferior', 'ic95_superior', 'cv_porcentaje', 'alerta_n_menor_100']])  # Hace visibles las alertas.
display(SVG(filename=str(FIGURAS / '03_ic_edad.svg')))  # Presenta puntos e intervalos.'''))  # Agrega edad.
celdas.append(nbf.v4.new_markdown_cell('''## 5. Provincia

Existe heterogeneidad global entre provincias, pero los intervalos tienen amplitudes diferentes y muchas estimaciones se superponen. Morona Santiago tiene el punto más alto, 89,66 %, con IC 71,52–96,77; su intervalo impide tratar la posición como un rango exacto. No se hicieron comparaciones entre todos los pares.'''))  # Interpreta territorio.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 6: revisar tasas provinciales con precisión.
provincia = tasas.loc[tasas['variable'] == 'prov'].sort_values('porcentaje')  # Ordena puntos para lectura.
display(provincia[['etiqueta', 'n', 'upm_con_casos', 'porcentaje', 'error_estandar_pp', 'ic95_inferior', 'ic95_superior', 'cv_porcentaje']])  # Presenta soporte e incertidumbre.
display(SVG(filename=str(FIGURAS / '05_ic_provincia.svg')))  # Presenta el perfil territorial.'''))  # Agrega provincia.
celdas.append(nbf.v4.new_markdown_cell('''## 6. Pruebas globales

Una prueba global evalúa si todas las categorías podrían compartir la misma tasa. Sexo, área, edad, educación y provincia presentan evidencia global al 5 %. La prueba no identifica por sí sola qué pares difieren; para eso se necesitan contrastes definidos y control de multiplicidad.'''))  # Explica pruebas conjuntas.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 7: consultar pruebas globales de Wald.
globales = pd.read_csv(REPORTES / '03_pruebas_globales_wald.csv')  # Lee las cinco pruebas.
display(globales)  # Presenta grados de libertad, estadístico y valor p.
assert globales['evidencia_global_005'].all()  # Confirma el resultado registrado.'''))  # Agrega pruebas globales.
celdas.append(nbf.v4.new_markdown_cell('''## 7. Tabla científica y siguiente etapa

La tabla científica combina estimación, error estándar, IC, CV, n, UPM, estratos y grados de libertad. El Excel incluye hojas de resumen, detalle, contrastes, pruebas globales y método.

La hipótesis de diferencias descriptivas queda evaluada. La hipótesis ajustada requiere regresión logística. La comparación entre regresión y árboles requiere desarrollar modelos con los cinco pliegues internos, congelar las decisiones y usar la prueba una sola vez.

**Ejercicio:** compara el punto y el intervalo de Morona Santiago con Pichincha. Explica por qué el punto mayor no basta para afirmar que la tasa poblacional sea mayor.'''))  # Cierra y conecta con modelado.
nb.cells = celdas  # Asigna todas las celdas.
nbf.write(nb, RAIZ / 'notebooks/06_inferencia_diseno.ipynb')  # Guarda el cuaderno editable.
print('Cuaderno EDA 06 creado.')  # Confirma la creación.
