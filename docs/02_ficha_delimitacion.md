# Ficha de delimitación de la investigación

Versión 1.0 — 27 de septiembre de 2026.

**Actualización posterior:** la auditoría EDA 02 ya verificó las preguntas educativas en los doce formularios y auditó identificadores, códigos y diseño. Véase el [informe de calidad](04_informe_calidad.md), que actualiza las verificaciones pendientes de esta ficha y precisa los códigos de edad 98 y 99.

**Etapa:** delimitación y viabilidad. **Función del archivo:** fijar qué estudiaremos, en quiénes y con qué límites. La ficha está sustentada documentalmente y tiene una comprobación estructural inicial en los microdatos; no sustituye el EDA ni el protocolo estadístico definitivo.

## 1. Identificación y propósito

**Título de trabajo:** Brechas de empleo adecuado en personas con educación superior completada en Ecuador: un análisis estadístico y de aprendizaje automático interpretable con ENEMDU 2025.

**Finalidad inmediata:** trabajo final de la asignatura de Python para Ciencia de Datos e IA, con dashboard y código explicado para un investigador de nivel inicial.

**Proyección:** preparar una investigación reproducible que pueda desarrollarse posteriormente como artículo científico. La contribución y los resultados deberán evaluarse antes de seleccionar una revista.

**Definición operativa del título:** en este estudio, educación superior completada se identificará por la declaración de haber obtenido algún título superior. No se afirmará que se verificó una credencial en un registro administrativo, ni que la persona necesariamente completó el nivel más alto que reporta haber cursado.

## 2. Problema y pregunta

El problema que se investigará es la posible desigualdad en la situación laboral adecuada dentro de una población que ya obtuvo educación superior. La existencia, dirección y magnitud de esas brechas son cuestiones empíricas; no se dan por demostradas antes del análisis.

**Pregunta principal:** ¿Qué características se asocian con tener empleo adecuado entre las personas económicamente activas con educación superior completada en Ecuador durante 2025, y cómo se compara el desempeño de un modelo de aprendizaje automático con el de una regresión logística para clasificar esa situación?

**Objetivo general:** analizar brechas y asociaciones sociodemográficas y territoriales del empleo adecuado en dicha población, y comparar la discriminación, calibración y errores fuera de muestra de los modelos.

**Hipótesis de trabajo:** existen diferencias por sexo y territorio; algunas diferencias persisten tras el ajuste por covariables justificadas; un modelo de árboles o boosting puede mejorar la clasificación frente a la logística. La tercera hipótesis también puede ser rechazada: una mejora no está garantizada.

## 3. Delimitación

| Dimensión | Decisión |
|---|---|
| Enfoque | Cuantitativo, con análisis de datos secundarios |
| Diseño | Observacional transversal sobre una base anual agregada de encuesta compleja; verificar repeticiones de unidades |
| Alcance | Descriptivo, asociativo y de clasificación contemporánea |
| Territorio | Ecuador; provincias y áreas urbana/rural según disponibilidad y precisión efectiva del dominio analizado |
| Periodo | Enero a diciembre de 2025; la base anual no equivale a la encuesta de diciembre |
| Unidad conceptual | Persona de la población elegible |
| Unidad del archivo | Registro de persona en un levantamiento; no asumir que cada fila representa una persona distinta a lo largo del año |
| Población principal | PEA de 15 años o más con declaración de título superior y nivel educativo compatible |
| Fuente | Base oficial de personas ENEMDU anual 2025, con documentación del INEC |
| Resultado principal | Pertenecer a la categoría oficial de empleo adecuado/pleno |
| Análisis secundario | Ingresos laborales entre personas ocupadas del mismo dominio educativo |
| Producto aplicado | Dashboard Python de resultados agregados, con denominadores y precisión visibles |

## 4. Regla de elegibilidad documentada

La propuesta de selección exige simultáneamente:

1. `p03 >= 15`: edad mínima para los indicadores laborales del estudio.
2. `p10a` en `{8, 9, 10}`: superior no universitario, superior universitario o posgrado.
3. `p12a == 1`: declaración de haber obtenido algún título superior.
4. `condact` en `{1, 2, 3, 4, 5, 6, 7, 8}`: pertenencia a la PEA según la sintaxis oficial.

La pregunta 12 del formulario y su explicación en el manual sustentan el uso de titulación. El manual indica registrar el último título superior obtenido. El diccionario anual identifica `p12a` y `p12b`; ambas columnas están presentes en el CSV anual. [S1–S4]

**Casos que requieren cuidado:** una persona titulada que estudia otra carrera sigue siendo elegible; `p07` (asistencia) no se utilizará para excluirla. Una persona con posgrado cursado y título universitario previo puede ser elegible, sin que ello demuestre que terminó el posgrado. Los años aprobados por sí solos no reemplazan la declaración de título. [S2–S3]

**Exclusiones:** menores de 15 años, personas económicamente inactivas, quienes no declaran título superior y registros cuya elegibilidad no pueda establecerse. Un valor desconocido se registrará como desconocido y su exclusión quedará contabilizada; no se convertirá automáticamente en una respuesta negativa.

**Límite de la definición:** egreso sin titulación y titulación no son equivalentes. La población operativa corresponde a personas con algún título superior declarado, no a todas las personas que posiblemente terminaron materias. Esta precisión se conservará en el informe y el dashboard.

## 5. Resultado y denominador

Para la tasa descriptiva oficial, el numerador corresponde a `condact == 1` y el denominador a la PEA elegible, con los factores de expansión. La sintaxis identifica subempleo con 2–3, desempleo con 7–8 y empleo con 1–6. [S4]

El código 6 significa empleo no clasificado. Se conservará en el denominador descriptivo oficial. Para la clasificación predictiva se documentará por separado: no es prueba inequívoca de empleo inadecuado. Se propone excluirlo de la etiqueta principal de entrenamiento y realizar un análisis de sensibilidad que lo incluya como categoría distinta de empleo adecuado. La evaluación predictiva tendrá, por ello, un denominador explícito diferente cuando corresponda.

## 6. Comprobación inicial realizada

El programa `src/00_verificar_fuentes.py` verificó el ZIP mediante CRC y registró su huella SHA-256. Encontró **334 786 registros y 139 columnas** en la base de personas. Los nombres de columnas coinciden con los 139 campos del diccionario anual. Hay registros en los doce meses.

La regla preliminar de elegibilidad identifica **39 551 registros candidatos**. Son filas sin ponderar, no personas únicas ni población expandida. En los niveles 8–10 se observaron respuestas 1 o 2 para `p12a`, sin vacíos ni otros códigos. Esto demuestra disponibilidad estructural, no valida todavía la exactitud de todas las respuestas.

Evidencia reproducible: [reporte de comprobación](../reports/00_verificacion_fuentes.json). La auditoría completa de duplicados, identificadores, pesos, consistencia y diseño queda para el EDA.

## 7. Límites y próximos controles

- Verificar la equivalencia de la pregunta educativa en los instrumentos de los demás meses; el formulario y manual consultados corresponden a diciembre de 2025 y el diccionario corresponde a la base anual.
- No interpretar sexo registrado como identidad de género, ni territorio de residencia como ubicación del puesto de trabajo.
- No usar ingresos, horas, condición de actividad ni variables que revelen esa condición como predictores del resultado.
- Auditar la repetición de personas, hogares y viviendas antes de separar entrenamiento y prueba.
- Incorporar `fexp`, `estrato` y `upm` en la estimación de incertidumbre según el diseño anual. [S5]
- No inferir causalidad ni pronosticar automáticamente el empleo futuro de una persona.

## 8. Fuentes oficiales y localizadores

- **S1. INEC. Diccionario de variables ENEMDU anual 2025.** Archivo `Diccionario de Datos_persona_anual_2025.xlsx`, hoja `Hoja1`: filas 23–27 (educación), 125–145 (variables derivadas, diseño e identificadores). [Descarga oficial](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Diccionario_de_variables.zip).
- **S2. INEC. Formulario ENEMDU diciembre 2025.** Páginas 3–4 del PDF, preguntas 10 y 12. [Formulario](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/Diciembre_2025/202512_Formulario_ENEMDU.pdf).
- **S3. INEC. Manual del encuestador, diciembre 2025.** Página 65 del PDF, instrucciones educativas y segunda carrera; página 69, pregunta 12 y último título superior obtenido. [Manual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/Diciembre_2025/202512_Manual_del_encuestador_ENEMDU_Diciembre_2025.pdf).
- **S4. INEC. Sintaxis anual 2025.** Archivo `00 Indicadores de Mercado Laboral.sps`, bloque de construcción de variables de mercado laboral. [Sintaxis](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Sintaxis_anual_2025.zip).
- **S5. INEC. Diseño muestral ENEMDU anual enero–diciembre 2025.** Capítulos de diseño, factores de expansión y estimación de errores; tabla 11 de declaración muestral. [Diseño anual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Disenio_Muestral_ENEMDU_Anual_enero-diciembre_2025.pdf).
- **S6. INEC. Microdatos CSV ENEMDU anual 2025.** Archivo `BDDenemdu_personas_2025_anual.csv`. [Microdatos](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip).

Fuentes descargadas el 27 de septiembre de 2026. Las copias locales están en `data/raw`; los originales se conservan sin editar.
