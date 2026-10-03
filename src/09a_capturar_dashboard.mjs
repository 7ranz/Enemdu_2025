import fs from "node:fs/promises"; // Gestiona la carpeta de salida de la captura.
import path from "node:path"; // Construye rutas locales de forma segura.
import { chromium } from "file:///C:/Users/franz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs"; // Abre el navegador incluido en el entorno de trabajo.

const raiz = path.resolve(import.meta.dirname, ".."); // Localiza la raíz del proyecto ENEMDU.
const salida = path.join(raiz, "assets", "captura_dashboard.png"); // Define la imagen que utilizará la presentación.
await fs.mkdir(path.dirname(salida), { recursive: true }); // Asegura que exista la carpeta de activos.
const navegador = await chromium.launch({ headless: true, channel: "msedge" }); // Inicia Microsoft Edge sin ventana visible.
const pagina = await navegador.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 }); // Fija un lienzo amplio y reproducible.
await pagina.goto("http://localhost:8501/", { waitUntil: "networkidle", timeout: 120000 }); // Abre el dashboard local y espera su carga.
await pagina.waitForTimeout(5000); // Permite que Streamlit termine de dibujar gráficos y fuentes.
await pagina.screenshot({ path: salida, fullPage: false }); // Captura la vista inicial profesional del observatorio.
await navegador.close(); // Cierra el navegador y libera recursos.
console.log(salida); // Informa la ruta creada para la presentación.
