# Etapa 10. Documento metodológico APA 7 y presentación final

## Propósito

Esta etapa integra en productos académicos editables las decisiones y los resultados ya cerrados. No recalcula métricas ni vuelve a utilizar la muestra de prueba. El documento y las diapositivas leen las tablas, figuras y decisiones verificadas en las etapas anteriores.

## Productos

- `outputs/final/Informe_metodologico_ENEMDU_2025_APA7.docx`: informe editable de 18 páginas, con portada, resumen, problema, objetivos, hipótesis, metodología, resultados, discusión, conclusiones, referencias y apéndices.
- `outputs/final/Presentacion_final_ENEMDU_2025.pptx`: presentación editable de 16 diapositivas en formato panorámico, fondo blanco, notas de fuente y franja inferior con los logos de la Facultad de Ciencias, UCETech, Ciencia Central y Universidad Central del Ecuador.
- `src/09_crear_documento_metodologico.py`: programa comentado que reproduce el documento Word.
- `src/09_crear_presentacion_final.mjs`: programa comentado que reproduce el PowerPoint y ejecuta sus controles estructurales.
- `src/09b_verificar_entrega_final.py`: control reproducible de integridad, estructura y huellas SHA-256.
- `assets/portada_investigacion_enemdu_2025.png`: ilustración original de la investigación utilizada en la carátula.

## Estándares de comunicación científica

La redacción, las tablas y las referencias siguen APA 7. El reporte observacional se organizó con la guía STROBE para estudios transversales. La parte predictiva adapta TRIPOD+AI para transparentar población, particiones, predictores, métricas, calibración y desempeño por grupos. PROBAST+AI se empleó como marco crítico para discutir riesgo de sesgo y aplicabilidad; no se presenta como una certificación formal del modelo.

## Hilo narrativo compartido

Ambos productos conservan los mismos resultados: empleo adecuado ponderado de 68,85% (IC 95% [67,54%, 70,13%]); brechas de −5,91 puntos porcentuales para mujeres frente a hombres y de −10,97 puntos para área rural frente a urbana; asociaciones ajustadas principales; desempeño de la regresión logística y del boosting; calibración; y brechas de sensibilidad. La regresión logística se mantiene como referencia y el boosting como comparador.

## Controles realizados

El Word se exportó a PDF y sus 18 páginas se revisaron como imágenes. Se comprobó que no existieran cortes, superposiciones ni tablas fragmentadas de forma inadecuada. El PowerPoint superó controles de integridad del paquete, geometría, fuentes, cantidad de diapositivas y gráficos nativos; contiene seis gráficos cuantitativos editables con sus libros de datos incrustados. Las 16 diapositivas también se renderizaron y se revisaron visualmente.

## Reproducción

1. Ejecute `src/09_crear_documento_metodologico.py` con el entorno Python del proyecto.
2. Ejecute `src/09_crear_presentacion_final.mjs` con Node.js y las dependencias del proyecto.
3. Compruebe que las salidas aparezcan en `outputs/final`.
4. Revise visualmente el documento y la presentación después de cualquier cambio de contenido, fuente, imagen o tamaño.

Los programas identifican la etapa, el archivo, sus bloques y cada instrucción relevante mediante comentarios. Los recursos institucionales y la ilustración permanecen separados para facilitar su reemplazo o edición posterior.
