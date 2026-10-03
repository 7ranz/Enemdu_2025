# Decisión de uso de modelos en el dashboard

## Modelo presentado primero

La regresión logística será la vista predeterminada. En prueba obtuvo ROC-AUC 0,674, pendiente de calibración 0,930 y exactitud balanceada 0,632. Su comportamiento es más fácil de explicar mediante asociaciones y probabilidades ajustadas.

## Comparador de IA

El boosting permanecerá disponible como comparador. Obtuvo ROC-AUC 0,684 y PR-AUC 0,824, pero la ventaja frente a la logística no fue concluyente y su pendiente de calibración fue 0,761.

## Contenido del panel de modelos

- ROC-AUC, PR-AUC, Brier y calibración con intervalos.
- Sensibilidad, especificidad, precisión y exactitud balanceada con los umbrales congelados.
- Resultados por sexo y área, con tamaños de muestra visibles.
- Importancia por permutación del desarrollo, identificada como interpretación predictiva y no causal.
- Razones de momios de la regresión asociativa, separadas de la evaluación predictiva.

## Lenguaje recomendado

“El modelo de árboles mostró una ventaja puntual pequeña en discriminación, sin evidencia concluyente de mejora frente a la regresión logística. Ambos modelos presentaron diferencias de sensibilidad por sexo y área con un umbral global.”

## Restricciones

El dashboard no calculará predicciones individuales ni recomendará decisiones laborales. Los controles de umbral se etiquetarán como escenarios exploratorios y no modificarán los resultados principales congelados.
