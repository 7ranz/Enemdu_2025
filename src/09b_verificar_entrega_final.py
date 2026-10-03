"""Etapa 10: verifica la integridad y registra las huellas de los entregables finales."""  # Describe la finalidad del programa.

from pathlib import Path  # Gestiona rutas de forma portable.
import hashlib  # Calcula huellas criptográficas de los archivos finales.
import json  # Lee y actualiza el reporte de verificación.
import zipfile  # Comprueba la integridad interna de DOCX y PPTX.

from docx import Document  # Inspecciona la estructura editable del documento Word.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto.
DOCX = RAIZ / "outputs" / "final" / "Informe_metodologico_ENEMDU_2025_APA7.docx"  # Localiza el documento final.
PPTX = RAIZ / "outputs" / "final" / "Presentacion_final_ENEMDU_2025.pptx"  # Localiza la presentación final.
REPORTE = RAIZ / "reports" / "final" / "00_verificacion_entrega.json"  # Localiza el registro de control.


def sha256(ruta):  # Calcula una huella SHA-256 sin cargar todo el archivo en memoria.
    huella = hashlib.sha256()  # Inicializa el algoritmo criptográfico.
    with ruta.open("rb") as archivo:  # Abre el archivo en modo binario y asegura su cierre.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):  # Lee bloques de un megabyte hasta finalizar.
            huella.update(bloque)  # Incorpora cada bloque al cálculo.
    return huella.hexdigest()  # Devuelve la huella hexadecimal completa.


for archivo_final in (DOCX, PPTX):  # Recorre los dos paquetes editables finales.
    with zipfile.ZipFile(archivo_final) as paquete:  # Abre el contenedor Office Open XML.
        assert paquete.testzip() is None, f"Paquete dañado: {archivo_final.name}"  # Exige que todos los componentes internos sean legibles.

documento = Document(DOCX)  # Abre el Word para contar sus tablas editables.
with zipfile.ZipFile(PPTX) as paquete_pptx:  # Abre el PowerPoint para inventariar objetos nativos.
    nombres = paquete_pptx.namelist()  # Recupera la lista de componentes internos.
    diapositivas = sum(nombre.startswith("ppt/slides/slide") and nombre.endswith(".xml") for nombre in nombres)  # Cuenta diapositivas reales.
    graficos = sum(nombre.startswith("ppt/slides/charts/chart") and nombre.endswith(".xml") for nombre in nombres)  # Cuenta gráficos nativos en la ruta generada por la herramienta de presentación.
    libros = sum(nombre.startswith("ppt/embeddings/") and nombre.endswith(".xlsx") for nombre in nombres)  # Cuenta libros de datos incrustados.

control = json.loads(REPORTE.read_text(encoding="utf-8"))  # Lee el control preparado para esta etapa.
control["documento"]["sha256"] = sha256(DOCX)  # Registra la huella exacta del Word.
control["documento"]["tamano_bytes"] = DOCX.stat().st_size  # Registra el tamaño del Word.
control["documento"]["tablas_editables"] = len(documento.tables)  # Registra el número de tablas editables.
control["presentacion"]["sha256"] = sha256(PPTX)  # Registra la huella exacta del PowerPoint.
control["presentacion"]["tamano_bytes"] = PPTX.stat().st_size  # Registra el tamaño del PowerPoint.
control["presentacion"]["diapositivas"] = diapositivas  # Confirma el número de diapositivas.
control["presentacion"]["graficos_nativos_editables"] = graficos  # Confirma el número de gráficos editables.
control["presentacion"]["libros_de_datos_incrustados"] = libros  # Confirma la presencia de las hojas de datos.
REPORTE.write_text(json.dumps(control, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")  # Guarda el reporte legible y actualizado.
print(json.dumps(control, ensure_ascii=False, indent=2))  # Muestra el resultado para la bitácora de ejecución.
