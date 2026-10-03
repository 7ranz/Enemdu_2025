# Cómo estudiar la etapa de calidad

**Para comenzar:** abre el informe `04_informe_calidad.md` y lee sus secciones 1, 4, 5 y 7. Después abre el cuaderno `notebooks/02_calidad_identificadores_meses.ipynb`; ya contiene resultados de una ejecución comprobada.

## Tres conceptos para esta etapa

| Concepto | Significado en nuestro proyecto |
|---|---|
| Registro | Una fila de una observación de encuesta; no necesariamente una persona distinta durante el año |
| Clave | Un código para relacionar registros; su composición determina qué identifica |
| Faltante estructural | Ausencia esperada porque una pregunta no correspondía a esa persona |

Una celda vacía no es un cero. Un código único no garantiza identidad longitudinal. Un número grande puede ser un código de no respuesta.

## Orden de lectura

1. En el cuaderno, localiza las carpetas y comprueba el tamaño de las tablas.
2. Revisa la cobertura por mes y comprueba que sus recuentos suman el total.
3. Lee los controles con alertas junto con su denominador y explicación; no sumes sus cantidades porque pueden referirse a los mismos registros.
4. Compara duplicados exactos con revisitas de hogares.
5. Examina el cruce de ingresos por condición laboral.
6. Explica por qué la próxima división entre entrenamiento y prueba debe respetar grupos.

## Programas de la etapa

| Archivo | Qué hace |
|---|---|
| `src/01_auditoria_calidad.py` | Lee ambas bases, perfila variables, comprueba reglas, claves, enlaces, pesos y repeticiones |
| `src/01a_revisar_formularios.py` | Descarga o reutiliza los doce formularios y contrasta preguntas educativas |
| `src/01c_validar_etiquetas_oficiales.py` | Recupera etiquetas SPSS y contrasta 89 campos categóricos |
| `src/01d_resumir_ingresos.py` | Desglosa ingresos vacíos y códigos especiales entre ocupados candidatos |
| `src/01b_crear_cuaderno_calidad.py` | Genera la versión editable del cuaderno; regenerarlo borra sus salidas guardadas |

## Volver a ejecutar

En un entorno Python con las dependencias de `requirements_eda.txt`, desde la carpeta `enemdu_2025`:

```powershell
python src/01_auditoria_calidad.py # Audita estructura, claves y consistencia.
python src/01a_revisar_formularios.py # Contrasta preguntas de los doce meses.
python src/01c_validar_etiquetas_oficiales.py # Comprueba códigos contra SPSS.
python src/01d_resumir_ingresos.py # Explica ausencias y códigos de ingresos.
```

Los comandos necesitan las dos bases comprimidas oficiales ya presentes en `data/raw`. El programa de formularios utiliza internet solo si faltan sus descargas documentadas. La auditoría principal puede tardar varios minutos porque revisa las columnas completas, no una muestra pequeña.

Si solo deseas estudiar resultados, no necesitas repetir todas las lecturas: el cuaderno inicia con `RECALCULAR = False`. Si lo cambias a `True`, se vuelve a ejecutar la auditoría principal. Los complementos documentales y de etiquetas se ejecutan con sus programas propios.

## Qué queda para EDA 03

Construir la base tratada y su diccionario, aplicar las decisiones de esta auditoría, conservar trazabilidad de transformaciones y reservar la muestra de prueba. Todavía no calcularemos una “exactitud de IA” ni interpretaremos asociaciones como efectos causales.
