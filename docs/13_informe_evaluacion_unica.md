# Etapa 8. Evaluación única en la prueba reservada

## Estado

La evaluación quedó completada y cerrada el 30 de septiembre de 2026. Se aplicaron sin modificaciones los modelos, predictores, hiperparámetros y umbrales congelados en la etapa anterior. La prueba contiene 7.791 personas y 1.269 UPM; no comparte UPM ni hogares con entrenamiento.

La incertidumbre se estimó mediante 1.000 réplicas de bootstrap que remuestrean UPM con reemplazo dentro de cada estrato. Las mismas réplicas se usaron para las diferencias pareadas entre modelos y grupos.

## Desempeño fuera de muestra

| Modelo | ROC-AUC (IC 95 %) | PR-AUC (IC 95 %) | Brier (IC 95 %) | Exactitud balanceada (IC 95 %) |
|---|---:|---:|---:|---:|
| Logística | 0,674 (0,645–0,702) | 0,813 (0,783–0,842) | 0,198 (0,185–0,210) | 0,632 (0,604–0,659) |
| Boosting | 0,684 (0,654–0,714) | 0,824 (0,794–0,852) | 0,195 (0,181–0,210) | 0,621 (0,592–0,647) |

Ambos modelos superan claramente la referencia de prevalencia. El desempeño de prueba es cercano al observado durante el desarrollo, lo que reduce la preocupación por un optimismo fuerte de la validación interna.

La logística presenta intercepto de calibración 0,026 y pendiente 0,930, cercanos a los valores ideales de 0 y 1. El boosting presenta intercepto 0,134 y pendiente 0,761, consistente con probabilidades más extremas de lo observado.

## ¿El aprendizaje automático mejora la clasificación?

| Diferencia: boosting menos logística | Estimación | IC 95 % |
|---|---:|---:|
| ROC-AUC | +0,0106 | −0,0097 a +0,0303 |
| PR-AUC | +0,0119 | −0,0012 a +0,0237 |
| Brier | −0,0028 | −0,0083 a +0,0032 |
| Log-loss | −0,0068 | −0,0195 a +0,0065 |
| Exactitud balanceada | −0,0117 | −0,0388 a +0,0145 |

El boosting ofrece una ventaja puntual pequeña en discriminación y error probabilístico, pero todos los intervalos pareados incluyen cero. Con esta muestra no existe evidencia concluyente de que mejore el desempeño fuera de muestra frente a la regresión logística. Con los umbrales congelados, la logística incluso alcanza mayor exactitud balanceada y mejor calibración.

La conclusión científica debe formularse como **ausencia de una mejora demostrada**, no como demostración de equivalencia entre los modelos.

## Resultados por sexo

La ROC-AUC del boosting fue 0,676 en hombres y 0,677 en mujeres. La diferencia mujeres menos hombres fue 0,001, con IC 95 % de −0,052 a 0,057. Por tanto, la capacidad de ordenamiento es semejante entre ambos grupos.

Con el umbral global 0,705, la sensibilidad fue 69,2 % en hombres y 53,9 % en mujeres. La brecha fue −15,3 puntos porcentuales, IC 95 % de −20,5 a −9,7. El Brier fue 0,182 en hombres y 0,207 en mujeres; la diferencia fue 0,0256, IC 95 % de 0,0064 a 0,0446.

La coexistencia de ROC-AUC similar y sensibilidad diferente indica que el problema aparece principalmente en el punto de operación global y en las distribuciones de riesgo/prevalencia, no en una pérdida clara de capacidad de ordenamiento para las mujeres.

## Resultados por área

La ROC-AUC del boosting fue 0,671 en área urbana y 0,746 en área rural. La diferencia rural menos urbana fue 0,075, IC 95 % de 0,007 a 0,135. A pesar de esa mayor discriminación, la sensibilidad rural fue 53,5 %, frente a 62,5 % urbana. La brecha fue −9,0 puntos porcentuales, IC 95 % de −17,7 a −0,7.

Esto muestra por qué la discriminación y las métricas dependientes de umbral deben informarse juntas: un grupo puede presentar mejor ROC-AUC y, al mismo tiempo, menor sensibilidad con un umbral común.

## Decisión para el artículo y el dashboard

La regresión logística será el **modelo principal de referencia** por parsimonia, calibración y desempeño competitivo. El boosting se conservará como comparador de aprendizaje automático. El dashboard mostrará ambos, pero no presentará al boosting como superior.

La contribución del artículo puede centrarse en que una mejora interna aparente del modelo de árboles se atenúa en prueba, mientras persisten diferencias de sensibilidad por sexo y área. Este resultado responde directamente a la pregunta sobre mejora predictiva con calibración comparable.

No se propondrán umbrales distintos por grupo en el análisis principal. Esa decisión implica objetivos normativos y costos de error que exceden la evaluación estadística. El dashboard permitirá examinar escenarios de umbral como análisis exploratorio claramente separado.

## Límites

La ENEMDU es transversal y las predicciones clasifican la situación observada en 2025. Los resultados no demuestran causalidad, no predicen empleo futuro y no autorizan decisiones individuales. Los intervalos de desempeño son condicionales a la partición reservada y aproximan la variación por conglomerados mediante el bootstrap especificado.

## Cierre de reproducibilidad

El archivo `reports/eda08_evaluacion/00_estado_evaluacion.json` conserva las huellas de la prueba y de las predicciones, los modelos aplicados y los umbrales. El programa impide una nueva puntuación si detecta ese cierre. Los análisis posteriores deben usar `data/processed/modelado/evaluacion/predicciones_prueba_unica.csv.gz` y las tablas ya exportadas.
