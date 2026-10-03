# EDA 05 — Empleo adecuado por sexo, área, edad, educación y territorio

Fecha de cierre: 29 de septiembre de 2026. Esta etapa presenta asociaciones descriptivas bivariadas. Las diferencias están expresadas en puntos porcentuales y todavía no incluyen errores estándar, intervalos de confianza ni pruebas ajustadas al diseño muestral.

## Población y definición

El análisis utiliza las 39 551 observaciones del dominio: personas de 15 años o más, económicamente activas, con nivel superior reportado y título. El numerador corresponde a `adecuado_descriptivo=1`; el denominador incluye toda la PEA del dominio, incluidos los 258 registros de empleo no clasificado como ausencia de empleo adecuado. Esta definición es apropiada para la tasa descriptiva, aunque esos registros no integran la etiqueta del modelo predictivo.

Las tasas usan el factor anual `fexp`. Una diferencia positiva significa mayor porcentaje de empleo adecuado que el grupo de referencia; una negativa, menor porcentaje. Son asociaciones observadas y no efectos causales.

La tasa ponderada total de empleo adecuado es **68,9 %**. El porcentaje sin ponderar y los tamaños muestrales se mantienen en las tablas para auditar el efecto de la ponderación.

## Sexo y área

La tasa ponderada es 72,1 % en hombres y 66,2 % en mujeres. La diferencia mujeres menos hombres es **−5,9 puntos porcentuales**.

En el área urbana la tasa es 70,4 % y en la rural, 59,4 %. La diferencia rural menos urbana es **−11,0 puntos porcentuales**. Esta es la mayor de las dos brechas principales examinadas, pero no debe calificarse todavía como estadísticamente significativa.

## Edad

La tasa aumenta desde 40,6 % entre 20 y 24 años hasta valores cercanos a 77–79 % entre 35 y 59 años. Luego desciende a 68,8 % entre 60 y 64, 52,4 % entre 65 y 69 y 43,2 % entre 70 y 74 años.

Los grupos extremos requieren especial cautela. Hay solamente 11 observaciones entre 15 y 19 años, 48 entre 80 y 84 y 5 entre 85 y 89. Sus porcentajes no deben usarse como conclusiones sustantivas antes de calcular incertidumbre y revisar reglas de agrupación. No hubo observaciones del dominio en los grupos de 90 años o más.

La forma observada sugiere una relación no lineal entre edad y empleo adecuado. En el modelado no conviene imponer automáticamente una relación lineal; se compararán una forma flexible predefinida y una especificación parsimoniosa utilizando únicamente los pliegues de entrenamiento.

## Educación

La tasa es 63,9 % para superior no universitaria, 66,3 % para superior universitaria y 85,6 % para posgrado. Respecto al nivel universitario, las diferencias descriptivas son −2,4 y +19,3 puntos porcentuales, respectivamente.

`p10a` representa el nivel de instrucción reportado y no necesariamente el nivel del título más alto obtenido. La asociación no demuestra que cursar un posgrado cause la diferencia, porque edad, ocupación, territorio, experiencia y selección laboral pueden estar relacionados con ambos elementos.

## Territorio

Las tasas provinciales varían entre 48,1 % en Chimborazo y 89,7 % en Morona Santiago. Entre los valores inferiores también aparecen Cotopaxi (55,4 %) y Los Ríos (60,1 %); entre los superiores, Galápagos (85,7 %) y Zamora Chinchipe (83,7 %).

Estas posiciones son descriptivas. Las provincias difieren en número de observaciones, UPM, composición de edad, educación y área. Morona Santiago tiene 281 registros y 64 UPM; Galápagos, 386 y 79 UPM. No se publicará una clasificación definitiva de provincias hasta disponer de intervalos de confianza y evaluar comparaciones múltiples.

## Archivo preparado para inferencia

Se creó `data/processed/inferencia/diseno_bivariado.csv.gz` con las 334 786 filas de la muestra completa. Conserva 150 estratos, 7 780 UPM y el peso `fexp`, además de indicadores de numerador y denominador. Los grados de libertad preliminares del diseño son 7 630, calculados como UPM menos estratos.

Conservar la muestra completa es esencial para inferencia de subpoblaciones: las observaciones fuera del dominio aportan cero al numerador y denominador, pero sus UPM siguen formando parte de la estructura usada para estimar variación. Filtrar primero las 39 551 filas podría eliminar UPM sin casos del dominio y alterar la varianza.

El diagnóstico por grupo informa número de registros, UPM, estratos, tamaño efectivo de Kish debido a pesos y estratos con una sola UPM que contiene casos. Este último dato no convierte automáticamente al estrato del diseño completo en solitario; indica por qué deben conservarse también las UPM con contribución cero.

## Relación con la evaluación predictiva

Este análisis usa el dominio anual completo para responder la pregunta descriptiva poblacional. No abre el archivo `prueba_reservada.csv`, no calcula desempeño predictivo y no modifica la lista de predictores, los pliegues, la semilla ni el futuro umbral de clasificación. Las tasas agregadas no se utilizarán para optimizar un modelo.

La tasa descriptiva total de 68,9 % no coincide necesariamente con el 69,5 % ponderado observado previamente en entrenamiento: tienen denominadores y propósitos distintos. El primero usa todo el dominio e incluye empleo no clasificado; el segundo describe la etiqueta disponible en la partición de desarrollo.

## Productos

`src/04_analisis_bivariado.py` genera la tabla larga de tasas, una tabla de diferencias, el diagnóstico de diseño, el control del archivo de inferencia y seis figuras en PNG y SVG. El cuaderno `notebooks/05_analisis_bivariado.ipynb` explica el procedimiento. La configuración `config/eda05_bivariado_v1.json` registra referencias y decisiones.

Las figuras utilizan escala de 0 a 100 para las tasas, muestran el total del dominio y declaran que la incertidumbre está pendiente. El gráfico de brechas usa puntos porcentuales y explicita cada referencia.

La siguiente etapa aplicará linealización de Taylor para proporciones y diferencias, usando estrato, UPM y `fexp`, antes de cualquier afirmación sobre significancia o precisión territorial.
