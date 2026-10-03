# Ficha de los modelos congelados

## Uso previsto

Comparar, en la muestra reservada ENEMDU 2025, la clasificación contemporánea de empleo adecuado en la PEA de 15 años o más con educación superior reportada y título. Los resultados apoyan análisis científico agregado y el futuro dashboard.

## Modelos

- **Regresión logística predictiva:** regularización L2, `C=1`, codificación de referencia aprendida dentro de los pliegues.
- **Boosting:** 250 iteraciones, tasa 0,05, 15 hojas, mínimo 50 casos por hoja y L2=1.
- **Referencia:** prevalencia ponderada estimada sin usar el pliegue validado.

## Datos y variables

Entrenamiento: 31.502 registros y 5.054 UPM. Variables autorizadas: edad, marca 98 años o más, sexo, estado civil, asistencia educativa, nivel educativo reportado, autoidentificación étnica, provincia, área y mes. Se excluyeron ingresos, horas, condición de actividad, variables derivadas del objetivo, identificadores y variables del diseño como predictores.

## Límites

El objetivo describe la situación observada en 2025. Los modelos no pronostican empleo futuro, no establecen causas y no deben usarse para decisiones individuales de contratación, crédito o acceso a servicios. La categoría “nivel educativo reportado” no equivale necesariamente al título más alto obtenido.

## Resultados de desarrollo

La ROC-AUC OOF fue 0,669 para logística y 0,689 para boosting. El boosting mejoró la discriminación de forma moderada y presentó una pendiente de calibración de 0,757. Se observaron diferencias de sensibilidad por sexo y área que requieren evaluación única en prueba.

## Estado

Congelados el 30 de septiembre de 2026. La prueba reservada permanece sin leer y sin evaluar. Versiones y huellas están en `models/metadatos_modelos_congelados.json`.
