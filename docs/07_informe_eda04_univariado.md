# EDA 04 — Informe de análisis exploratorio univariado

Fecha de cierre: 28 de septiembre de 2026. Este informe describe distribuciones, frecuencias y valores faltantes. No estima asociaciones ajustadas, efectos causales ni desempeño predictivo.

## Alcance analítico

Las covariables se describieron en las 39 551 observaciones del dominio: personas de 15 años o más, económicamente activas, con nivel superior reportado y título. Se presentan conteos muestrales y composiciones ponderadas con `fexp`. El análisis secundario de ingresos parte de 36 906 ocupados del dominio.

La etiqueta de empleo adecuado se examinó únicamente en las 31 502 observaciones de entrenamiento. El archivo de prueba reservada no fue leído por el programa. Su resultado, prevalencia y métricas continúan ocultos para evitar que las decisiones exploratorias se adapten a la evaluación final.

Los porcentajes son descriptivos. Aunque emplean `fexp`, todavía no incorporan la varianza del diseño complejo mediante estratos y UPM; por eso no se presentan intervalos de confianza ni pruebas de hipótesis en esta etapa.

## Resultados principales

Las diez covariables preespecificadas y el factor de expansión no tienen valores faltantes dentro del dominio. Este resultado se limita a esos campos y no implica que la base completa carezca de ausencias.

La edad media ponderada es 39,06 años y la mediana ponderada, 37 años. La distribución se concentra entre 25 y 44 años y tiene una cola hacia edades mayores. El código 98 representa 98 años o más y se trata como categoría abierta, no como una edad exacta.

La composición ponderada es 54,9 % mujeres y 45,1 % hombres; 85,8 % reside en el área urbana y 14,2 % en la rural. El nivel de instrucción reportado se distribuye en 64,6 % superior universitario, 19,7 % superior no universitario y 15,8 % posgrado. Estos porcentajes describen el dominio definido y no toda la población ecuatoriana con estudios superiores.

La autoidentificación mestiza concentra 92,2 % ponderado. Le siguen indígena (3,5 %), montuvia (1,4 %), afroecuatoriana (1,0 %), blanca (1,0 %), negra (0,6 %), mulata (0,4 %) y otra (menos de 0,1 %). Las categorías pequeñas pueden producir estimaciones o métricas inestables; cualquier agrupación futura deberá justificarse sustantivamente y declararse antes de evaluar modelos.

En estado civil, las mayores proporciones ponderadas corresponden a soltero/a (36,6 %) y casado/a (35,1 %), seguidas por unión libre (15,8 %). El 96,6 % no asiste actualmente a clases. La participación mensual ponderada oscila entre 7,5 % y 9,1 %, sin meses ausentes; esto confirma cobertura, pero no constituye todavía un análisis de estacionalidad.

## Diagnóstico del resultado en entrenamiento

En entrenamiento, 22 140 registros tienen empleo adecuado y 9 362 no adecuado. Las proporciones son 70,3 % y 29,7 % sin ponderar, y 69,5 % y 30,5 % ponderadas. Son características del conjunto de desarrollo, no estimaciones nacionales.

La clase mayoritaria representa cerca de 70 %. Por ello, la exactitud por sí sola puede ser engañosa: un clasificador trivial que predijera siempre la clase mayoritaria alcanzaría una exactitud aparente semejante. La evaluación deberá añadir sensibilidad, especificidad, ROC-AUC, PR-AUC, calibración y métricas por grupos.

## Ingresos laborales

De los 36 906 ocupados, 34 656 declaran un monto positivo y 424 un cero real. En conjunto, 35 080 poseen un monto monetario utilizable. Los demás estados se mantienen separados: 981 vacíos de trabajadores no remunerados, 431 vacíos de otros ocupados, 268 códigos de no información y 146 casos que declaran gastar más de lo que ganan.

Entre los montos utilizables, la mediana ponderada es USD 778, la media ponderada USD 931,64 y los cuartiles ponderados USD 475 y USD 1 120. El percentil 90 es USD 1 750; el 95, USD 2 216; y el 99, USD 4 000. El máximo observado es USD 30 000. La media mayor que la mediana y la distancia entre los percentiles altos muestran asimetría a la derecha. No se imputaron ni recortaron extremos; el gráfico utiliza tramos explícitos e incluye ceros.

Los ingresos siguen excluidos de los predictores de empleo adecuado porque participan en su definición operativa. Se reservarán para el análisis secundario entre ocupados.

## Productos y reproducibilidad

El programa `src/03_analisis_univariado.py` genera nueve tablas CSV, seis figuras PNG a 200 dpi y las mismas seis figuras en SVG editable. Cada gráfico muestra fuente, denominador, ponderación y limitación inferencial. Se usa una paleta distinguible para formas comunes de daltonismo, barras con origen cero y categorías sin perspectiva tridimensional.

El cuaderno `notebooks/04_analisis_exploratorio_univariado.ipynb` guía la lectura para un nivel inicial de Python. El archivo `config/eda04_univariado_v1.json` registra el alcance y las decisiones. `reports/eda04_univariado/09_manifiesto_productos.csv` conserva tamaños y huellas SHA-256, y `10_verificacion_eda04.json` documenta los controles automáticos.

Las tablas que alimentan cada figura se conservan por separado. Esto permite modificar títulos o estilo sin recalcular ni copiar valores manualmente. Los programas y las celdas ejecutables incorporan comentarios de etapa, archivo, bloque y línea.

## Límites e implicaciones

La ponderación corrige la contribución desigual de observaciones para descriptivos puntuales, pero no reemplaza el cálculo de incertidumbre con el diseño muestral. Tampoco convierte el conjunto de entrenamiento en una muestra independiente de la población. Las comparaciones entre mujeres y hombres, áreas o territorios pertenecen al análisis bivariado e inferencial.

Las frecuencias pequeñas anticipan un reto para el análisis de equidad: algunas métricas por grupo tendrán alta variabilidad. Antes de modelar se deberán fijar reglas para categorías raras, codificación, valores desconocidos y agrupaciones, aprendiendo cualquier transformación solamente dentro de los pliegues de entrenamiento.

La siguiente etapa será el análisis bivariado: empleo adecuado por sexo, área, nivel educativo, edad y territorio. Se distinguirán estimaciones descriptivas nacionales, incertidumbre ajustada al diseño y diagnósticos propios del entrenamiento.
