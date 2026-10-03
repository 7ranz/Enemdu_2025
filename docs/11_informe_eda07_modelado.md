# Etapa 7. Desarrollo de modelos, asociaciones ajustadas e interpretación

## Estado y alcance

La etapa quedó **completada y congelada** el 30 de septiembre de 2026. Se utilizó exclusivamente el archivo de entrenamiento (31.502 personas, 5.054 UPM) y sus cinco pliegues internos previamente asignados por UPM. El archivo de prueba reservada no fue leído, perfilado ni evaluado.

Los resultados de esta etapa son diagnósticos de desarrollo. La comparación final se realizará una sola vez en la prueba reservada después de aceptar este congelamiento.

## Preguntas resueltas

1. ¿Qué hiperparámetros ofrecen el mejor desempeño interno para la regresión logística y el boosting?
2. ¿Cuánto mejora internamente el boosting frente a la regresión logística?
3. ¿Qué asociaciones persisten después de ajustar simultáneamente por edad, sexo, área, educación, estado civil, asistencia, etnia, provincia y mes?
4. ¿Qué variables sostienen la capacidad predictiva y cómo cambia el desempeño por sexo y área?

## Diseño del desarrollo predictivo

Se compararon una referencia de prevalencia ponderada, tres regresiones logísticas y cuatro modelos `HistGradientBoostingClassifier`. En cada pliegue, el preprocesamiento y el modelo se ajustaron con cuatro grupos de UPM y predijeron el quinto. Los pesos `fexp` se normalizaron a media uno dentro del ajuste; esta operación conserva su peso relativo y mejora la estabilidad numérica.

La selección usó ROC-AUC ponderada media y, ante empate, menor Brier. Se congeló la logística con `C=1`. En boosting se congeló la configuración B1: tasa de aprendizaje 0,05; 15 hojas; mínimo de 50 observaciones por hoja; regularización L2 de 1 y 250 iteraciones. Los umbrales elegidos mediante exactitud balanceada OOF fueron 0,695 para logística y 0,705 para boosting.

## Desempeño interno

| Modelo | ROC-AUC OOF | PR-AUC OOF | Brier | Pendiente de calibración | Exactitud balanceada |
|---|---:|---:|---:|---:|---:|
| Base | 0,473 | 0,680 | 0,212 | −3,856 | 0,500 |
| Logística | 0,669 | 0,812 | 0,196 | 0,895 | 0,621 |
| Boosting | 0,689 | 0,828 | 0,193 | 0,757 | 0,634 |

El boosting aumenta la ROC-AUC en 0,020 y la PR-AUC en 0,016 frente a la logística, y reduce el Brier en 0,003. La mejora es consistente con una ganancia incremental de discriminación. La pendiente de calibración menor que uno indica probabilidades algo extremas, especialmente en boosting; esto deberá comprobarse en prueba antes de decidir cualquier recalibración.

La referencia base varía ligeramente entre pliegues porque usa la prevalencia de los cuatro pliegues de ajuste. Por ello su ROC-AUC agrupada puede diferir de 0,5; sigue funcionando únicamente como referencia de prevalencia.

## Desempeño por grupos

En boosting, la ROC-AUC fue 0,700 en hombres y 0,675 en mujeres. Con el umbral global congelado, la sensibilidad fue 70,1 % en hombres y 57,0 % en mujeres: una diferencia descriptiva de −13,1 puntos porcentuales para mujeres. Por área, la ROC-AUC fue 0,673 en urbana y 0,730 en rural; la sensibilidad fue 64,6 % y 52,5 %, respectivamente, una diferencia de −12,1 puntos porcentuales para el área rural.

Estas diferencias OOF son diagnósticos para vigilar, no estimaciones definitivas de equidad. La evaluación única en prueba deberá informar incertidumbre y evitar concluir que una diferencia observada prueba sesgo algorítmico por sí sola.

## Asociaciones ajustadas

Se estimó una regresión logística ponderada en las 39.293 personas del dominio analítico. La covarianza sándwich incorporó las 7.780 UPM y 150 estratos de la muestra completa mediante contribuciones cero fuera del dominio; los grados de libertad fueron 7.630. El algoritmo convergió en seis iteraciones.

| Comparación | OR ajustada | IC 95 % | p |
|---|---:|---:|---:|
| Mujer frente a hombre | 0,73 | 0,66–0,81 | <0,001 |
| Rural frente a urbana | 0,80 | 0,68–0,94 | 0,007 |
| Superior no universitaria frente a universitaria | 0,86 | 0,76–0,98 | 0,029 |
| Posgrado frente a universitaria | 2,88 | 2,42–3,43 | <0,001 |

Las asociaciones por sexo y área persisten después del ajuste. Educación, edad, estado civil y provincia presentan evidencia global; etnia y mes no alcanzan 0,05 en las pruebas globales ajustadas. Los términos lineal y cuadrático de edad deben interpretarse conjuntamente: describen una relación curvada y no una razón de momios constante para cualquier década.

Las razones de momios son asociaciones condicionales contemporáneas. No estiman efectos causales ni probabilidades individuales futuras.

## Interpretación predictiva

La importancia por permutación se calculó exclusivamente en los pliegues no usados para el ajuste. En boosting, las mayores caídas medias de ROC-AUC correspondieron a edad (0,067), nivel educativo (0,045), estado civil (0,034), provincia (0,027) y sexo (0,018). En logística dominaron nivel educativo, estado civil y provincia.

La importancia señala dependencia predictiva del modelo. No mide causalidad, justicia ni importancia social. Las variables correlacionadas pueden repartirse o intercambiar importancia.

## Artefactos congelados

- `models/logistica_predictiva_congelada.joblib`
- `models/boosting_congelado.joblib`
- `models/metadatos_modelos_congelados.json`
- `data/processed/modelado/desarrollo/predicciones_oof.csv.gz`
- `reports/eda07_modelado/`: tablas de selección, métricas, calibración, grupos, importancia y asociaciones.
- `reports/figures/eda07_modelado/`: cuatro figuras en PNG y SVG editable.
- `notebooks/07_desarrollo_modelos_interpretables.ipynb`: recorrido reproducible comentado.

## Regla para la etapa siguiente

La próxima etapa cargará estos objetos y aplicará exactamente sus predictores, hiperparámetros y umbrales a la prueba reservada. Se calcularán una sola vez ROC-AUC, PR-AUC, Brier, calibración y métricas por sexo y área. No se reajustarán decisiones después de observar esos resultados; cualquier cambio posterior se registrará como análisis nuevo y separado.
