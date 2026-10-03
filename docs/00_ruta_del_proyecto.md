# Ruta de investigación y productos

## Forma de trabajo

Cada etapa tendrá objetivo, explicación conceptual, archivos editables, ejecución comentada, verificación e interpretación. Se avanzará en entregas pequeñas para que el investigador pueda comprender y reproducir el trabajo. Los productos finales se completarán después de validar los análisis; el protocolo Word podrá empezar antes, identificado como proyecto y sin resultados inventados.

## Fases generales

| Fase | Trabajo | Producto y criterio de cierre |
|---|---|---|
| 0. Delimitación | Población, problema, pregunta, objetivos, hipótesis, alcance | Protocolo preliminar con decisiones explícitas |
| 1. Fundamentación y diseño | Antecedentes verificables, marco conceptual, operacionalización, plan estadístico, ética | Protocolo y matriz de variables; referencias comprobadas |
| 2. Adquisición y auditoría | Descargar, inventariar, validar integridad y documentación | Original preservado, manifiesto de archivos, reporte original |
| 3. EDA y preparación | Siete etapas descritas abajo | Notebooks y base tratada con diccionario y reporte |
| 4. Inferencia | Estimaciones de dominio, brechas, intervalos y asociaciones ajustadas | Tablas y gráficos con diseño muestral y precisión documentados |
| 5. Modelos predictivos | Modelo nulo, logística y árboles/boosting; explicación y validación | Modelos, métricas y evaluación por grupos |
| 6. Dashboard | Filtros, indicadores, comparación, ingresos y modelos | Aplicación Python, manual y verificación contra tablas |
| 7. Comunicación | Redacción, discusión, limitaciones y presentación | Word APA 7, PowerPoint y paquete reproducible |

La fase 7 quedó completada el 1 de octubre de 2026. El informe metodológico integra el diseño, los controles analíticos, los resultados y las referencias; la presentación resume el mismo hilo narrativo en 16 diapositivas editables.

## Las siete etapas del EDA

Esta división es la organización didáctica del proyecto, no una clasificación universal del EDA. La preparación de datos forma parte de este recorrido.

| Etapa / notebook previsto | Pregunta | Salida |
|---|---|---|
| 01. Comprensión e inventario | ¿Qué archivos, unidades, variables y códigos existen? | Inventario, dimensiones, diccionario preliminar y estructura muestral |
| 02. Calidad y estructura | ¿Qué faltantes, duplicados, saltos y valores inválidos hay? | Reporte original y reglas de calidad |
| 03. Preparación y población | ¿Cómo construimos una base analítica justificable? | Reglas de recodificación, flujo de elegibilidad, base tratada y partición de evaluación |
| 04. Exploración univariada | ¿Cómo se distribuyen las variables? | Frecuencias ponderadas, distribuciones y tamaños observados |
| 05. Exploración bivariada | ¿Qué diferencias y relaciones se observan? | Cruces, brechas e intervalos compatibles con el diseño |
| 06. Exploración multivariada | ¿Qué redundancias, interacciones y patrones requieren atención? | Diagnóstico de asociaciones, colinealidad y posibles fugas de información |
| 07. Síntesis y entrega analítica | ¿Qué decisiones y límites quedan documentados? | Reporte EDA final, diccionario definitivo y controles de la base tratada |

La auditoría estructural puede usar toda la base. Tras comprobar las unidades y las posibles repeticiones, se reservará la prueba antes del EDA que guíe selección de variables o modelos. Las estadísticas descriptivas nacionales pueden usar toda la muestra bajo un plan separado; no se emplearán hallazgos de la prueba para ajustar el modelo. Imputación, escalado, selección y ajuste se aprenderán dentro de los subconjuntos de entrenamiento correspondientes.

## Productos comprometidos

1. Dashboard profesional en Python, con archivos fuente, instrucciones y dependencias fijadas.
2. Siete notebooks de EDA y programas auxiliares, comentados por etapa, archivo, bloque y línea ejecutable.
3. Reporte del conjunto original; conjunto tratado en formatos adecuados para análisis e intercambio; diccionario; reporte de transformaciones, exclusiones y calidad.
4. Proyecto e informe Word editables con presentación y referencias APA 7; estructura cuantitativa y guía de transparencia adaptada de STROBE.
5. PowerPoint editable de fondo blanco, con los cuatro logos solicitados en la franja inferior y una ilustración de carátula generada para el estudio. Los gráficos estadísticos conservarán datos o fuentes editables; la ilustración generada será un recurso gráfico rasterizado.
6. Complementos: matriz de operacionalización, bitácora de decisiones, manifiesto de datos, ficha de modelos, manual del dashboard, guía de reproducción y lista de comprobación del reporte.

Los productos finales de comunicación se encuentran en `outputs/final`, y su construcción reproducible está documentada en `docs/16_documento_presentacion_final.md`.

## Verificación transversal

- Comparar indicadores generales reproducidos con publicaciones oficiales antes de interpretar el subgrupo educativo.
- Conservar denominadores explícitos: PEA para las tasas laborales pertinentes y personas ocupadas para ingresos laborales.
- Comprobar pesos, estratos y conglomerados; no confundir ponderar un promedio con estimar correctamente su incertidumbre.
- Mostrar muestra observada, estimación ponderada y precisión; definir reglas para celdas pequeñas o imprecisas antes de publicar el dashboard.
- Verificar que tablas, figuras, dashboard y textos reporten los mismos resultados.
