# Plan para intervalos de confianza con diseño muestral

## Estimador

Para cada grupo (g), la proporción de empleo adecuado se estimará como razón de totales ponderados:

\[
\hat p_g =
\frac{\sum_i w_i I(D_i=1)I(G_i=g)y_i}
     {\sum_i w_i I(D_i=1)I(G_i=g)}.
\]

Aquí, (D_i) identifica el dominio, (G_i) el grupo, (y_i) el empleo adecuado y (w_i) el factor anual `fexp`.

## Varianza

Se usará linealización de Taylor del estimador de razón. Las contribuciones linealizadas se agregarán primero por UPM y después se centrará su variación dentro de cada estrato. Se mantendrán todas las UPM de la muestra; las que no contienen casos de un subgrupo tendrán contribución cero.

No se aplicará corrección por población finita mientras no exista una variable pública oficial que permita especificarla de manera verificable. Los grados de libertad se calcularán como número de UPM menos número de estratos: 7 780 − 150 = 7 630 para la muestra completa.

Para proporciones se evaluarán intervalos en escala logit y transformación inversa, porque mantienen los límites entre 0 y 1. Para categorías con estimación exactamente 0 o 1 se definirá una alternativa antes de publicar resultados.

## Diferencias

La varianza de una diferencia se obtendrá de la influencia conjunta de ambos estimadores. No se sumarán varianzas como si los grupos provinieran de muestras independientes, porque comparten estratos, UPM y calibración de pesos.

Contrastes primarios preespecificados:

- Mujeres menos hombres.
- Rural menos urbana.
- Superior no universitaria menos universitaria.
- Posgrado menos universitaria.

Edad y provincia se tratarán primero como análisis globales. Las comparaciones provinciales individuales requerirán un control explícito por multiplicidad o se presentarán como exploratorias.

## Diagnósticos que deben acompañar cada estimación

- Número de observaciones, UPM y estratos con casos.
- Error estándar e intervalo de confianza de 95 %.
- Coeficiente de variación de la estimación.
- Grados de libertad utilizados.
- Advertencias por tamaño pequeño, límites 0/1 o inestabilidad.
- Regla documentada para estratos con una sola UPM en casos del subgrupo, manteniendo la estructura completa.

## Validación

Se contrastarán las tasas puntuales con `01_tasas_empleo_adecuado_grupos.csv`. Se implementarán casos de prueba manuales para una media ponderada simple, un estimador de dominio con UPM de aporte cero y una diferencia con covarianza. Si es posible, se comparará una selección de resultados con una implementación reconocida de encuestas complejas.

Ningún resultado se llamará significativo hasta que estos controles hayan pasado.
