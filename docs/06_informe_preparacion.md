# EDA 03 — Informe de preparación y reserva de prueba

Fecha de cierre: 28 de septiembre de 2026. Proyecto ENEMDU anual 2025. Esta entrega prepara datos; no presenta estimaciones de brechas ni resultados predictivos.

## Productos y población

| Archivo en data/processed | Registros | Variables | Uso |
|---|---:|---:|---|
| personas_tratada_completa.csv.gz | 334 786 | 165 | Muestra completa, conservación del diseño y banderas de dominio |
| dominio_educacion_superior.csv | 39 551 | 165 | PEA de 15 años o más con nivel superior y título reportado |
| ocupados_ingresos.csv | 36 906 | 18 | Análisis secundario de ingresos del dominio ocupado |
| modelado/entrenamiento.csv | 31 502 | 20 | Desarrollo y validación interna |
| modelado/prueba_reservada.csv | 7 791 | 20 | Evaluación final pendiente |

El diccionario `diccionario_base_tratada.csv` define las 165 variables. `esquema_lectura.json` registra tipos, columnas por archivo y lista de predictores. `etiquetas_oficiales.json` conserva las etiquetas y `asignacion_upm.csv` permite reproducir la reserva. Todos son archivos editables; las bases deben regenerarse mediante código, no corregirse manualmente.

## Transformaciones y trazabilidad

Se conservaron los 334 786 registros y las 139 variables originales. Se normalizaron espacios exteriores y vacíos; los identificadores siguen siendo texto. `fexp` se convirtió a número con punto decimal sin cambiar su escala anual. Se incorporaron 26 variables de elegibilidad, resultados, ingresos, etiquetas, agrupación y partición. No hubo imputaciones, recorte de ingresos ni eliminación de revisitas.

El flujo acumulado es: 334 786 registros originales; 266 889 con edad conocida de al menos 15 años; 169 445 económicamente activos; 50 863 con nivel superior reportado; 39 551 con título. La educación superior completada se operacionaliza con `p10a` en 8, 9 o 10 y `p12a=1`. El nivel reportado no necesariamente identifica el nivel del título más alto completado; esa distinción debe conservarse en la interpretación.

Para el resultado descriptivo, `condact=1` representa empleo adecuado y las restantes categorías de PEA, ausencia de empleo adecuado. Los 258 casos de empleo no clasificado (`condact=6`) permanecen en ese denominador; se excluyen de la etiqueta principal del modelo por su clasificación laboral incompleta. Quedan 39 293 registros para modelado.

La edad 98 representa 98 años o más: se registra como límite inferior y se acompaña de una bandera. El código 99 se trata como edad no informada. En ingresos se preserva el campo original y se crea un monto no negativo utilizable: −1 (gasta más de lo que gana) y 999999 (no informa) no se convierten en cantidades monetarias. Los ceros declarados permanecen en cero. Entre 36 906 ocupados del dominio hay 35 080 montos utilizables; los faltantes y códigos especiales no se imputan. Los vacíos de trabajadores no remunerados se distinguen de los demás vacíos.

## Reserva por grupos y validación interna

La configuración fija `config/preparacion_v1.json` precede al análisis predictivo. Se ordenaron las UPM de cada estrato mediante SHA-256 de la semilla 20250928, el propósito de la partición y su código. Se seleccionó aproximadamente 20 % de UPM por estrato, redondeando al entero más próximo y manteniendo al menos una en cada conjunto. No se utilizó la etiqueta laboral.

En la muestra completa se reservaron 1 578 de 7 780 UPM; quedaron 6 202 en entrenamiento. En el conjunto de modelado corresponden a 31 502 registros de entrenamiento y 7 791 de prueba. El porcentaje se fija sobre grupos, por lo que no equivale a una división exacta 80/20 de filas. Se asignaron cinco pliegues internos por UPM de entrenamiento, también dentro de estratos y sin usar la etiqueta.

La intersección entre entrenamiento y prueba es **cero** para UPM, vivienda sin mes, hogar sin mes y posición de persona sin mes. También se comprobó la separación de estos grupos entre pliegues. La reconstrucción de identificadores se validó antes de retirar el sufijo mensual. Estas claves no permiten garantizar identidad longitudinal individual cuando alguien cambia de vivienda.

El dominio de entrenamiento abarca 150 estratos y el de prueba 149: el estrato 1321 no tiene casos del dominio en prueba. Se conserva la asignación original y se documenta esta limitación. El balance categórico, revisado una sola vez con proporciones ponderadas y sin ponderar, mostró una diferencia absoluta máxima de 1,444 puntos porcentuales entre las comparaciones realizadas. No se modificó la semilla. Esto no garantiza precisión suficiente en cada grupo ni representatividad completa del conjunto reservado.

No se calcularon métricas predictivas ni tasas de la etiqueta en prueba. Los pesos originales se mantienen; el objetivo y procedimiento de ponderación de las futuras métricas se especificarán antes de evaluar modelos. Los totales de pesos por partición no son nuevas estimaciones de la población nacional.

## Prevención de filtración de información

Los diez predictores permitidos son `edad_limite_inferior`, `edad_98_mas`, `p02`, `p06`, `p07`, `p10a`, `p15`, `prov`, `area` y `mes`. Las etiquetas, ingresos, horas, identificadores, pesos, estratos, UPM y particiones no entran en X. Los archivos de modelado tienen además diez campos de contexto y resultado: no deben pasarse completos a un estimador. El lector `02a_leer_bases.py` separa X, y y contexto.

La base completa conserva variables laborales para auditoría e inferencia, pero conservarlas no autoriza usarlas como predictores. Las futuras transformaciones que aprendan de los datos se ajustarán dentro de los pliegues de entrenamiento. La prueba se utilizará una vez fijadas las decisiones de modelado.

## Verificación y reproducción

`02b_verificar_bases.py` contrastó las 139 columnas originales en las 334 786 filas, admitiendo únicamente las normalizaciones documentadas y tolerancia numérica de lectura para el peso. Verificó las huellas de los cinco productos, esquemas, unicidad de claves, pesos positivos, población, etiquetas, ingresos y separación de grupos; reprodujo independientemente la asignación de UPM. Resultado: **verificado**. Evidencia en `reports/preparacion/10_verificacion_bases.json`; bitácora por variable en `01_bitacora_transformaciones.csv` y manifiesto en `08_manifiesto_productos.csv`.

Orden de reproducción: ejecutar `src/02_preparar_base.py`, luego `src/02b_verificar_bases.py` y finalmente el cuaderno `notebooks/03_preparacion_base_y_particion.ipynb`. El programa `02c_crear_cuaderno_preparacion.py` reconstruye el cuaderno didáctico. Cada línea ejecutable de los programas y celdas incorpora comentario explicativo, además de encabezados de etapa, archivo y bloque.

Los CSV tratados usan coma, punto decimal y UTF-8 con BOM. Utilizar el lector con tipos explícitos; para importación en hojas de cálculo, declarar los identificadores como texto. El archivo comprimido se lee directamente con pandas. La inferencia de dominios requiere conservar el diseño de la muestra completa; filtrar filas no basta para especificar correctamente sus varianzas.

## Sustento documental

Las definiciones e identificadores proceden de la [guía oficial ENEMDU anual 2025](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Guia_de_usuario_BDD_ENEMDU_anual_2025.pdf), tablas 12, 14 y 16, y del [diseño muestral anual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Disenio_Muestral_ENEMDU_Anual_enero-diciembre_2025.pdf). Los códigos se contrastaron con las etiquetas de la [base oficial SPSS](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/1_BDD_ENEMDU_2025_SPSS.zip) y los formularios mensuales, documentados en el informe EDA 02. La partición, selección de predictores y tratamiento analítico son decisiones de este proyecto, no instrucciones del INEC.

Siguiente etapa: EDA univariado. Las decisiones predictivas se basarán en entrenamiento y los descriptivos anuales se distinguirán explícitamente de la evaluación predictiva.
