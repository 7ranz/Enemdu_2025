# ETAPA 2 DEL EDA: preparar el cuaderno didáctico de controles de calidad.
# ARCHIVO: 01b_crear_cuaderno_calidad.py. Crea un cuaderno editable con instrucciones y código comentado.
# BLOQUE 1: herramientas y rutas.
from pathlib import Path  # Localiza los archivos del proyecto.
import nbformat as nbf  # Crea cuadernos Jupyter en su formato estándar.

RAIZ = Path(__file__).resolve().parents[1]  # Identifica la raíz del proyecto.
DESTINO = RAIZ / 'notebooks'  # Selecciona la carpeta de cuadernos.
DESTINO.mkdir(parents=True, exist_ok=True)  # Prepara el directorio de entrega.
celdas = []  # Almacena las celdas en el orden de aprendizaje.

def texto(contenido):  # Añade una explicación para el estudiante.
    celdas.append(nbf.v4.new_markdown_cell(contenido))  # Crea una celda de texto editable.

def codigo(contenido):  # Añade instrucciones Python ejecutables.
    celdas.append(nbf.v4.new_code_cell(contenido))  # Crea una celda de código editable.

# BLOQUE 2: objetivos, preparación y ejecución opcional del análisis completo.
texto('''# EDA 02 · Calidad, identificadores y consistencia mensual

**Proyecto:** educación superior y empleo en Ecuador, ENEMDU 2025.

**Objetivo de aprendizaje:** distinguir un dato inválido, una ausencia esperada y una repetición de encuesta. Este cuaderno no elimina filas ni cambia los archivos originales.

Trabajaremos con los reportes reales producidos por `src/01_auditoria_calidad.py`, cuyo código incluye comentarios de etapa, bloque y línea. La auditoría perfila todas las columnas y aplica reglas semánticas a las variables del estudio; no certifica cada respuesta ni reconstruye todos los saltos ocupacionales.

Ejecuta las celdas de arriba hacia abajo. Si un concepto es nuevo, detente en la pregunta de interpretación antes de continuar.''')
texto('''## Paso 1. Encontrar el proyecto

Una **ruta** indica dónde está un archivo. `Path` evita escribir una ruta personal fija. Buscamos la carpeta del proyecto partiendo de la ubicación donde abriste Jupyter.''')
codigo('''# BLOQUE 1: importar herramientas y localizar la carpeta del proyecto.
from pathlib import Path  # Maneja rutas de archivos.
import hashlib  # Verifica la identidad del archivo original.
import importlib.util  # Permite cargar nuestro programa comentado.
import json  # Lee los reportes estructurados.
import pandas as pd  # Trabaja con tablas.
from IPython.display import display, Markdown  # Presenta tablas y explicaciones.

ubicacion = Path.cwd().resolve()  # Obtiene la carpeta desde la que se ejecuta el cuaderno.
posibles = [ubicacion, *ubicacion.parents]  # Examina también las carpetas superiores.
raiz = next((p for p in posibles if (p / "src/01_auditoria_calidad.py").exists()), None)  # Busca el programa del proyecto.
if raiz is None:  # Contempla que Jupyter se abra en la carpeta que contiene enemdu_2025.
    raiz = ubicacion / "enemdu_2025"  # Prueba la ubicación habitual dentro del espacio de trabajo.
assert (raiz / "src/01_auditoria_calidad.py").exists(), "Abre este cuaderno dentro de la carpeta enemdu_2025."  # Verifica la ubicación.
reportes = raiz / "reports/calidad"  # Define dónde leeremos las salidas.
print("Proyecto localizado:", raiz.name)  # Confirma la localización sin depender de una ruta personal.''')
texto('''## Paso 2. Reproducir o consultar

La primera auditoría ya está ejecutada. Deja `RECALCULAR = False` para estudiar sus resultados. Cambia a `True` si deseas recorrer de nuevo las tablas completas; puede tardar varios minutos. **Recalcular no modifica los originales.**''')
codigo('''# BLOQUE 2: ejecutar opcionalmente el programa de auditoría.
RECALCULAR = False  # Cambia a True únicamente si deseas repetir todos los controles.
if RECALCULAR or not (reportes / "00_resumen_auditoria.json").exists():  # Ejecuta también si faltan resultados.
    especificacion = importlib.util.spec_from_file_location("auditoria", raiz / "src/01_auditoria_calidad.py")  # Localiza el módulo.
    modulo = importlib.util.module_from_spec(especificacion)  # Prepara el módulo en memoria.
    especificacion.loader.exec_module(modulo)  # Carga las funciones sin alterar la base.
    modulo.auditar()  # Ejecuta los controles comentados del programa principal.
resumen = json.loads((reportes / "00_resumen_auditoria.json").read_text(encoding="utf-8"))  # Lee los resultados.
huella = hashlib.sha256((raiz / "data/raw/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip").read_bytes()).hexdigest()  # Calcula la huella actual.
assert huella == resumen["sha256_original"], "El ZIP cambió: recalcula antes de interpretar estos reportes."  # Evita leer resultados de otra fuente.
display(pd.DataFrame({"Medida": ["Registros de personas", "Registros vivienda-hogar", "Variables de personas", "Reglas distintas"], "Valor": [resumen["filas_personas"], resumen["filas_vivienda_hogar"], resumen["columnas_personas"], resumen["reglas_distintas"]]}))  # Presenta el tamaño auditado.''')
texto('''## Paso 3. Leer la cobertura mensual

Cada fila de esta tabla resume un mes. Los pesos proceden de la **base anual**: sumar los pesos de un mes no produce automáticamente la estimación mensual oficial. “Registros candidatos” tampoco significa personas distintas durante el año.''')
codigo('''# BLOQUE 3: comprobar que los doce meses recuperan todos los registros.
mensual = pd.read_csv(reportes / "10_cobertura_mensual.csv", dtype={"mes": str})  # Conserva los ceros de los meses.
display(mensual[["mes", "registros", "hogares_observacion", "upm", "provincias", "candidatos", "edad_99"]])  # Muestra cobertura y población candidata.
assert mensual["registros"].sum() == resumen["filas_personas"]  # Comprueba una conciliación básica.
print("Los recuentos mensuales coinciden con el total anual de registros.")  # Explica el resultado.''')
texto('''## Paso 4. Interpretar faltantes con su denominador

Un **vacío físico** es una celda sin contenido. Puede corresponder a una pregunta que no se aplica. Una **no respuesta codificada** contiene un número reservado, como 999999 en determinados ingresos. No se deben tratar igual que un cero real.

Las reglas muestran cuántos registros debían cumplir cada condición (`n_aplicables`) y cuántos requieren revisión (`n_alertas`). Una alerta no demuestra un error.''')
codigo('''# BLOQUE 4: consultar controles y faltantes del dominio de estudio.
reglas = pd.read_csv(reportes / "03_reglas_calidad.csv", dtype={"mes": str})  # Lee todas las reglas con sus denominadores.
anuales = reglas.loc[reglas["mes"].eq("ANUAL")]  # Selecciona el resumen anual.
display(anuales.loc[anuales["n_alertas"].gt(0), ["regla", "descripcion", "tipo", "n_aplicables", "n_alertas"]])  # Muestra señales que requieren interpretación.
display(anuales.loc[anuales["tipo"].eq("faltante_candidato"), ["descripcion", "n_aplicables", "n_alertas"]])  # Examina covariables dentro de la población candidata.''')
texto('''**Pregunta de interpretación:** ¿por qué sería incorrecto eliminar toda fila que tenga al menos una celda vacía? Busca una pregunta que solo corresponda a quienes tienen trabajo o a quienes estudiaron educación superior.''')
codigo('''# BLOQUE 5: explorar disponibilidad de variables sin limpiar los datos.
perfil = pd.read_csv(reportes / "01_perfil_variables_mes.csv", dtype={"mes": str})  # Lee el perfil de todas las columnas.
seleccion = perfil["tabla"].eq("personas") & perfil["mes"].eq("ANUAL") & perfil["variable"].isin(["p03", "p10a", "p12a", "p12b", "ingrl"])  # Escoge ejemplos del estudio.
display(perfil.loc[seleccion, ["variable", "n", "vacios", "pct_vacios", "distintos_no_vacios"]])  # Compara ausencia física sin atribuirle causas automáticamente.
cambios = pd.read_csv(reportes / "02_cambios_disponibilidad.csv")  # Lee cambios entre meses.
display(cambios.head(10))  # Identifica las mayores variaciones para revisar módulos y saltos.''')
texto('''## Paso 5. Separar unicidad de seguimiento

Una clave puede ser única porque incorpora el mes. Eso no garantiza que una vivienda no reaparezca en otro levantamiento. Retiramos el sufijo mensual **solo después de comprobar su composición en todas las filas**.

La clave de persona sin mes representa una posición dentro del hogar. Cambios de miembros, numeración o respuesta pueden impedir que corresponda siempre a la misma persona física.''')
codigo('''# BLOQUE 6: examinar duplicados y repeticiones temporales.
duplicados = pd.read_csv(reportes / "04_duplicados.csv")  # Consulta unicidad de claves y filas completas.
repeticiones = pd.read_csv(reportes / "09_repeticion_sin_mes.csv")  # Consulta repeticiones una vez retirado el mes validado.
display(duplicados)  # Distingue repeticiones exactas de coincidencias de identificador.
display(repeticiones)  # Muestra cuántas claves estructurales aparecen en varios meses.
display(pd.read_csv(reportes / "08_cambios_claves_persona.csv"))  # Muestra señales que limitan el seguimiento individual.''')
texto('''**Pregunta de interpretación:** si repartimos las filas al azar, ¿podrían dos visitas a la misma vivienda terminar en entrenamiento y prueba? Explica por qué una separación por grupos reduce ese riesgo.''')
codigo('''# BLOQUE 7: consultar la matriz de solapamiento mensual de hogares.
solapamiento = pd.read_csv(reportes / "07_solapamiento_id_hogar.csv", dtype={"mes_a": str, "mes_b": str})  # Lee claves compartidas entre meses.
matriz = solapamiento.pivot(index="mes_a", columns="mes_b", values="claves_compartidas")  # Organiza meses en filas y columnas.
display(matriz)  # Presenta los recuentos sin añadir dependencias de gráficos en esta etapa.''')
texto('''La diagonal compara cada mes consigo mismo. Las celdas fuera de la diagonal muestran revisitas posibles. Esta matriz no demuestra por sí sola que cada integrante del hogar sea la misma persona.''')
texto('''## Paso 6. Verificar el enlace entre tablas y el diseño

La unión personas–hogares debe ser **muchos a uno**: muchas personas pueden pertenecer a un hogar, pero una observación de persona no debe multiplicarse al unir tablas. Los estratos y conglomerados se conservan en la muestra completa para la futura inferencia de dominios.''')
codigo('''# BLOQUE 8: revisar integridad y número de conglomerados.
display(pd.read_csv(reportes / "06_integridad_personas_hogares.csv"))  # Muestra registros sin pareja y discrepancias de campos comunes.
display(pd.read_csv(reportes / "05_dependencias_identificadores.csv"))  # Comprueba la jerarquía de identificadores.
diseno = pd.read_csv(reportes / "11_upm_por_estrato.csv", dtype={"estrato": str})  # Lee UPM de muestra completa y dominio.
display(diseno.loc[diseno["upm_muestra_completa"].le(1) | diseno["upm_con_candidatos"].le(1)])  # Muestra estratos con poca presencia para revisar incertidumbre.
print("Estratos de la muestra completa:", len(diseno))  # Informa cobertura del diseño.''')
texto('''## Paso 7. Comprobar la consistencia de los formularios

Comparamos las preguntas 10 y 12 de los doce PDF oficiales. El texto se normaliza quitando diferencias de espacios y acentos. La coincidencia respalda el mismo significado de estas preguntas, pero no demuestra que todos los módulos del cuestionario sean idénticos.''')
codigo('''# BLOQUE 9: consultar evidencia documental mensual.
formularios = json.loads((reportes / "formularios_mensuales.json").read_text(encoding="utf-8"))  # Lee páginas, enlaces y huellas.
display(pd.DataFrame([{"mes": f["mes"], "estado": f["estado"], "pagina_nivel": f.get("pregunta10_pagina_pdf"), "titulo_si1_no2": f.get("pregunta12_si1_no2", False)} for f in formularios]))  # Presenta la cobertura documental.
print("Textos distintos de pregunta 10:", len({f.get("pregunta10_sha256_texto") for f in formularios}))  # Resume equivalencia del texto educativo.
print("Fragmentos distintos de pregunta 12:", len({f.get("pregunta12_sha256_fragmento") for f in formularios}))  # Resume equivalencia de titulación.''')
texto('''## Paso 8. Contrastar códigos con las etiquetas oficiales

El archivo SPSS del INEC conserva etiquetas de valores que no aparecen en el diccionario Excel. Verificamos 89 variables categóricas contra ese catálogo. En edad, 98 significa **98 y más** y 99 significa **no informa**. En ingreso laboral, -1 significa **gasta más de lo que gana** y 999999 significa **no informa**.

El valor -1 no mide una pérdida de exactamente un dólar. Tampoco debe confundirse con una respuesta faltante.''')
codigo('''# BLOQUE 10: leer la validación de códigos y los estados del ingreso.
etiquetas = json.loads((reportes / "17_resumen_etiquetas.json").read_text(encoding="utf-8"))  # Lee el contraste con el SAV oficial.
print("Variables categóricas validadas:", etiquetas["variables_categoricas_validadas"])  # Informa el alcance de esta comprobación.
print("Categorías no etiquetadas encontradas:", len(etiquetas["alertas_anuales"]))  # No confunde ausencia de códigos inválidos con ausencia de cualquier problema.
display(pd.read_csv(reportes / "18_ingresos_por_condicion.csv"))  # Distingue no remuneración, no respuesta y gasto superior al ingreso.
print("Diferencias ciudad–prefijo UPM:", etiquetas["filas_prefijo_upm_distinto_ciudad"])  # Expone la revisión cartográfica pendiente.
print("Diferencias provincia–prefijo UPM:", etiquetas["filas_provincia_prefijo_upm_distinta_prov"])  # Comprueba consistencia territorial al nivel usado en el estudio.''')
texto('''## Paso 9. Decidir antes de limpiar

Consulta `docs/04_informe_calidad.md` para la interpretación y las decisiones. En la siguiente etapa construiremos la base tratada, registrando cada cambio. Todavía no hemos imputado ingresos, eliminado observaciones repetidas ni seleccionado modelos por su rendimiento.

**Ejercicio:** explica con tus palabras (1) por qué una celda vacía puede ser correcta, (2) por qué un identificador único puede ocultar revisitas y (3) por qué 999999 no debe convertirse automáticamente en un ingreso alto.

**Fuentes:** [guía anual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Guia_de_usuario_BDD_ENEMDU_anual_2025.pdf), [diseño anual](https://www.ecuadorencifras.gob.ec/documentos/web-inec/EMPLEO/2025/anual/Disenio_Muestral_ENEMDU_Anual_enero-diciembre_2025.pdf), diccionarios y sintaxis guardados en `data/raw/documentacion`. Los enlaces exactos de cada formulario están en `formularios_mensuales.json`.''')

# BLOQUE 3: guardar un cuaderno estándar, editable y ejecutable.
cuaderno = nbf.v4.new_notebook(cells=celdas)  # Construye el documento con texto y código.
cuaderno.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}  # Declara un núcleo Python estándar.
cuaderno.metadata['language_info'] = {'name': 'python', 'version': '3.12'}  # Indica el lenguaje de las celdas.
nbf.write(cuaderno, DESTINO / '02_calidad_identificadores_meses.ipynb')  # Guarda el cuaderno para uso y edición.
print('Cuaderno creado: 02_calidad_identificadores_meses.ipynb')  # Confirma el producto generado.
