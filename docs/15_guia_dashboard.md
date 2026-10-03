# Guía del dashboard profesional

## Producto

El **Observatorio de educación superior y empleo en Ecuador** es una aplicación Streamlit desarrollada íntegramente en Python. Presenta resultados descriptivos, inferenciales y predictivos de ENEMDU anual 2025 sin incluir identificadores de persona, hogar o vivienda.

## Inicio rápido

1. Abra la carpeta `enemdu_2025`.
2. Haga doble clic en `iniciar_dashboard.bat`.
3. Espere a que el navegador abra `http://localhost:8501`.
4. Mantenga abierta la ventana de ejecución mientras utiliza el dashboard.
5. Para detenerlo, cierre esa ventana o presione `Ctrl+C`.

También puede iniciar desde PowerShell:

```powershell
.\iniciar_dashboard.ps1
```

## Secciones

### Panorama

Muestra tasas ponderadas de empleo adecuado, subempleo y desempleo. Cada tarjeta incluye IC 95 %, n, número de UPM, coeficiente de variación y nivel de precisión. Incluye comparación provincial, evolución mensual y descarga de la tabla filtrada.

### Brechas

Permite elegir indicador, dimensión y dos grupos. Calcula la diferencia A menos B, su IC 95 % y valor p utilizando la covarianza compartida del diseño.

### Ingresos

Presenta 35.080 montos laborales observados entre personas ocupadas del dominio. Calcula cuantiles ponderados y permite variar el límite visual del histograma. Los faltantes y códigos especiales no se imputan.

### Asociaciones

Presenta razones de momios e IC 95 % de la regresión logística ajustada. Las familias de variables se pueden seleccionar de forma independiente. La prueba global de Wald se muestra debajo del gráfico.

### Modelos

Compara logística y boosting con la evaluación única en prueba reservada. Incluye métricas con intervalos, diferencias pareadas, calibración, desempeño por sexo y área e importancia por permutación.

### Metodología

Resume universo, diseño, ponderación, inferencia, evaluación predictiva, privacidad y límites de interpretación.

## Filtros

Los filtros de provincia, sexo, área, edad, educación y mes afectan las secciones descriptivas e inferenciales. Los resultados de modelos permanecen congelados porque provienen de la evaluación única en prueba.

Una selección con menos de 100 observaciones o CV superior a 20 % aparece como **Precaución**. Estas cifras son exploratorias y no deberían citarse sin revisar soporte e incertidumbre.

## Arquitectura editable

- `dashboard/app.py`: interfaz Streamlit.
- `dashboard/metricas.py`: motor de estimación por diseño.
- `config/dashboard_v1.json`: textos y reglas configurables.
- `.streamlit/config.toml`: colores y comportamiento visual.
- `data/dashboard/`: datos de visualización sin identificadores personales.
- `src/08_preparar_dashboard.py`: preparación reproducible.
- `src/08a_verificar_dashboard.py`: controles automáticos.

## Criterios científicos

Las tasas dinámicas utilizan linealización de Taylor, 150 estratos, 7.780 UPM, 7.630 grados de libertad e intervalos logit para proporciones. Los resultados predictivos no se recalculan en la interfaz. La aplicación no genera predicciones individuales y no debe utilizarse para decisiones laborales, crediticias o de acceso a servicios.
