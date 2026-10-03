import fs from "node:fs/promises"; // Lee imágenes y guarda los productos de la presentación.
import path from "node:path"; // Construye rutas absolutas del proyecto.
import { pathToFileURL } from "node:url"; // Convierte rutas locales en módulos importables.
import { Presentation, PresentationFile } from "@oai/artifact-tool"; // Crea la presentación PowerPoint editable.

const SKILL_DIR = "C:/Users/franz/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations"; // Localiza las utilidades oficiales de presentaciones.
const RUNTIME_PYTHON = "C:/Users/franz/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"; // Selecciona el Python incluido en el entorno.
const workspaceDir = path.resolve(import.meta.dirname, ".."); // Localiza la raíz del proyecto ENEMDU.
const TMP_DIR = path.join(workspaceDir, ".build", "presentacion_final"); // Define la carpeta privada de construcción.
const FINAL_PPTX = path.join(workspaceDir, "outputs", "final", "Presentacion_final_ENEMDU_2025.pptx"); // Define el nombre estable del entregable PowerPoint.
await fs.mkdir(TMP_DIR, { recursive: true }); // Crea la carpeta de construcción.
await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true }); // Crea la carpeta final.
await fs.rm(FINAL_PPTX, { force: true }); // Retira una versión generada anteriormente para permitir una reconstrucción reproducible.

const { resolvePresentationFont, applyPresentationChartFont, finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href); // Carga utilidades de fuente y validación.
const family = resolvePresentationFont({ fontFamily: "Aptos" }); // Usa una fuente instalada y legible en PowerPoint.
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } }); // Crea un lienzo panorámico 16:9.

const C = { navy: "#102A43", blue: "#176B87", cyan: "#20A4A0", red: "#D64045", gold: "#C9922E", ink: "#17202A", gray: "#667085", pale: "#EEF4F7", white: "#FFFFFF", line: "#D5DEE5" }; // Centraliza la paleta académica.
const assets = path.join(workspaceDir, "assets"); // Localiza los activos visuales.
const figures = path.join(workspaceDir, "reports", "figures"); // Localiza las figuras científicas.
const coverBytes = await fs.readFile(path.join(assets, "portada_investigacion_enemdu_2025.png")); // Lee la ilustración de carátula generada.
const logosBytes = await fs.readFile(path.join(assets, "institucional", "logos_fcd_ucetech_cienciacentral.png")); // Lee los tres logos institucionales combinados.
const uceBytes = await fs.readFile(path.join(assets, "institucional", "logo_uce_oficial.png")); // Lee el sello oficial de la Universidad Central.
const dashboardBytes = await fs.readFile(path.join(assets, "captura_dashboard.png")); // Lee la captura del dashboard profesional.

function addText(slide, text, left, top, width, height, size = 22, options = {}) { // Añade texto editable con una configuración uniforme.
  const shape = slide.shapes.add({ geometry: "textbox", position: { left, top, width, height }, fill: "none", line: { fill: "none", width: 0 } }); // Crea una caja de texto sin marco.
  shape.text = text; // Inserta el contenido solicitado.
  shape.text.style = { typeface: family, fontSize: size, bold: options.bold ?? false, italic: options.italic ?? false, color: options.color ?? C.ink, autoFit: "shrinkText", alignment: options.align ?? "left", verticalAlignment: options.valign ?? "middle" }; // Aplica estilo tipográfico y ajuste automático.
  return shape; // Devuelve la caja creada para futuras modificaciones.
} // Cierra el ayudante de texto.

function addTitle(slide, title, kicker) { // Añade el encabezado estándar de una diapositiva.
  if (kicker) addText(slide, kicker.toUpperCase(), 64, 28, 520, 24, 13, { bold: true, color: C.cyan }); // Inserta una categoría breve sobre el título.
  addText(slide, title, 64, kicker ? 52 : 38, 1130, 64, 34, { bold: true, color: C.navy }); // Inserta el título principal.
  const rule = slide.shapes.add({ geometry: "line", position: { left: 64, top: 118, width: 1152, height: 0 }, fill: "none", line: { fill: C.line, width: 1 } }); // Dibuja una línea divisoria ligera.
  return rule; // Devuelve la línea para completar la función.
} // Cierra el ayudante de títulos.

function addFooter(slide, number) { // Añade los cuatro logos y el número de diapositiva.
  slide.shapes.add({ geometry: "line", position: { left: 64, top: 650, width: 1152, height: 0 }, fill: "none", line: { fill: C.line, width: 1 } }); // Separa el contenido de la franja institucional.
  slide.images.add({ blob: logosBytes, contentType: "image/png", alt: "Facultad de Ciencias, UCETech y Ciencia Central", fit: "contain", position: { left: 64, top: 658, width: 348, height: 45 } }); // Inserta los tres logos solicitados.
  slide.images.add({ blob: uceBytes, contentType: "image/png", alt: "Universidad Central del Ecuador", fit: "contain", crop: { left: 0, top: 0, right: 0, bottom: 0.2 }, position: { left: 1120, top: 654, width: 56, height: 52 } }); // Inserta el sello de la Universidad Central.
  addText(slide, String(number).padStart(2, "0"), 1180, 666, 36, 24, 12, { bold: true, color: C.gray, align: "right" }); // Añade el número de diapositiva.
} // Cierra el ayudante de pie institucional.

function addNotes(slide, notes) { // Añade fuentes y orientación de exposición en las notas.
  slide.speakerNotes.textFrame.setText(notes); // Conserva las citas sin saturar el lienzo.
} // Cierra el ayudante de notas.

function addBodyLines(slide, lines, left, top, width, lineHeight = 54, size = 21) { // Añade una secuencia de ideas breves.
  lines.forEach((line, index) => { // Recorre cada idea en orden.
    addText(slide, line, left, top + index * lineHeight, width, lineHeight - 4, size, { color: index === 0 ? C.navy : C.ink, bold: index === 0 }); // Coloca cada línea con jerarquía visual.
  }); // Finaliza el recorrido de ideas.
} // Cierra el ayudante de líneas.

function addMetric(slide, value, label, left, top, color = C.blue) { // Añade una cifra protagonista sin apariencia de panel interactivo.
  addText(slide, value, left, top, 230, 58, 44, { bold: true, color }); // Muestra la cifra principal.
  addText(slide, label, left, top + 56, 245, 48, 17, { color: C.gray }); // Explica la cifra con texto corto.
} // Cierra el ayudante de métricas.

function addImage(slide, bytes, alt, left, top, width, height, fit = "contain") { // Inserta una imagen con texto alternativo.
  return slide.images.add({ blob: bytes, contentType: "image/png", alt, fit, position: { left, top, width, height } }); // Añade la imagen preservando su proporción.
} // Cierra el ayudante de imágenes.

function addChart(slide, type, config) { // Crea un gráfico nativo y editable.
  const chart = slide.charts.add(type, config); // Añade el gráfico al lienzo.
  applyPresentationChartFont(chart, { fontFamily: family }); // Aplica la fuente seleccionada a ejes, etiquetas y leyendas.
  return chart; // Devuelve el gráfico para completar el contrato de edición.
} // Cierra el ayudante de gráficos.

let slide = presentation.slides.add(); // Crea la diapositiva 1.
slide.background.fill = C.white; // Aplica fondo blanco.
addImage(slide, coverBytes, "Ilustración científica sobre educación superior, empleo e inteligencia artificial en Ecuador", 470, 0, 810, 650, "cover"); // Coloca la carátula generada en el lado derecho.
addText(slide, "BRECHAS DE EMPLEO ADECUADO", 64, 88, 500, 34, 17, { bold: true, color: C.cyan }); // Introduce el tema.
addText(slide, "Educación superior y empleo en Ecuador", 64, 126, 510, 158, 48, { bold: true, color: C.navy }); // Presenta el título de la investigación.
addText(slide, "Análisis estadístico y aprendizaje automático interpretable con ENEMDU 2025", 64, 300, 485, 88, 23, { color: C.ink }); // Resume el enfoque metodológico.
addText(slide, "Franz Eduardo Del Pozo Sánchez\nPython para Ciencia de Datos e Inteligencia Artificial\n30 de septiembre de 2026", 64, 458, 470, 104, 17, { color: C.gray }); // Identifica autor, asignatura y fecha.
addFooter(slide, 1); // Añade la franja institucional.
addNotes(slide, "Fuente visual: ilustración original generada para este proyecto. Datos: INEC, ENEMDU anual 2025."); // Registra fuentes de portada.

slide = presentation.slides.add(); // Crea la diapositiva 2.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "El título superior no elimina las brechas laborales", "Problema"); // Plantea la conclusión sustantiva.
addMetric(slide, "68,85%", "empleo adecuado en la población analizada", 80, 180, C.blue); // Presenta la tasa global.
addMetric(slide, "−5,91 pp", "diferencia de mujeres frente a hombres", 395, 180, C.red); // Presenta la brecha por sexo.
addMetric(slide, "−10,97 pp", "diferencia rural frente a urbana", 710, 180, C.red); // Presenta la brecha territorial.
addText(slide, "La investigación combina inferencia poblacional y evaluación predictiva para responder si las diferencias persisten tras el ajuste y si un modelo de árboles aporta una mejora real fuera de muestra.", 80, 360, 1030, 130, 25, { color: C.ink }); // Explica el valor del estudio.
addText(slide, "Las estimaciones incorporan pesos, estratos y UPM.", 80, 530, 900, 40, 18, { bold: true, color: C.blue }); // Señala la exigencia del diseño complejo.
addFooter(slide, 2); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/eda06_inferencia/06_tabla_cientifica_principal.csv. pp = puntos porcentuales."); // Registra la fuente de las cifras.

slide = presentation.slides.add(); // Crea la diapositiva 3.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Pregunta, objetivos e hipótesis", "Diseño de investigación"); // Presenta la lógica de investigación.
addText(slide, "¿Qué características se asocian con el empleo adecuado y cuánto mejora la clasificación al usar aprendizaje automático frente a una regresión logística?", 80, 150, 1090, 95, 27, { bold: true, color: C.navy }); // Expone la pregunta principal.
addBodyLines(slide, ["Objetivo descriptivo", "Estimar tasas y brechas ponderadas por sexo y territorio."], 80, 285, 500, 62, 21); // Presenta el objetivo descriptivo.
addBodyLines(slide, ["Objetivo asociativo", "Evaluar si las diferencias persisten tras el ajuste."], 660, 285, 500, 62, 21); // Presenta el objetivo asociativo.
addBodyLines(slide, ["Hipótesis predictiva", "El modelo de árboles puede mejorar la clasificación, pero la mejora debe confirmarse en prueba."], 80, 430, 1080, 60, 21); // Declara la hipótesis refutable.
addFooter(slide, 3); // Añade la franja institucional.
addNotes(slide, "La tercera hipótesis se definió como contrastable y podía rechazarse. Véase docs/02_ficha_delimitacion.md."); // Añade orientación metodológica.

slide = presentation.slides.add(); // Crea la diapositiva 4.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Población analítica y prueba reservada", "Datos"); // Introduce el flujo analítico.
const flow = [ // Define las etapas del flujo de datos.
  ["334 786", "registros originales", 80], // Registra la base de origen.
  ["39 551", "dominio descriptivo", 350], // Registra la población elegible.
  ["39 293", "dominio predictivo", 620], // Registra la etiqueta principal.
  ["7 791", "prueba reservada", 890], // Registra el conjunto final.
]; // Cierra la definición del flujo.
flow.forEach(([value, label, left], index) => { // Recorre las cuatro etapas.
  const box = slide.shapes.add({ geometry: "roundRect", position: { left, top: 210, width: 220, height: 150 }, fill: index === 3 ? "#E9F7F5" : C.pale, line: { fill: index === 3 ? C.cyan : C.line, width: 1.2 } }); // Crea un bloque editable para cada etapa.
  addText(slide, value, left + 20, 225, 180, 52, 38, { bold: true, color: index === 3 ? C.cyan : C.navy, align: "center" }); // Añade el número de registros.
  addText(slide, label, left + 18, 286, 184, 48, 18, { color: C.gray, align: "center" }); // Añade la descripción de etapa.
  if (index < flow.length - 1) addText(slide, "›", left + 225, 250, 40, 50, 40, { bold: true, color: C.gold, align: "center" }); // Indica la secuencia sin mezclar los grupos.
  return box; // Conserva el bloque en el archivo editable.
}); // Finaliza el flujo.
addText(slide, "Desarrollo: 31 502 registros y 5 054 UPM\nPrueba: 1 269 UPM, abierta una sola vez", 80, 410, 500, 90, 22, { bold: true, color: C.blue }); // Describe la partición agrupada.
addText(slide, "La separación por UPM evitó repartir viviendas y hogares entre desarrollo y prueba.", 660, 410, 500, 90, 22, { color: C.ink }); // Explica la prevención de contaminación.
addFooter(slide, 4); // Añade la franja institucional.
addNotes(slide, "Fuente: docs/06_informe_preparacion.md y docs/13_informe_evaluacion_unica.md. UPM = unidad primaria de muestreo."); // Registra la fuente del flujo.

slide = presentation.slides.add(); // Crea la diapositiva 5.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Definición operativa y prevención de fuga", "Variables"); // Presenta las decisiones de medición.
addText(slide, "Población elegible", 80, 160, 420, 38, 25, { bold: true, color: C.navy }); // Introduce la elegibilidad.
addText(slide, "15 años o más\nPEA\nNivel superior 8, 9 o 10\nTítulo superior declarado", 80, 215, 420, 210, 22, { color: C.ink }); // Enumera criterios observables.
addText(slide, "Predictores autorizados", 520, 160, 340, 38, 25, { bold: true, color: C.navy }); // Introduce el conjunto predictivo.
addText(slide, "Edad, sexo, estado civil, asistencia educativa, nivel, etnia, provincia, área y mes", 520, 215, 320, 180, 22, { color: C.ink }); // Enumera predictores.
addText(slide, "Variables excluidas", 875, 160, 305, 38, 25, { bold: true, color: C.red }); // Introduce las exclusiones.
addText(slide, "Ingresos, horas, condición de actividad, derivados del resultado, identificadores y variables del diseño", 875, 215, 305, 180, 22, { color: C.ink }); // Explica la protección contra fuga.
addText(slide, "La lista permitida se congeló antes de consultar la prueba.", 80, 500, 1060, 52, 24, { bold: true, color: C.blue, align: "center" }); // Resume la decisión clave.
addFooter(slide, 5); // Añade la franja institucional.
addNotes(slide, "Fuente: config/preparacion_v1.json y docs/03_matriz_inicial_variables.md. La titulación es autodeclarada."); // Registra la fuente de operacionalización.

slide = presentation.slides.add(); // Crea la diapositiva 6.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Dos preguntas requieren dos marcos analíticos", "Método"); // Distingue inferencia y predicción.
addText(slide, "Inferencia poblacional", 90, 160, 480, 42, 28, { bold: true, color: C.blue }); // Titula el bloque inferencial.
addText(slide, "Proporciones ponderadas\nIC 95% con linealización de Taylor\nContrastes por sexo y territorio\nRegresión logística asociativa", 90, 225, 470, 230, 23, { color: C.ink }); // Resume las técnicas inferenciales.
addText(slide, "Predicción fuera de muestra", 690, 160, 480, 42, 28, { bold: true, color: C.cyan }); // Titula el bloque predictivo.
addText(slide, "Cinco pliegues internos por UPM\nModelos y umbrales congelados\nEvaluación única en prueba\nBootstrap de UPM dentro de estrato", 690, 225, 470, 230, 23, { color: C.ink }); // Resume las técnicas predictivas.
addText(slide, "Las asociaciones describen la situación observada. Los modelos clasifican esa situación y no predicen empleo futuro.", 120, 505, 1040, 60, 23, { bold: true, color: C.navy, align: "center" }); // Impide una interpretación causal o temporal.
addFooter(slide, 6); // Añade la franja institucional.
addNotes(slide, "Estándares de reporte recomendados: STROBE para el componente transversal y TRIPOD+AI para el componente predictivo. Collins et al. (2024); von Elm et al. (2007)."); // Cita las guías metodológicas.

slide = presentation.slides.add(); // Crea la diapositiva 7.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Las brechas aparecen antes del ajuste", "Resultados descriptivos"); // Presenta las tasas por grupo.
const rates = addChart(slide, "bar", { position: { left: 80, top: 150, width: 820, height: 420 }, categories: ["Hombre", "Mujer", "Urbana", "Rural", "Sup. no univ.", "Sup. universitaria", "Posgrado"], series: [{ name: "Empleo adecuado (%)", values: [72.10, 66.19, 70.41, 59.44, 63.91, 66.28, 85.58], fill: C.cyan }], barOptions: { direction: "bar", grouping: "clustered", gapWidth: 55 }, hasLegend: false, dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.0\"%\"" }, xAxis: { minimumScale: 0, maximumScale: 100, numberFormatCode: "0\"%\"" }, chartFill: C.white, plotAreaFill: C.white }); // Crea un gráfico nativo de tasas ponderadas.
addText(slide, "−5,91 pp", 950, 195, 220, 60, 38, { bold: true, color: C.red, align: "center" }); // Destaca la brecha por sexo.
addText(slide, "mujer menos hombre", 950, 252, 220, 38, 17, { color: C.gray, align: "center" }); // Etiqueta la brecha.
addText(slide, "−10,97 pp", 950, 350, 220, 60, 38, { bold: true, color: C.red, align: "center" }); // Destaca la brecha rural.
addText(slide, "rural menos urbana", 950, 407, 220, 38, 17, { color: C.gray, align: "center" }); // Etiqueta la brecha.
addFooter(slide, 7); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/eda06_inferencia/06_tabla_cientifica_principal.csv. Tasas ponderadas. El gráfico es nativo y editable."); // Registra la fuente del gráfico.

slide = presentation.slides.add(); // Crea la diapositiva 8.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "La incertidumbre confirma las brechas principales", "Inferencia"); // Presenta los intervalos de confianza.
const contrastBytes = await fs.readFile(path.join(figures, "eda06_inferencia", "06_ic_contrastes_primarios.png")); // Lee la figura de contrastes validada.
addImage(slide, contrastBytes, "Intervalos de confianza de las brechas por sexo y área", 70, 145, 790, 430, "contain"); // Inserta la figura científica.
addText(slide, "Sexo", 900, 180, 250, 36, 22, { bold: true, color: C.navy }); // Identifica el primer resultado.
addText(slide, "La tasa de las mujeres fue menor que la de los hombres.", 900, 225, 260, 100, 20, { color: C.ink }); // Interpreta el contraste por sexo.
addText(slide, "Área", 900, 360, 250, 36, 22, { bold: true, color: C.navy }); // Identifica el segundo resultado.
addText(slide, "La diferencia rural fue mayor y tuvo menor precisión efectiva.", 900, 405, 260, 100, 20, { color: C.ink }); // Interpreta el contraste territorial.
addFooter(slide, 8); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/figures/eda06_inferencia/06_ic_contrastes_primarios.png y reports/eda06_inferencia/02_contrastes_primarios_ic95.csv."); // Registra la fuente de la figura.

slide = presentation.slides.add(); // Crea la diapositiva 9.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Las diferencias persisten tras el ajuste", "Asociaciones"); // Presenta las razones de momios.
const orChart = addChart(slide, "bar", { position: { left: 90, top: 160, width: 780, height: 390 }, categories: ["Mujer", "Rural", "Sup. no universitaria", "Posgrado"], series: [{ name: "Razón de momios", values: [0.73, 0.80, 0.86, 2.88], fill: C.blue, points: [{ idx: 3, fill: C.cyan }] }], barOptions: { direction: "bar", grouping: "clustered", gapWidth: 75 }, hasLegend: false, dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.00" }, xAxis: { minimumScale: 0, maximumScale: 3.2 }, chartFill: C.white, plotAreaFill: C.white }); // Crea un gráfico nativo de asociaciones seleccionadas.
addText(slide, "Referencias", 930, 170, 230, 38, 22, { bold: true, color: C.navy }); // Introduce las categorías de referencia.
addText(slide, "Hombre\nÁrea urbana\nSuperior universitaria", 930, 220, 230, 120, 19, { color: C.gray }); // Enumera las referencias de comparación.
addText(slide, "OR < 1", 930, 370, 230, 36, 24, { bold: true, color: C.red }); // Explica las razones menores a uno.
addText(slide, "Menores momios ajustados de empleo adecuado.", 930, 415, 230, 85, 19, { color: C.ink }); // Interpreta la dirección.
addText(slide, "Asociación no equivale a causalidad.", 930, 520, 230, 34, 18, { bold: true, color: C.blue }); // Añade la cautela central.
addFooter(slide, 9); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/eda07_modelado/09_asociaciones_ajustadas_or.csv. IC 95%: mujer [0,66; 0,81], rural [0,68; 0,94], no universitaria [0,76; 0,98], posgrado [2,42; 3,43]."); // Registra estimaciones completas.

slide = presentation.slides.add(); // Crea la diapositiva 10.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "El boosting lideró durante el desarrollo interno", "Modelado"); // Presenta la validación interna.
const oofChart = addChart(slide, "bar", { position: { left: 100, top: 170, width: 760, height: 350 }, categories: ["Base", "Logística", "Boosting"], series: [{ name: "ROC AUC OOF", values: [0.473, 0.669, 0.689], fill: C.blue, points: [{ idx: 2, fill: C.cyan }] }], barOptions: { direction: "column", grouping: "clustered", gapWidth: 70 }, hasLegend: false, dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.000" }, yAxis: { minimumScale: 0.4, maximumScale: 0.75 }, chartFill: C.white, plotAreaFill: C.white }); // Crea un gráfico nativo del desempeño fuera de pliegue.
addText(slide, "Cinco pliegues", 930, 180, 250, 44, 28, { bold: true, color: C.navy, align: "center" }); // Destaca el esquema de validación.
addText(slide, "agrupados por UPM", 930, 225, 250, 38, 18, { color: C.gray, align: "center" }); // Explica la agrupación.
addText(slide, "Umbrales congelados", 930, 330, 250, 44, 25, { bold: true, color: C.blue, align: "center" }); // Destaca el control contra sobreajuste.
addText(slide, "0,695 logística\n0,705 boosting", 930, 380, 250, 80, 21, { color: C.ink, align: "center" }); // Muestra los umbrales elegidos.
addText(slide, "La prueba permaneció cerrada.", 930, 500, 250, 42, 18, { bold: true, color: C.red, align: "center" }); // Refuerza la separación de prueba.
addFooter(slide, 10); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/eda07_modelado/03_metricas_oof_globales.csv. OOF = predicciones fuera de pliegue."); // Registra la fuente del desarrollo.

slide = presentation.slides.add(); // Crea la diapositiva 11.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "La ventaja del boosting no fue concluyente en prueba", "Evaluación única"); // Presenta el resultado decisivo.
const testChart = addChart(slide, "bar", { position: { left: 90, top: 165, width: 760, height: 370 }, categories: ["Logística", "Boosting"], series: [{ name: "ROC AUC", values: [0.674, 0.684], fill: C.blue, points: [{ idx: 1, fill: C.cyan }] }], barOptions: { direction: "column", grouping: "clustered", gapWidth: 90 }, hasLegend: false, dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.000" }, yAxis: { minimumScale: 0.60, maximumScale: 0.72 }, chartFill: C.white, plotAreaFill: C.white }); // Crea un gráfico nativo del resultado final.
addText(slide, "+0,0106", 920, 190, 250, 60, 42, { bold: true, color: C.cyan, align: "center" }); // Presenta la diferencia puntual.
addText(slide, "boosting menos logística", 920, 245, 250, 40, 18, { color: C.gray, align: "center" }); // Etiqueta la comparación.
addText(slide, "IC 95%", 920, 335, 250, 34, 21, { bold: true, color: C.navy, align: "center" }); // Introduce el intervalo.
addText(slide, "[−0,0097; 0,0303]", 920, 375, 250, 46, 24, { bold: true, color: C.red, align: "center" }); // Muestra que el intervalo incluye cero.
addText(slide, "La mejora puntual puede explicarse por variación muestral.", 910, 465, 270, 80, 19, { color: C.ink, align: "center" }); // Interpreta la incertidumbre.
addFooter(slide, 11); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/eda08_evaluacion/02_metricas_prueba_ic95.csv y 03_comparacion_pareada_modelos.csv. Evaluación ponderada en 7 791 registros."); // Registra las fuentes de prueba.

slide = presentation.slides.add(); // Crea la diapositiva 12.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "La regresión logística conservó mejor calibración", "Calibración"); // Presenta la razón de la selección final.
const calChart = addChart(slide, "bar", { position: { left: 90, top: 165, width: 720, height: 370 }, categories: ["Logística", "Boosting"], series: [{ name: "Pendiente de calibración", values: [0.930, 0.761], fill: C.blue, points: [{ idx: 1, fill: C.cyan }] }], barOptions: { direction: "column", grouping: "clustered", gapWidth: 90 }, hasLegend: false, dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.000" }, yAxis: { minimumScale: 0, maximumScale: 1.05 }, chartFill: C.white, plotAreaFill: C.white }); // Crea un gráfico nativo de pendientes.
addText(slide, "1,000", 900, 175, 250, 55, 38, { bold: true, color: C.gold, align: "center" }); // Presenta el valor ideal.
addText(slide, "pendiente ideal", 900, 225, 250, 38, 18, { color: C.gray, align: "center" }); // Etiqueta el referente.
addText(slide, "Decisión", 900, 335, 250, 36, 24, { bold: true, color: C.navy, align: "center" }); // Introduce la decisión final.
addText(slide, "Logística como referencia\nBoosting como comparador", 880, 385, 290, 95, 22, { bold: true, color: C.blue, align: "center" }); // Resume la elección de modelos.
addText(slide, "La parsimonia y la calibración pesaron junto con la discriminación.", 860, 500, 330, 60, 18, { color: C.ink, align: "center" }); // Explica el criterio integral.
addFooter(slide, 12); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/eda08_evaluacion/07_resumen_evaluacion.json y docs/14_decision_modelos_dashboard.md."); // Registra la fuente de calibración.

slide = presentation.slides.add(); // Crea la diapositiva 13.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "El umbral global produjo sensibilidades desiguales", "Desempeño por grupos"); // Presenta las brechas de error.
const gapChart = addChart(slide, "bar", { position: { left: 80, top: 160, width: 820, height: 390 }, categories: ["Mujer − hombre", "Rural − urbana"], series: [{ name: "Brecha de sensibilidad, pp", values: [-15.3, -9.0], fill: C.red }], barOptions: { direction: "bar", grouping: "clustered", gapWidth: 100 }, hasLegend: false, dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.0" }, xAxis: { minimumScale: -20, maximumScale: 2 }, chartFill: C.white, plotAreaFill: C.white }); // Crea un gráfico nativo de brechas para boosting.
addText(slide, "Rural − urbana", 100, 245, 220, 38, 17, { bold: true, color: C.gray }); // Identifica la barra superior que el motor de gráficos no rotuló al renderizar.
addText(slide, "Mujer − hombre", 100, 435, 220, 38, 17, { bold: true, color: C.gray }); // Identifica la barra inferior y mantiene editable la etiqueta.
addText(slide, "ROC AUC similar por sexo", 940, 180, 240, 62, 24, { bold: true, color: C.navy, align: "center" }); // Distingue ordenamiento y sensibilidad.
addText(slide, "La brecha aparece principalmente en el punto de operación global.", 930, 260, 260, 100, 19, { color: C.ink, align: "center" }); // Interpreta el patrón por sexo.
addText(slide, "Mayor AUC rural", 940, 400, 240, 48, 24, { bold: true, color: C.cyan, align: "center" }); // Destaca la aparente paradoja territorial.
addText(slide, "Mejor discriminación coexistió con menor sensibilidad rural.", 930, 455, 260, 90, 19, { color: C.ink, align: "center" }); // Explica la necesidad de varias métricas.
addFooter(slide, 13); // Añade la franja institucional.
addNotes(slide, "Fuente: reports/eda08_evaluacion/06_brechas_desempeno_ic95.csv. Brechas del modelo boosting, con el umbral global congelado."); // Registra la fuente de equidad.

slide = presentation.slides.add(); // Crea la diapositiva 14.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Observatorio de educación superior y empleo", "Producto aplicado"); // Presenta el dashboard final.
addImage(slide, dashboardBytes, "Captura del dashboard Streamlit del proyecto", 70, 145, 860, 460, "contain"); // Inserta la captura verificada del dashboard.
addText(slide, "Filtros", 970, 155, 220, 34, 22, { bold: true, color: C.navy }); // Introduce la exploración.
addText(slide, "Provincia, sexo, edad, área, nivel y mes", 970, 198, 220, 90, 18, { color: C.ink }); // Enumera filtros principales.
addText(slide, "Precisión visible", 970, 330, 220, 34, 22, { bold: true, color: C.navy }); // Introduce la incertidumbre.
addText(slide, "n, UPM, IC 95% y coeficiente de variación", 970, 373, 220, 85, 18, { color: C.ink }); // Enumera indicadores de precisión.
addText(slide, "Sin identificadores", 970, 500, 220, 34, 22, { bold: true, color: C.cyan }); // Destaca la privacidad.
addText(slide, "39 551 filas analíticas y 21 variables seguras", 970, 540, 220, 55, 18, { color: C.ink }); // Resume el conjunto de publicación.
addFooter(slide, 14); // Añade la franja institucional.
addNotes(slide, "Producto: dashboard/app.py. La captura corresponde a la vista Panorama en localhost:8501. La base del dashboard excluye identificadores de persona, hogar y vivienda."); // Documenta el producto aplicado.

slide = presentation.slides.add(); // Crea la diapositiva 15.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Alcance, limitaciones y ruta de publicación", "Discusión"); // Presenta los límites y siguientes pasos.
addText(slide, "Qué permite afirmar", 80, 160, 320, 38, 25, { bold: true, color: C.blue }); // Introduce el alcance válido.
addText(slide, "Brechas ponderadas\nAsociaciones ajustadas\nClasificación contemporánea\nDesempeño por grupos", 80, 215, 320, 220, 22, { color: C.ink }); // Resume afirmaciones permitidas.
addText(slide, "Límites", 475, 160, 300, 38, 25, { bold: true, color: C.red }); // Introduce las limitaciones.
addText(slide, "Diseño transversal\nTitulación autodeclarada\nValidación interna\nUna partición de prueba", 475, 215, 300, 220, 22, { color: C.ink }); // Resume límites principales.
addText(slide, "Antes del artículo", 835, 160, 350, 38, 25, { bold: true, color: C.cyan }); // Introduce la ruta de publicación.
addText(slide, "Validación temporal\nSensibilidad de la definición educativa\nListas STROBE y TRIPOD+AI\nEvaluación PROBAST+AI", 835, 215, 350, 220, 22, { color: C.ink }); // Enumera tareas publicables.
addText(slide, "La contribución científica une brechas laborales, calibración y diferencias de error.", 100, 515, 1080, 52, 24, { bold: true, color: C.navy, align: "center" }); // Formula la contribución propuesta.
addFooter(slide, 15); // Añade la franja institucional.
addNotes(slide, "Referencias metodológicas: Collins et al. (2024), Moons et al. (2025) y von Elm et al. (2007). TRIPOD+AI y PROBAST+AI se adaptan con cautela a un problema no clínico."); // Registra la base metodológica.

slide = presentation.slides.add(); // Crea la diapositiva 16.
slide.background.fill = C.white; // Mantiene el fondo blanco.
addTitle(slide, "Conclusiones", "Cierre"); // Abre el cierre de la presentación.
addText(slide, "1", 90, 165, 60, 60, 40, { bold: true, color: C.cyan, align: "center" }); // Numera la primera conclusión.
addText(slide, "Las brechas por sexo y área persisten dentro de la población titulada.", 170, 160, 950, 72, 26, { bold: true, color: C.navy }); // Presenta la conclusión sustantiva.
addText(slide, "2", 90, 285, 60, 60, 40, { bold: true, color: C.cyan, align: "center" }); // Numera la segunda conclusión.
addText(slide, "El boosting no demostró una mejora concluyente en la prueba reservada.", 170, 280, 950, 72, 26, { bold: true, color: C.navy }); // Presenta la conclusión predictiva.
addText(slide, "3", 90, 405, 60, 60, 40, { bold: true, color: C.cyan, align: "center" }); // Numera la tercera conclusión.
addText(slide, "La calibración y las brechas de sensibilidad cambian la decisión sobre el modelo principal.", 170, 400, 950, 86, 26, { bold: true, color: C.navy }); // Presenta la conclusión de evaluación responsable.
addText(slide, "Preguntas", 450, 545, 380, 55, 34, { bold: true, color: C.blue, align: "center" }); // Invita a la discusión final.
addFooter(slide, 16); // Añade la franja institucional.
addNotes(slide, "Mensaje de cierre: la regresión logística queda como referencia por parsimonia, calibración y desempeño competitivo; el boosting permanece como comparador."); // Conserva la conclusión oral.

const candidatePath = path.join(TMP_DIR, "candidate.pptx"); // Define el archivo candidato privado.
await (await PresentationFile.exportPptx(presentation)).save(candidatePath); // Exporta el candidato con objetos editables.
const requirements = { explicitTotalSlideCount: 16, requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [7, 9, 10, 11, 12, 13], materializeLiteralChartWorkbooks: true }; // Declara los requisitos y autoriza libros editables para los gráficos literales nuevos.
const fontPolicy = { basis: "design", families: [family] }; // Declara que la fuente fue elegida como decisión de diseño.
const expectedSlideSizeEmu = "12192000,6858000"; // Declara el tamaño panorámico de la presentación.
const stagingDir = path.join(TMP_DIR, ".codex-finalizer"); // Define la carpeta privada del validador.
await fs.mkdir(stagingDir, { recursive: true }); // Crea la carpeta del validador.
await finalizePresentation({ ...requirements, workspaceDir, candidatePath, finalPath: FINAL_PPTX, pythonExecutable: RUNTIME_PYTHON, integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"), layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"), layoutArgs: ["--expected-slide-size-emu", expectedSlideSizeEmu, "--validate-bullet-geometry", "--validate-heading-fit"], requiredNativeTableOwnerSlides: [], fontPolicy, verifyArtifactToolImport: true, receiptPath: path.join(stagingDir, "Presentacion_final_ENEMDU_2025.validation.json") }); // Valida estructura, geometría, fuentes y editabilidad antes de escribir el archivo final.
console.log(FINAL_PPTX); // Informa la ruta final para la revisión visual.
