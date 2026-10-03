# Protocolo preliminar — versión 0.3

**Actualización EDA 02:** auditoría de calidad, claves y consistencia mensual completada. Se conserva el dominio de 39 551 registros candidatos y se planifica partición predictiva por UPM. Las revisitas anuales se preservan para inferencia. Véase el [informe de calidad](04_informe_calidad.md) para la evidencia, el tratamiento propuesto de 258 casos no clasificados y los códigos especiales de edad e ingreso.

Estado: preferencias registradas y primera operacionalización contrastada con diccionario anual, formulario/manual de diciembre, sintaxis oficial y estructura de microdatos. Consultar la ficha de delimitación y matriz inicial, que detallan la definición por título superior declarado y los controles todavía pendientes.

## Acuerdos confirmados

- Nivel inicial de Python: avanzar con explicaciones conceptuales, ejemplos pequeños, código comentado y verificación de cada resultado.
- Finalidad inmediata: trabajo final de la asignatura de Python para Ciencia de Datos e IA.
- Proyección: desarrollar una investigación que pueda convertirse posteriormente en un artículo científico; la publicabilidad dependerá de la contribución, calidad y resultados, no solo del dashboard.
- No existe plantilla ni reglamento institucional obligatorio.
- Población principal: personas económicamente activas con educación superior completada. No incluir automáticamente a quienes solamente accedieron a ese nivel.
- La culminación debe identificarse mediante evidencia del cuestionario y diccionario. Si no se puede establecer, se informará la limitación y se acordará una reformulación, sin sustituir silenciosamente culminación por acceso.

## Diseño y alcance

Enfoque cuantitativo; estudio observacional de corte transversal basado en datos secundarios de una encuesta compleja anual, con componentes descriptivo, asociativo y de clasificación predictiva. Se verificará la estructura de observaciones repetidas antes de definir las unidades finales de análisis y partición. No se interpretarán asociaciones como efectos causales ni la clasificación contemporánea como pronóstico de empleo futuro.

La IA se utiliza como metodología de análisis; no se estudiará el efecto de usar IA en la universidad.

## Objetivo general

Analizar las brechas de empleo adecuado y sus asociaciones con características sociodemográficas y territoriales en la población económicamente activa con educación superior completada en Ecuador durante 2025, y comparar la capacidad de clasificación de una regresión logística y un modelo de aprendizaje automático interpretable.

## Objetivos específicos

1. Evaluar calidad, cobertura y estructura de los datos y construir una base analítica reproducible.
2. Estimar proporciones ponderadas de empleo adecuado y brechas por sexo y territorio, con incertidumbre compatible con el diseño muestral.
3. Estimar asociaciones ajustadas entre las características preespecificadas y el empleo adecuado.
4. Comparar discriminación, calibración y errores fuera de muestra de modelos base, logística y árboles o boosting.
5. Examinar desempeño y calibración por grupos, atendiendo al tamaño muestral y la incertidumbre.
6. Comunicar los resultados mediante un dashboard científico y documentos editables.

## Hipótesis de investigación propuestas

- H1: la proporción de empleo adecuado difiere por sexo y territorio.
- H2: existen diferencias asociadas con sexo y territorio tras ajustar por edad, nivel educativo y covariables justificadas conceptualmente.
- H3: un modelo de árboles o boosting mejora el desempeño de clasificación fuera de muestra respecto de la regresión logística. La mejora no se da por supuesta: deberá evaluarse junto con su incertidumbre y calibración.

Se definirán comparaciones principales, métrica primaria y diferencia relevante antes del entrenamiento. Los análisis adicionales se etiquetarán como exploratorios y se considerará la multiplicidad de contrastes.

## Población y variables: decisiones pendientes

| Elemento | Propuesta / verificación requerida |
|---|---|
| Edad | PEA de 15 años o más; examinar sensibilidad a un corte adulto si corresponde |
| Educación superior | Completada, por decisión del investigador. Comprobar categorías y preguntas que permitan establecer culminación; no equiparar años aprobados con titulación |
| Resultado | Empleo adecuado según clasificación oficial; documentar códigos y tratamiento de casos sin clasificación |
| Comparación | Resto de la PEA elegible, incluido desempleo; explicitar el denominador |
| Predictores | Edad, sexo registrado, territorio, nivel educativo y otras características justificadas y disponibles en toda la población elegible |
| Exclusiones predictivas | Ingresos, horas, componentes de la clasificación laboral, variables que reproduzcan el resultado y proxies evidentes de la condición laboral |
| Diseño | La guía identifica upm, estrato y fexp; confirmar su uso específico en la base anual y el tratamiento de repeticiones |
| Ingresos | Análisis secundario de personas ocupadas; documentar ceros, faltantes y extremos sin eliminarlos automáticamente |

No asumir que una variable de años aprobados demuestra titulación. No usar como predictores principales variables laborales que solo se observan entre ocupados sin evaluar el sesgo y la información implícita sobre el resultado.

## Plan analítico inicial

**Inferencia:** estimación de dominios conservando la información del diseño completo, proporciones e intervalos, contrastes compatibles con la encuesta y regresión logística con varianzas apropiadas. Presentar probabilidades ajustadas o efectos marginales cuando faciliten la interpretación, además de odds ratios. No reemplazar el diseño complejo por errores estándar convencionales de una logística con pesos.

**Predicción:** reservar prueba por unidades de agrupación justificadas después de auditar identificadores y repetición de personas/hogares. Si los identificadores no permiten garantizar ausencia de solapamiento, documentar el límite y elegir una agrupación más conservadora. Usar validación agrupada dentro de entrenamiento. Comparar un predictor constante basado en prevalencia, logística y un modelo de árboles o boosting. Ajustar hiperparámetros y umbral sin consultar la prueba. Reportar ROC-AUC, precisión positiva, sensibilidad, PR-AUC con definición exacta, Brier y curvas de calibración; documentar métricas ponderadas y no ponderadas. Evaluar incertidumbre respetando agrupación y, según el estimando, diseño muestral. Interpretar importancia de variables sin atribuir causalidad.

**Dashboard:** separar descripción, asociaciones e información de modelos. Exponer denominadores, filtros, tamaños y precisión; no usar filtros provinciales para sugerir representatividad en cualquier cruce arbitrario. Elegir tecnología Python después de precisar volumen de datos y modo de uso local o publicado.

## Estándares de documentación

APA 7 guiará presentación, citas y referencias. STROBE se adaptará como lista de transparencia para el componente observacional transversal, reconociendo su origen epidemiológico; no sustituye el diseño de encuesta ni constituye una certificación de calidad. El componente predictivo tendrá documentación independiente de partición, fuga de información, ajuste, calibración y limitaciones.

## Información pendiente del investigador

- Autoría, afiliación y datos de portada cuando se prepare Word.
- Archivos oficiales de los logos de Facultad de Ciencias, UCETech, Ciencia Central y Universidad Central, o su ubicación verificable, antes de diseñar la presentación final.

## Bitácora inicial

2026-09-27: se crea una carpeta independiente. Se consulta la guía oficial y se identifica la declaración de diseño en su tabla 16. Se propone una ruta didáctica de siete etapas de EDA. No se ha verificado aún el ZIP ni se han calculado indicadores. Las decisiones de población y modelos permanecen provisionales.

2026-09-27, actualización: el investigador confirma nivel inicial de Python, trabajo final de asignatura con proyección a artículo, ausencia de plantilla obligatoria y educación superior completada como criterio de población. Queda pendiente verificar cómo operacionalizar este último criterio en ENEMDU.

2026-09-27, verificación documental: se identifica p12a como declaración de algún título superior y se comprueba su presencia en el CSV anual. Regla inicial: edad >=15, p10a en 8–10, p12a=1 y condact en 1–8. La auditoría encuentra 39 551 registros candidatos, no personas únicas. Se completan ficha de delimitación y matriz inicial. El código condact=6 se mantiene en el denominador descriptivo oficial, pero se propone dejarlo sin etiqueta en el modelo principal y examinarlo en sensibilidad. Los instrumentos de los otros meses y la estabilidad de identificadores quedan pendientes de revisión.
