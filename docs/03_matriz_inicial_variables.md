# Matriz inicial de variables

Versión 1.0 — 27 de septiembre de 2026.

**Actualización posterior:** la auditoría EDA 02 contrastó los códigos con el SPSS oficial y las preguntas educativas de los doce meses. Los resultados y decisiones que actualizan esta matriz están en el [informe de calidad](04_informe_calidad.md). En particular, edad 98 significa 98 y más, edad 99 significa no informa; ingrl=-1 indica gasto superior al ingreso e ingrl=999999 indica no información.

**Etapa:** operacionalización inicial. **Función del archivo:** conectar cada concepto con una columna observable, una regla de uso y controles de calidad. Las variables originales incluidas abajo fueron localizadas en el diccionario anual y en el encabezado del CSV. Las variables derivadas son propuestas del proyecto y aún no constituyen una base tratada.

**Cómo leerla:** variable es una característica medida; código es su nombre en el archivo; operacionalizar significa indicar exactamente cómo mediremos el concepto. Una columna disponible no se convierte automáticamente en un predictor autorizado.

Los identificadores S1–S6 remiten a las fuentes enlazadas al final y detalladas en la [ficha de delimitación](02_ficha_delimitacion.md).

## A. Población y resultado

| Concepto / código | Tipo y papel | Definición o regla inicial | Control / límite | Fuente |
|---|---|---|---|---|
| Edad / `p03` | Cuantitativa, años; selección y predictor | Elegibilidad desde 15 años; conservar edad continua en modelos | Revisar extremos y códigos especiales; no imponer relación lineal sin evaluación | S1, fila 15; S4 |
| Nivel de instrucción / `p10a` | Categórica; selección y predictor candidato | 8 = superior no universitario; 9 = superior universitario; 10 = posgrado | Indica nivel cursado/aprobado según pregunta, no garantiza culminación de ese nivel | S1, fila 23; S2, pregunta 10 |
| Año aprobado / `p10b` | Cuantitativa discreta; verificación educativa | Mantener para evaluar coherencia con el nivel | No usar un umbral arbitrario de años como prueba de titulación | S1, fila 24; S3, p. 65 |
| Algún título superior / `p12a` | Binaria; selección | 1 = sí; 2 = no. Exigir 1 y nivel compatible | Distinguir título declarado de validación administrativa; vacíos fuera del flujo pueden ser estructurales | S1, fila 26; S2, pregunta 12; S3, p. 69 |
| Título obtenido / `p12b` | Código nominal; validación y posible ampliación | Identifica el título reportado; revisar catálogo antes de agrupar | No inventar equivalencias ni clasificar campos de estudio sin catálogo | S1, fila 27; S3, p. 69 |
| Condición de actividad / `condact` | Categórica; selección y resultado | PEA: 1–8; empleo adecuado: 1; subempleo: 2–3; desempleo: 7–8; inactividad: 9 | No incluir como predictor; separar categoría 6 de empleo no clasificado | S1, fila 130; S4 |
| Dominio de estudio / `elegible` (derivada) | Indicador booleano; selección | Edad ≥15, nivel 8–10, título =1 y condición 1–8 | Llevar una cuenta de exclusiones y elegibilidad desconocida; preservar diseño completo para inferencia de dominio | S2–S5; decisión del proyecto |
| Empleo adecuado descriptivo / `adecuado_descriptivo` (derivada) | Binaria; indicador descriptivo | 1 si condact=1; 0 si condact=2–8, exclusivamente en PEA elegible | Etiqueta: pertenencia a categoría oficial de empleo adecuado; 0 no equivale siempre a inadecuación comprobada | S4; decisión del proyecto |
| Etiqueta predictiva / `y_adecuado` (derivada) | Binaria; resultado de modelos | Propuesta: 1 si condact=1; 0 si condact en 2–5,7–8; condact=6 no etiquetado en análisis principal | Documentar sensibilidad con código 6 y cambio de denominador; nunca convertir condact faltante en 0 | S4; decisión del proyecto |

## B. Características para descripción y ajuste

| Concepto / código | Tipo y papel | Uso inicial | Control / límite | Fuente |
|---|---|---|---|---|
| Sexo / `p02` | Categórica; comparación principal y predictor | Comparar categorías registradas en encuesta | Verificar etiquetas antes de recodificar; no equiparar automáticamente con género | S1, fila 14 |
| Provincia / `prov` | Categórica nominal; territorio y predictor | Comparación territorial y filtro | Conservar códigos; vincular catálogo oficial; estimar precisión de cada dominio | S1, fila 136 |
| Área / `area` | Categórica nominal; territorio y predictor | Urbano/rural con etiquetas verificadas | No confundir residencia con ubicación laboral | S1, fila 7; S2 |
| Estado civil / `p06` | Categórica nominal; ajuste candidato | Evaluar inclusión con justificación conceptual | Revisar categorías y faltantes; asociación no implica causalidad | S1, fila 19 |
| Autoidentificación étnica / `p15` | Categórica nominal; descripción y ajuste candidato | Describir diversidad y evaluar diferencias con precisión suficiente | Evitar agrupaciones sin justificación y resultados de celdas pequeñas | S1, fila 28; S2, pregunta 15 |
| Asistencia a clases / `p07` | Binaria; descripción y ajuste candidato | Distinguir titulados que continúan estudiando | No excluir estudiantes titulados; la relación con empleo puede ser simultánea | S1, fila 20; S3, p. 65 |
| Parentesco / `p04` | Categórica nominal; candidato secundario | Describir posición en el hogar | Justificar antes de ajustar; puede reflejar circunstancias simultáneas al empleo | S1, fila 16 |
| Mes / `mes` | Categórica temporal; auditoría y posible ajuste | Comprobar presencia de doce meses y efectos estacionales | Evaluar interpretación de ajustes temporales y partición; no usar el mes para mezclar unidades repetidas | S1, fila 145 |
| Nivel agregado / `nnivins` | Categórica; contraste de consistencia | Comparar con p10a y reglas oficiales | No duplicar innecesariamente dos versiones de educación en el modelo | S1, fila 127 |

Las covariables candidatas no constituyen todavía una especificación final. Seleccionaremos un conjunto principal pequeño con fundamentos conceptuales antes de consultar la prueba de modelos. La agrupación por nivel se llamará nivel educativo reportado; no se presentará como grado más alto completado sin validar `p12b` y su catálogo.

## C. Diseño muestral e identificadores

| Concepto / código | Tipo y papel | Uso inicial | Control / límite | Fuente |
|---|---|---|---|---|
| Factor de expansión / `fexp` | Numérica positiva; ponderación | Estimaciones poblacionales y métricas ponderadas cuando corresponda | Revisar valores finitos y positivos, escala anual y extremos; no es predictor | S1, fila 126; S5 |
| Estrato / `estrato` | Identificador nominal; diseño | Estimación de varianzas de la encuesta | Conservar como categoría, no como magnitud; revisar estratos con una sola UPM | S1, fila 125; S5 |
| UPM / `upm` | Identificador nominal; conglomeración | Varianzas y evaluación de agrupación para validación | Verificar relación con estrato; no predictor | S1, fila 140; S5 |
| Vivienda / `id_vivienda` | Identificador; trazabilidad | Revisar repeticiones y agrupación de registros | No publicar registros individuales ni usar como predictor | S1, fila 141 |
| Hogar / `id_hogar` | Identificador; trazabilidad | Prevenir mezcla de hogares entre entrenamiento y prueba | Verificar estabilidad entre meses; identificador único por registro no garantiza identidad longitudinal | S1, fila 142 |
| Persona / `id_persona` | Identificador; trazabilidad | Auditar unicidad y repetición | No eliminar observaciones solo por repetición sin revisar periodo y diseño | S1, fila 143 |
| Periodo / `periodo` | Identificador temporal; auditoría | Validar correspondencia con base anual y mes | No interpretar sin observar formato y documentación | S1, fila 144 |
| Identificadores componentes / `ciudad`, `conglomerado`, `panelm`, `vivienda`, `hogar`, `p01` | Códigos nominales; auditoría | Contrastar identificadores y estructura del panel | Preservar ceros iniciales; no formar claves longitudinales sin verificar su significado | S1, filas 8–13 |

## D. Ingresos y exclusiones de predictores

| Variable o grupo | Uso permitido inicialmente | Razón de exclusión del modelo principal | Fuente |
|---|---|---|---|
| `ingrl` | Resultado secundario en ocupados | Ingreso laboral vinculado a la definición de empleo adecuado | S1, fila 128; S2, módulo laboral |
| `ingpc`, `pobreza`, `epobreza` | Descripción secundaria, si se justifica | Pueden incorporar ingresos del propio trabajo y filtrar información del resultado | S1, filas 129,138–139; decisión del proyecto |
| `p24`, `p27`, `p28`, `p51a`, `p51b`, `p51c` | Auditoría de clasificación laboral | Horas, deseo y disponibilidad relacionados con construcción del resultado | S1, filas 36,39–40,75–77; S2 |
| `p63`–`p70b` presentes en el diccionario | Análisis de ingresos y revisión de consistencia | Componentes de ingresos laborales y pagos en especie | S1, filas 88–98 |
| `empleo`, `desempleo`, `condact` | Selección, resultados y validación de indicadores | Revelan directamente situación laboral que se desea clasificar | S1, filas 130–132; S4 |
| `p20`–`p39` presentes en el diccionario | Auditoría del flujo ocupacional | Trabajo, búsqueda, disponibilidad e inactividad revelan partes de la condición laboral | S1, filas 32–51; S2 |
| `secemp`, `rama1`, `grupo1`, `p40`, `p41`, `p42`, prestaciones y seguridad social | Eventual estudio descriptivo separado de ocupados | Disponibilidad selectiva y relación directa con empleo; ausencias pueden revelar desempleo | S1, filas 52–68,87,133–135; decisión del proyecto |

La exclusión se implementará mediante una lista explícita de predictores permitidos. No bastará con retirar unas pocas columnas de ingreso y horas, dejando entrar el resto automáticamente.

## E. Indicadores previstos y denominadores

| Indicador | Numerador | Denominador | Unidad |
|---|---|---|---|
| Tasa de empleo adecuado | Suma de fexp en elegibles con condact=1 | Suma de fexp en PEA elegible | Porcentaje |
| Tasa de subempleo | Suma de fexp en elegibles con condact=2 o 3 | Suma de fexp en PEA elegible | Porcentaje |
| Tasa de desempleo | Suma de fexp en elegibles con condact=7 u 8 | Suma de fexp en PEA elegible | Porcentaje |
| Brecha entre grupos | Diferencia entre dos tasas comparables | Cada tasa usa su propio dominio elegible | Puntos porcentuales |
| Distribución de ingresos | Valores válidos de ingrl entre ocupados elegibles | Dominio de ocupados con ingreso utilizable, explicitando faltantes | Dólares; periodicidad por confirmar antes del análisis |
| Tamaño observado | Número de registros incluidos | No aplica | Registros sin ponderar |

Las tres tasas laborales mostradas no suman necesariamente 100 %, porque existen otras categorías de empleo. Los intervalos no se calcularán con fórmulas de muestreo aleatorio simple: requieren diseño complejo.

## F. Fuentes y verificaciones pendientes

- **S1:** [Diccionario anual oficial](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Diccionario_de_variables.zip), archivo de personas, hoja `Hoja1`. Aporta nombres y descripciones; no contiene un catálogo completo de todos los valores.
- **S2:** [Formulario diciembre 2025](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/Diciembre_2025/202512_Formulario_ENEMDU.pdf), preguntas 10, 12 y módulos laborales.
- **S3:** [Manual diciembre 2025](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/Diciembre_2025/202512_Manual_del_encuestador_ENEMDU_Diciembre_2025.pdf), páginas 65 y 69 del PDF.
- **S4:** [Sintaxis anual oficial](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Sintaxis_anual_2025.zip), archivo `00 Indicadores de Mercado Laboral.sps`.
- **S5:** [Diseño muestral anual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Disenio_Muestral_ENEMDU_Anual_enero-diciembre_2025.pdf).
- **S6:** [Microdatos anuales](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip), encabezado y auditoría estructural en [reporte local](../reports/00_verificacion_fuentes.json).

Antes de crear la base tratada: verificar instrumentos de otros meses, etiquetas completas de covariables, catálogo de títulos, formatos numéricos, ingresos y códigos especiales, pesos e identificadores. No completar etiquetas faltantes por intuición.
