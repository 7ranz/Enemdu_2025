# ETAPA 5 DEL EDA: construir el cuaderno didáctico del análisis bivariado.
# ARCHIVO: 04a_crear_cuaderno_bivariado.py; genera un cuaderno editable y ejecutable.
# BLOQUE 1: dependencia, ubicación y metadatos.
from pathlib import Path  # Maneja rutas portables.
import nbformat as nbf  # Construye cuadernos Jupyter.
RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
nb = nbf.v4.new_notebook()  # Inicializa el cuaderno.
nb.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}  # Define el núcleo.
nb.metadata['language_info'] = {'name': 'python', 'version': '3.12'}  # Documenta la versión.
celdas = []  # Reúne celdas en orden.

# BLOQUE 2: narrativa y código comentado línea por línea.
celdas.append(nbf.v4.new_markdown_cell('''# EDA 05 — Análisis bivariado del empleo adecuado

**Objetivo:** comparar descriptivamente el porcentaje ponderado de empleo adecuado por sexo, área, edad, nivel educativo y provincia.

El dominio contiene 39 551 registros. La tasa se calcula como suma ponderada de empleo adecuado dividida para la suma de pesos del grupo. Las diferencias están en puntos porcentuales. Todavía no se calculan errores estándar ni intervalos de confianza.

Esta descripción poblacional usa el dominio anual completo. La prueba predictiva permanece cerrada y las conclusiones de esta etapa no modificarán variables, semilla, pliegues, hiperparámetros ni umbral.'''))  # Introduce objetivo y separación de usos.
celdas.append(nbf.v4.new_code_cell('''# ETAPA 5 / ARCHIVO: cuaderno 05 / BLOQUE 1: localizar resultados verificados.
from pathlib import Path  # Representa archivos y carpetas.
import json  # Lee los informes estructurados.
import pandas as pd  # Trabaja con tablas.
from IPython.display import SVG, display  # Presenta tablas y gráficos vectoriales.
RAIZ = Path.cwd() if (Path.cwd() / 'reports/eda05_bivariado').exists() else Path.cwd().parent  # Admite iniciar en proyecto o notebooks.
REPORTES = RAIZ / 'reports/eda05_bivariado'  # Localiza tablas.
FIGURAS = RAIZ / 'reports/figures/eda05_bivariado'  # Localiza figuras.
resumen = json.loads((REPORTES / '00_resumen_eda05.json').read_text(encoding='utf-8'))  # Lee resultados centrales.
verificacion = json.loads((REPORTES / '06_verificacion_eda05.json').read_text(encoding='utf-8'))  # Lee controles.
assert verificacion['estado'] == 'verificado'  # Exige una ejecución validada.
assert verificacion['prueba_predictiva_evaluada'] is False  # Confirma la separación predictiva.
display(pd.Series(resumen, name='valor').to_frame())  # Presenta el alcance general.'''))  # Agrega el bloque inicial.
celdas.append(nbf.v4.new_markdown_cell('''## 1. Tasa total y comparación por sexo

La tasa total ponderada es 68,9 %. En hombres es 72,1 % y en mujeres, 66,2 %. La diferencia mujeres menos hombres es −5,9 puntos porcentuales. Esta brecha es descriptiva; su intervalo de confianza está pendiente.'''))  # Interpreta sexo.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 2: revisar tasas por sexo y su referencia.
tasas = pd.read_csv(REPORTES / '01_tasas_empleo_adecuado_grupos.csv', dtype={'codigo': 'string', 'codigo_referencia': 'string'})  # Lee la tabla principal conservando códigos.
sexo = tasas.loc[tasas['variable'] == 'p02']  # Selecciona sexo.
display(sexo[['etiqueta', 'n', 'porcentaje_no_ponderado', 'porcentaje_ponderado', 'diferencia_referencia_pp', 'upm', 'estratos']])  # Muestra tasa y diferencia.
display(SVG(filename=str(FIGURAS / '01_empleo_adecuado_sexo.svg')))  # Presenta el gráfico editable.'''))  # Agrega sexo.
celdas.append(nbf.v4.new_markdown_cell('''## 2. Área de residencia

La tasa urbana es 70,4 % y la rural, 59,4 %. La diferencia rural menos urbana es −11,0 puntos porcentuales. La composición territorial puede estar relacionada con estructura productiva, edad, provincia y otras características; la comparación no demuestra causalidad.'''))  # Interpreta área.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 3: revisar tasas y brecha por área.
area = tasas.loc[tasas['variable'] == 'area']  # Selecciona área.
display(area[['etiqueta', 'n', 'porcentaje_ponderado', 'diferencia_referencia_pp', 'n_efectivo_pesos_kish']])  # Muestra resultados y tamaño efectivo por pesos.
display(SVG(filename=str(FIGURAS / '02_empleo_adecuado_area.svg')))  # Presenta tasas.
display(SVG(filename=str(FIGURAS / '06_brechas_sexo_area.svg')))  # Presenta las dos brechas principales.'''))  # Agrega área y brechas.
celdas.append(nbf.v4.new_markdown_cell('''## 3. Edad

El porcentaje aumenta durante la entrada y consolidación laboral, permanece cerca de 77–79 % entre 35 y 59 años y disminuye después. Los extremos tienen tamaños pequeños: 11 observaciones entre 15–19 y 5 entre 85–89. Sus valores no son conclusiones estables.

La forma no lineal es una señal para comparar especificaciones de edad dentro de entrenamiento; no autoriza a ajustar el modelo usando la prueba.'''))  # Interpreta edad y cautela.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 4: revisar la curva descriptiva por edad.
edad = tasas.loc[tasas['variable'] == 'grupo_edad']  # Selecciona grupos de edad.
display(edad[['etiqueta', 'n', 'porcentaje_ponderado', 'diferencia_referencia_pp', 'upm', 'estratos']])  # Hace visibles tamaños y tasas.
display(SVG(filename=str(FIGURAS / '03_empleo_adecuado_edad.svg')))  # Presenta la distribución bivariada.'''))  # Agrega edad.
celdas.append(nbf.v4.new_markdown_cell('''## 4. Nivel educativo reportado

Las tasas son 63,9 % en superior no universitaria, 66,3 % en superior universitaria y 85,6 % en posgrado. Frente al nivel universitario, las diferencias son −2,4 y +19,3 puntos porcentuales. `p10a` es nivel reportado, no necesariamente el título más alto.'''))  # Interpreta educación.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 5: revisar educación y referencias.
educacion = tasas.loc[tasas['variable'] == 'p10a']  # Selecciona nivel de instrucción.
display(educacion[['etiqueta', 'n', 'porcentaje_ponderado', 'etiqueta_referencia', 'diferencia_referencia_pp']])  # Presenta contrastes descriptivos.
display(SVG(filename=str(FIGURAS / '04_empleo_adecuado_educacion.svg')))  # Presenta tasas educativas.'''))  # Agrega educación.
celdas.append(nbf.v4.new_markdown_cell('''## 5. Provincia

El rango va de 48,1 % en Chimborazo a 89,7 % en Morona Santiago. Las posiciones no son una clasificación definitiva: las provincias tienen tamaños y composiciones diferentes. La incertidumbre y las comparaciones múltiples se resolverán antes de publicar conclusiones territoriales.'''))  # Interpreta territorio con prudencia.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 6: revisar territorio y diagnósticos de precisión futura.
provincia = tasas.loc[tasas['variable'] == 'prov'].sort_values('porcentaje_ponderado')  # Ordena provincias por tasa.
display(provincia[['etiqueta', 'n', 'porcentaje_ponderado', 'diferencia_total_pp', 'upm', 'estratos']])  # Muestra tasa y soporte muestral.
display(SVG(filename=str(FIGURAS / '05_empleo_adecuado_provincia.svg')))  # Presenta la comparación territorial.'''))  # Agrega provincia.
celdas.append(nbf.v4.new_markdown_cell('''## 6. Preparación de la inferencia

El archivo compacto de diseño contiene las 334 786 filas, 150 estratos y 7 780 UPM. Para un dominio no se deben conservar solamente las filas elegibles: las UPM sin casos aportan cero, pero forman parte de la estimación de variación.

La próxima etapa aplicará linealización de Taylor. Las diferencias usarán su covarianza conjunta; no se tratarán los grupos como muestras independientes. Véase `docs/09_plan_inferencia_diseno.md`.'''))  # Explica por qué se conserva el diseño completo.
celdas.append(nbf.v4.new_code_cell('''# BLOQUE 7: verificar el archivo preparado para diseño complejo.
control = pd.read_csv(REPORTES / '04_control_archivo_inferencia.csv')  # Lee el control sin cargar las 334 786 filas.
diagnostico = pd.read_csv(REPORTES / '03_diagnostico_diseno_grupos.csv')  # Lee alertas por categoría.
display(control)  # Presenta filas, estratos, UPM y grados de libertad.
display(diagnostico.loc[diagnostico['advertencia'] != 'sin alerta descriptiva'].head(20))  # Hace visibles grupos que requieren cautela.
assert control.loc[0, 'filas'] == 334786  # Exige la muestra completa.
assert control.loc[0, 'filas_dominio'] == 39551  # Reconcilia el dominio.'''))  # Agrega controles de diseño.
celdas.append(nbf.v4.new_markdown_cell('''## 7. Lectura responsable

- Una diferencia descriptiva no es todavía “significativa”.
- La asociación bivariada puede cambiar al ajustar simultáneamente otras características.
- Ningún resultado demuestra efectos de sexo, residencia, edad o educación.
- Los grupos pequeños requieren intervalos y reglas de publicación.
- La regresión logística responderá la hipótesis ajustada; el modelo de árboles responderá la comparación predictiva.

**Ejercicio:** identifica el numerador y denominador de la tasa rural. Explica por qué para su intervalo deben conservarse también UPM sin personas rurales del dominio.'''))  # Cierra con interpretación y actividad.
nb.cells = celdas  # Asigna todas las celdas.
nbf.write(nb, RAIZ / 'notebooks/05_analisis_bivariado.ipynb')  # Guarda el cuaderno editable.
print('Cuaderno EDA 05 creado.')  # Confirma la creación.
