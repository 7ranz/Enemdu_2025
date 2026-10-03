# Educación superior y empleo en Ecuador — ENEMDU 2025

## INTEGRANTES
* Verónica Cristina Montenegro Mejía 

* Grace de Lourdes Guerrero Agila 

* Franz Eduardo Del Pozo Sánchez 


## Título: 
# Brechas de empleo adecuado en personas con educación superior completada en Ecuador: un análisis estadístico y de aprendizaje automático interpretable con ENEMDU 2025.

## Pregunta: 
# ¿Qué características se asocian con tener empleo adecuado entre las personas económicamente activas con educación superior completada en Ecuador, y cómo se compara su clasificación al utilizar aprendizaje automático frente a una regresión logística?

## Organización 

| Carpeta | Contenido |
|---|---|
| docs | Protocolo, decisiones, bibliografía y manuales |
| data/raw | Originales inalterados y documentación INEC |
| data/interim | Datos de trabajo intermedios |
| data/processed | Base analítica, diccionario y trazabilidad |
| notebooks | Siete etapas explicadas del EDA |
| src | Preparación, inferencia y modelos en Python |
| reports | Auditorías, tablas y figuras |
| dashboard | Aplicación Python |
| assets | Logos institucionales autorizados y carátula |
| outputs/final | Word y PowerPoint finales editables |

Las carpetas de producción se incorporarán conforme avancemos.

# Informe de avance del proyecto: Análisis Exploratorio de Datos (EDA) sobre la ENEMDU 2025

## Introducción

Este informe documenta el trabajo que he desarrollado a lo largo del proyecto de análisis de la ENEMDU 2025, siguiendo el protocolo de siete pasos visto en clase: pregunta, estructura, univariado, multivariado, faltantes y atípicos, segmentación y hallazgos. Se detalla los productos generados en cada etapa y las decisiones metodológicas.

## Primera etapa: delimitación y fuentes

Se comenzó definiendo el alcance del estudio y las variables de interés. Los productos de esta etapa fueron la ficha de delimitación y la matriz inicial de variables.

## Entrega EDA 02: calidad de los datos

Se revisó la calidad de la base, los identificadores y la estructura por meses. 

## Entrega EDA 03: preparación de la base y partición

Se preparó la base tratada y se dividió en entrenamiento y prueba reservada. Al final quedaron 31 502 registros de entrenamiento y 7 791 de prueba reservada, sin UPM, viviendas ni hogares compartidos. La prueba reservada se mantuvo cerrada durante todo el análisis intermedio para evitar filtraciones de información. Además, se eleboró el diccionario de la base tratada y una verificación formal de ambas particiones.

## Entrega EDA 04: análisis univariado

SE analizó cada variable por separado: distribuciones, frecuencias y medidas resumen. Los resultados se organizaron en tablas y figuras en formatos PNG y SVG.

## Entrega EDA 05: análisis bivariado y plan inferencial

SE analizó las asociaciones entre pares de variables y la parte inferencial antes de estimar. Se conservó el diseño bivariado completo, con las 334 786 filas necesarias para la estimación de dominios.

## Entrega EDA 06: inferencia con diseño muestral

Se estimó intervalos de confianza con linealización de Taylor y se ajustó los contrastes múltiples con el método de Holm. Los resultados quedaron en una tabla y en un libro de Excel para consulta, además de las figuras con intervalos de confianza.

## Entrega EDA 07: modelado interpretable

Desarrollamos modelos interpretables y se congeló las versiones finales para que no cambien después. La prueba reservada siguió cerrada durante todo el desarrollo. SE documentó las características y el rendimiento de cada modelo en una ficha de modelos congelados.

## Entrega de evaluación única

Con los modelos congelados, se evaluó una sola vez contra la prueba reservada y se cerró el proceso. Con esos resultados se tomó en grupo la decisión de qué modelos llevar al dashboard.

## Dashboard 

Dashboard interactivo para explorar los resultados.

### Ejecución local

Instala las dependencias y ejecuta la aplicación desde la raíz del proyecto:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

### Despliegue en Streamlit Community Cloud

Selecciona la rama `main` y configura **Main file path** como `dashboard/app.py`. Las dependencias se instalan desde `requirements.txt`, ubicado en la raíz del repositorio.


## Fuentes iniciales

- [Microdatos oficiales CSV comprimidos](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip).
- [Guía oficial de uso](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Guia_de_usuario_BDD_ENEMDU_anual_2025.pdf).
- [Portal ENEMDU 2025](https://www.ecuadorencifras.gob.ec/enemdu-2025/).
- [STROBE: reporte de estudios observacionales](https://www.strobe-statement.org/).
