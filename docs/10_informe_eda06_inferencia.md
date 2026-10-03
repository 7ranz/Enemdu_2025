# EDA 06 — Inferencia con diseño muestral y revisión científica

Fecha de cierre: 30 de septiembre de 2026. Esta etapa incorpora estratos, UPM y el factor anual `fexp` para estimar errores estándar, intervalos de confianza y contrastes. Los resultados siguen siendo asociaciones observacionales.

## Método

La población analítica es la PEA de 15 años o más con nivel superior reportado y título. La tasa de empleo adecuado se estimó como razón entre el total ponderado de personas con empleo adecuado y el total ponderado del dominio o subgrupo.

La varianza se calculó mediante linealización de Taylor. Las influencias individuales se agregaron por UPM y se centraron dentro de los 150 estratos, conservando las 7 780 UPM de la muestra completa. Se utilizó una aproximación con reemplazo, sin corrección por población finita, y 7 630 grados de libertad.

Los intervalos de las proporciones se calcularon en escala logit y se transformaron de regreso a porcentaje. Esto mantiene sus límites entre 0 y 100. Las diferencias se calcularon en escala lineal con distribución t. Su varianza incorpora la covarianza entre grupos que comparten el mismo diseño.

Los cuatro contrastes primarios se definieron antes de revisar la inferencia: mujeres menos hombres, rural menos urbana, superior no universitaria menos universitaria y posgrado menos universitaria. Sus valores p se ajustaron conjuntamente con Holm. Las pruebas globales de Wald evalúan si existe alguna diferencia entre categorías de cada dimensión.

## Tasa total

La tasa ponderada de empleo adecuado es **68,85 %**, con error estándar de 0,66 puntos porcentuales e intervalo de confianza de 95 % de **67,54 % a 70,13 %**.

El intervalo cuantifica incertidumbre del diseño bajo las decisiones declaradas. No incorpora incertidumbre por posibles errores de medición, clasificación laboral, cobertura o definición del dominio.

## Sexo

La estimación para hombres es **72,10 %** (IC 95 %: 70,41–73,73) y para mujeres **66,19 %** (64,51–67,83).

La diferencia mujeres menos hombres es **−5,91 puntos porcentuales** (IC 95 %: −8,01 a −3,81). El valor p ajustado por Holm es menor que 0,001. Los datos respaldan una diferencia estadística en la situación observada. La comparación no prueba que el sexo cause la brecha ni controla otras características.

## Área de residencia

La tasa urbana es **70,41 %** (IC 95 %: 69,04–71,74) y la rural **59,44 %** (55,70–63,07).

La diferencia rural menos urbana es **−10,97 puntos porcentuales** (IC 95 %: −14,90 a −7,05), con valor p de Holm menor que 0,001. Es la mayor brecha primaria negativa en esta etapa. Territorio, estructura productiva, composición educativa y edad pueden contribuir a esta asociación.

## Educación

La tasa para superior no universitaria es **63,91 %** (61,17–66,56); para superior universitaria, **66,28 %** (64,68–67,84); y para posgrado, **85,58 %** (83,43–87,50).

La diferencia superior no universitaria menos universitaria es **−2,37 puntos porcentuales** (IC 95 %: −5,42 a 0,67; p de Holm=0,127). El intervalo incluye cero, por lo que este contraste no aporta evidencia suficiente de diferencia con el umbral de 0,05.

La diferencia posgrado menos universitaria es **19,31 puntos porcentuales** (16,84–21,77; p de Holm<0,001). La asociación es precisa y positiva, pero puede reflejar edad, experiencia, ocupación, sector, territorio y selección hacia el posgrado. `p10a` sigue siendo nivel reportado, no necesariamente el título más alto.

## Edad

La prueba global de Wald muestra heterogeneidad por edad (14 gl; p<0,001). Las tasas aumentan durante la inserción laboral, se mantienen alrededor de 77–79 % entre 35 y 59 años y disminuyen en edades mayores.

Los intervalos confirman la inestabilidad de los extremos. El grupo de 15–19 años tiene 11 observaciones, estimación de 3,00 %, IC 95 % de 0,35 % a 21,24 % y CV de 107,2 %. El grupo de 85–89 tiene 5 observaciones, 12,77 %, IC 95 % de 1,51 % a 58,33 % y CV de 100,5 %. No deben publicarse esos puntos aislados sin agrupar edades o aplicar reglas de supresión justificadas.

## Provincia

La prueba global de Wald aporta evidencia de heterogeneidad provincial (23 gl; p<0,001). Esto significa que al menos parte de las tasas difiere; no demuestra que cada par de provincias sea diferente.

Chimborazo presenta 48,08 % (IC 95 %: 42,99–53,21). Morona Santiago presenta 89,66 %, pero su intervalo es mucho más amplio: 71,52–96,77. Galápagos registra 85,70 % (79,68–90,15) y Zamora Chinchipe 83,66 % (78,83–87,56).

Los intervalos muestran que ordenar únicamente por el punto estimado exagera la certeza territorial. No se realizaron 276 comparaciones provinciales pareadas ni se ajustó esa familia de pruebas. El gráfico debe leerse como perfil descriptivo con incertidumbre, no como ranking.

## Revisión de gráficos

Las figuras actualizadas sustituyen las barras sin incertidumbre por puntos e intervalos de confianza. La línea vertical discontinua indica la tasa total del dominio. Esta forma permite distinguir magnitud, precisión y superposición visual.

Los gráficos de sexo y área muestran intervalos relativamente estrechos y separados. El gráfico educativo muestra la superposición entre superior no universitaria y universitaria, y la separación del posgrado. En edad, los intervalos se amplían en categorías extremas. En provincia, la precisión varía de forma sustancial; los valores amazónicos altos no tienen todos la misma precisión.

El gráfico de contrastes coloca el cero como referencia. Mujeres–hombres, rural–urbana y posgrado–universitaria no cruzan cero. Superior no universitaria–universitaria sí lo cruza, de acuerdo con el contraste tabular.

## Tabla científica

La tabla científica está disponible en CSV y en un libro Excel con cinco hojas: Resumen, Tasas, Contrastes, Pruebas globales y Método. Incluye n, UPM con casos, estratos con casos, estimación, error estándar, IC 95 %, CV, grados de libertad, valores p y ajuste de Holm. Las filas con n menor que 100 permanecen visibles y se marcan para revisión.

El libro se generó a partir de los CSV verificados y no contiene resultados copiados manualmente. Las probabilidades extremadamente pequeñas se mantienen como valores numéricos con formato científico. La hoja Método conserva las fuentes oficiales y las decisiones inferenciales.

## Alcance de las hipótesis

La hipótesis descriptiva de diferencias por sexo y territorio recibe apoyo en los contrastes de sexo y área y en la prueba global provincial. La hipótesis de persistencia después del ajuste todavía no está evaluada: requiere la regresión logística con covariables.

La hipótesis de que un modelo de árboles mejora la predicción tampoco está evaluada. La prueba predictiva sigue reservada porque primero deben construirse y congelarse la regresión logística, el modelo de árboles, el preprocesamiento, los hiperparámetros y el umbral usando entrenamiento y validación interna. Evaluar la prueba antes de completar ese proceso invalidaría su función como evaluación final.

## Productos y verificación

El programa `src/05_inferencia_diseno.py` genera 47 estimaciones con intervalos, cuatro contrastes primarios, cinco pruebas globales y seis figuras en PNG y SVG. `src/05a_preparar_tabla_cientifica.py` prepara la tabla editorial. El cuaderno `notebooks/06_inferencia_diseno.ipynb` documenta el análisis paso a paso.

Los controles reconciliaron puntos con la EDA 05, comprobaron intervalos dentro de 0–100, diferencias con sus tasas componentes, grados de libertad, ejecución del cuaderno, huellas y contenido del libro Excel.
