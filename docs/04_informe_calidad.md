# Informe de calidad, identificadores y consistencia mensual

**ENEMDU anual 2025 · Educación superior y empleo**  
**Etapa:** EDA 02. **Fecha local:** 27 de septiembre de 2026. **Versión:** 1.0.

## 1. Conclusión de la etapa

La base permite continuar con la preparación del dominio de estudio: se mantiene una selección de **39 551 registros candidatos**, con información completa en las nueve variables principales de selección y descripción revisadas. No se detectaron duplicados exactos, claves persona-mes duplicadas ni personas sin correspondencia en la tabla de hogares. Las preguntas educativas examinadas son consistentes entre los doce formularios.

La preparación deberá preservar tres distinciones: observación mensual frente a identidad longitudinal; ausencia estructural frente a no respuesta; y códigos especiales frente a cantidades numéricas. **No se han eliminado ni imputado registros, ni se ha creado todavía la base tratada.**

Esta auditoría recorre todas las filas y columnas de los dos CSV. Aplica controles específicos a las variables del estudio y contrasta 89 dominios categóricos con las etiquetas oficiales. No es una certificación de cada respuesta de campo ni una reconstrucción completa de todos los saltos ocupacionales del cuestionario.

## 2. Fuentes y método

Se utilizaron los microdatos CSV anuales, los diccionarios, la guía de uso, la sintaxis de indicadores, el diseño muestral anual y los doce formularios mensuales del INEC. Se descargó además la versión SPSS anual para recuperar las etiquetas oficiales de valores. Los nombres de las 139 variables de personas coinciden entre CSV, diccionario y SPSS.

La lectura conserva los identificadores como texto y sus ceros iniciales. Los CSV usan punto y coma como separador y coma en valores decimales, incluidos los pesos. Muchas ausencias están escritas como espacios: se registraron en el perfil original y se interpretaron como vacíos en una copia en memoria. El archivo original permanece intacto.

Se ejecutaron 73 reglas estructurales y semánticas, además del contraste de 89 dominios categóricos. Se comprobó la integridad CRC de los ZIP utilizados. La huella SHA-256 del CSV comprimido antes y después de la auditoría es:

`a2dc06b14b84ac2908f59313a70676f9b5c1b697b4780e744452585e60dbcbe8`

Programa principal: [01_auditoria_calidad.py](../src/01_auditoria_calidad.py). Evidencia general: [resumen de auditoría](../reports/calidad/00_resumen_auditoria.json). Las tablas de control contienen denominadores anuales y mensuales.

## 3. Estructura, cobertura y duplicados

| Comprobación | Resultado |
|---|---:|
| Registros de personas | 334 786 |
| Variables de personas | 139 |
| Registros de vivienda-hogar | 104 738 |
| Variables de vivienda-hogar | 35 |
| Meses presentes | 12 |
| Provincias presentes por mes | 24 |
| UPM distintas durante el año | 7 780 |
| Estratos durante el año | 150 |
| Filas exactamente duplicadas, personas | 0 |
| Filas exactamente duplicadas, vivienda-hogar | 0 |
| Repeticiones adicionales de id_persona | 0 |
| Repeticiones adicionales de id_hogar en vivienda-hogar | 0 |
| Personas sin hogar correspondiente | 0 |
| Hogares de vivienda-hogar sin personas | 0 |

La unión personas–hogares se verificó como muchos a uno, sin multiplicar las 334 786 filas. Área, UPM, estrato y factor de expansión coinciden entre ambas tablas en todas las observaciones enlazadas. La cantidad de personas de cada mes oscila entre 27 332 y 28 320; la suma mensual recupera exactamente el total anual.

Tener datos de todas las provincias no garantiza precisión suficiente para cualquier combinación de filtros. Esa evaluación requerirá estimaciones de incertidumbre del dominio correspondiente.

Evidencia: [duplicados](../reports/calidad/04_duplicados.csv), [integridad de la unión](../reports/calidad/06_integridad_personas_hogares.csv) y [cobertura mensual](../reports/calidad/10_cobertura_mensual.csv).

## 4. Identificadores: la unicidad no elimina las revisitas

Se comprobaron en **todas las filas** las siguientes composiciones empíricas:

- `id_vivienda = upm + panelm + vivienda + mes`.
- `id_hogar = upm + panelm + vivienda + hogar + mes`.
- `id_persona = upm + panelm + vivienda + hogar + p01 + mes`.

La suma representa concatenación de texto, no suma aritmética. Los dos caracteres finales identifican el mes. Después de validar esa composición se retiraron exclusivamente en copias auxiliares, para estudiar la repetición de claves.

| Nivel de clave sin mes | Claves distintas | Claves presentes en más de un mes | Máximo de meses por clave |
|---|---:|---:|---:|
| Vivienda | 67 117 | 37 216 | 2 |
| Hogar | 67 408 | 37 330 | 2 |
| Posición de persona en el hogar | 219 778 | 115 008 | 2 |

La diferencia entre 334 786 registros y 219 778 claves de persona sin mes **no autoriza a eliminar 115 008 filas**. Son observaciones de distintos levantamientos, no duplicados exactos. Además, la posición de persona dentro del hogar no prueba identidad individual: entre claves repetidas se encontraron 5 969 pares con cambio de sexo registrado. De 114 913 pares con edades exactas comparables, 25 871 muestran disminución o aumento de más de un año; se excluyeron de esta comparación los códigos 98 y 99. Estas señales pueden reflejar composición del hogar, numeración o respuesta; no demuestran que una persona cambió esas características ni que el INEC duplicó erróneamente sus datos.

**Decisión para modelado:** planificar la partición por UPM completa, conservando juntas sus observaciones mensuales. Es una opción conservadora para reducir dependencia y mezcla de revisitas. Se verificará ausencia de claves de vivienda y hogar compartidas entre conjuntos. No puede garantizarse ausencia de una misma persona que se mudó a otra UPM, porque la base pública no ofrece aquí una identidad individual longitudinal comprobada.

**Decisión para inferencia:** conservar los registros y pesos anuales; no deduplicar la muestra por claves sin mes.

Evidencia: [repetición](../reports/calidad/09_repeticion_sin_mes.csv), [solapamiento de hogares](../reports/calidad/07_solapamiento_id_hogar.csv), [cambios en posiciones de persona](../reports/calidad/08_cambios_claves_persona.csv). La documentación anual describe un diseño con rotación y seguimiento de viviendas; véase la sección de rotación del [diseño muestral](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Disenio_Muestral_ENEMDU_Anual_enero-diciembre_2025.pdf).

## 5. Educación: consistencia entre datos e instrumentos

Se localizaron las preguntas 10 y 12 en los doce formularios mensuales. El texto normalizado de la pregunta de nivel educativo coincide en todos; también coincide el fragmento de titulación, incluida la codificación sí = 1 y no = 2. El cotejo se refiere a esas preguntas, no a la identidad completa de todos los módulos de los cuestionarios.

En la base anual se observaron 71 278 registros con nivel superior reportado y 48 279 con algún título superior declarado. La combinación con edad y PEA produce los **39 551 candidatos**. Los tres recuentos son sin ponderar y pertenecen a universos diferentes.

En el flujo educativo no se detectaron respuestas inválidas de p12a, títulos informados fuera del flujo ni códigos p12b ausentes cuando se declaró un título. En candidatos tampoco se encontraron vacíos en sexo, estado civil, asistencia, nivel, titulación, autoidentificación étnica, provincia, área y año aprobado.

Los vacíos de p12a fuera de los niveles superiores son esperados por el cuestionario y no justifican eliminar las filas de la muestra completa. Tampoco tener un título y estudiar actualmente constituye una contradicción.

Evidencia: [formularios, URL, páginas y huellas](../reports/calidad/formularios_mensuales.json), [reglas y denominadores](../reports/calidad/03_reglas_calidad.csv).

## 6. Códigos, edades y condición laboral

Se contrastaron **89 variables categóricas** del CSV con las etiquetas del SAV oficial de 2025: no se detectaron valores informados fuera de esas etiquetas. Las ausencias se evaluaron por separado. Los indicadores empleo y desempleo son coherentes con condact en las comprobaciones realizadas; periodo y mes también coinciden en todas las filas.

El catálogo confirma dos códigos especiales de edad: **98 significa 98 y más**, y **99 significa no informa**. Hay 224 registros con código 98 y ninguno con 99 en la base completa; por ello, excluir el código de no respuesta no cambia los 39 551 candidatos. La edad 98 debe interpretarse como categoría abierta, no como edad exacta, y no se usó como edad exacta al contrastar pares temporales.

Dentro de la PEA candidata hay **258 registros con condact = 6**, empleo no clasificado. Se conservarán en el denominador descriptivo oficial. El conjunto principal de clasificación, si se mantiene la decisión de dejar esos casos sin etiqueta, contará con **39 293 registros** antes de cualquier otra decisión posterior. No se presentará ese subconjunto como toda la PEA elegible.

Evidencia: [catálogo de valores SPSS](../reports/calidad/14_catalogo_spss_oficial.json), [validación categórica mensual](../reports/calidad/15_validacion_codigos_spss.csv), [resumen de etiquetas](../reports/calidad/17_resumen_etiquetas.json).

## 7. Ingresos: interpretar antes de limpiar

Las etiquetas oficiales de 2025 definen `ingrl = -1` como gasto mayor que ingreso, y `ingrl = 999999` como no informa. El primero no representa una pérdida de exactamente un dólar; el segundo no representa un ingreso extraordinariamente alto.

Entre los **36 906 registros ocupados candidatos** se encontraron:

| Estado de ingreso laboral | Registros | Interpretación |
|---|---:|---|
| Vacío | 1 412 | Se debe revisar por condición laboral; no imputar todo como cero |
| Código -1 | 146 | Gasta más de lo que gana; conservar como estado distinto |
| Código 999999 | 268 | No informa; no usar como cantidad |
| Cero numérico | 424 | Diferenciar de vacío y de códigos especiales |

De los 1 412 vacíos, **981 corresponden a empleo no remunerado** y **431 a subempleo por insuficiencia de tiempo**. De los 268 códigos de no información, **258 corresponden a empleo no clasificado** y **10 a subempleo por insuficiencia de tiempo**. El cruce explica por qué el tratamiento uniforme de vacíos sería incorrecto.

**Decisión:** construir posteriormente una variable de estado del ingreso y otra de cantidad utilizable, sin sustituir -1 ni 999999 por montos ordinarios. La política para vacíos entre empleo no remunerado y el tratamiento de pérdidas se explicarán en el análisis secundario. Los cuantiles sin limpieza del anexo sirven para diagnóstico, no para comunicar resultados salariales del estudio. Los ingresos continúan excluidos de los predictores.

Evidencia: [diagnóstico de ingresos](../reports/calidad/13_diagnostico_ingresos.csv), [ingresos por condición](../reports/calidad/18_ingresos_por_condicion.csv) y etiquetas de la [base SPSS oficial](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/1_BDD_ENEMDU_2025_SPSS.zip).

## 8. Diseño muestral y revisión cartográfica

Todos los factores de expansión revisados son numéricos, finitos y positivos. Cada UPM corresponde a un único estrato, provincia y área en la base anual. No se detectaron estratos con una sola UPM ni en la muestra completa ni al contar UPM con candidatos: los mínimos respectivos son 23 y 4.

Esto no demuestra que todo cruce de filtros sea preciso ni que basten errores estándar convencionales. La estimación posterior deberá mantener el diseño de la muestra completa y tratar la educación superior titulada como dominio.

En **1 787 registros**, el prefijo geográfico de la UPM difiere de la columna ciudad normalizada. En cambio, el prefijo coincide con conglomerado en todas las filas, y no hay contradicción con la provincia. La causa exacta de la diferencia ciudad–UPM no está documentada en los recursos revisados; no se atribuye automáticamente a error o actualización cartográfica.

**Decisión:** preservar la UPM original y usar `prov` para las comparaciones provinciales. No reconstruir la UPM sustituyendo su prefijo por ciudad. Un análisis cantonal o parroquial requeriría resolver primero esas correspondencias.

Evidencia: [dependencias de claves](../reports/calidad/05_dependencias_identificadores.csv), [UPM por estrato](../reports/calidad/11_upm_por_estrato.csv), [diferencias geográficas por mes](../reports/calidad/16_revision_geografia_upm.csv).

## 9. Consistencia mensual de disponibilidad

Se perfilaron las **174 columnas combinadas** de personas y vivienda-hogar, para el año y cada mes: 2 262 combinaciones tabla-variable-periodo. El perfil incluye vacíos, espacios externos, categorías distintas y rangos numéricos aparentes. Un rango numérico de identificador no tiene interpretación cuantitativa.

Las mayores amplitudes mensuales del porcentaje de vacíos aparecen en p26 y p25, con aproximadamente 5,55 y 5,41 puntos porcentuales. Ambas preguntas dependen de horas trabajadas y sus saltos. Son señales para revisar composición y flujo, no pruebas de deterioro de calidad ni de cambio metodológico.

No se usan estas comparaciones para seleccionar predictores ni ajustar modelos. La evaluación de estabilidad predictiva se realizará después de reservar la prueba.

Evidencia: [perfil completo](../reports/calidad/01_perfil_variables_mes.csv), [cambios de disponibilidad](../reports/calidad/02_cambios_disponibilidad.csv), [códigos mensuales](../reports/calidad/12_codigos_por_mes.csv).

## 10. Decisiones para la próxima etapa

1. Mantener originales inalterados y conservar las observaciones anuales repetidas.
2. Normalizar espacios y tipos en columnas de trabajo, preservando códigos e identificadores originales.
3. Crear indicadores de elegibilidad, estado del ingreso y empleo adecuado con reglas explícitas y conteo de exclusiones.
4. Separar conjunto descriptivo, conjunto predictivo etiquetado y dominio de ingresos; documentar sus denominadores.
5. Reservar entrenamiento y prueba por grupos de UPM antes de explorar asociaciones para modelado; evaluar balance y ausencia de claves de vivienda/hogar compartidas.
6. No imputar covariables principales por rutina: no tienen vacíos en el dominio comprobado. Cualquier necesidad posterior se resolverá dentro del entrenamiento.
7. Preservar educación reportada y título declarado como conceptos diferentes; no inferir el nivel más alto completado solo desde p10a.

## 11. Reproducción y fuentes

El [cuaderno ejecutado](../notebooks/02_calidad_identificadores_meses.ipynb) guía la lectura de resultados y permite recalcular la auditoría. Los programas están comentados por etapa, archivo, bloque y línea ejecutable. Las versiones usadas se registran en el resumen y en [requirements_eda.txt](../requirements_eda.txt).

Fuentes principales:

- INEC. [Microdatos anuales CSV](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip) y [SPSS](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/1_BDD_ENEMDU_2025_SPSS.zip), edición 2025.
- INEC. [Guía anual de uso](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Guia_de_usuario_BDD_ENEMDU_anual_2025.pdf), secciones 3.3, 3.5 y 3.7.
- INEC. [Sintaxis anual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Sintaxis_anual_2025.zip), construcción de indicadores laborales.
- INEC. [Diseño muestral anual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Disenio_Muestral_ENEMDU_Anual_enero-diciembre_2025.pdf), rotación, ponderaciones y varianzas.
- INEC. Formularios enero–diciembre 2025, preguntas 10 y 12. Los doce enlaces exactos, páginas y huellas están en [evidencia documental mensual](../reports/calidad/formularios_mensuales.json).
