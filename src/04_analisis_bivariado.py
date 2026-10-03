# ETAPA 5 DEL EDA: empleo adecuado por sexo, área, edad, educación y territorio.
# ARCHIVO: 04_analisis_bivariado.py; calcula tasas y diferencias ponderadas sin inferencia todavía.
# BLOQUE 1: dependencias, rutas y configuración.
import hashlib  # Calcula huellas de integridad.
import json  # Lee decisiones y escribe resúmenes.
from pathlib import Path  # Construye rutas portables.
import matplotlib  # Configura gráficos sin interfaz visual.
matplotlib.use('Agg')  # Permite ejecución automática.
import matplotlib.pyplot as plt  # Dibuja figuras científicas.
import numpy as np  # Realiza cálculos numéricos.
import pandas as pd  # Lee y resume tablas.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
DATOS = RAIZ / 'data/processed'  # Localiza las bases tratadas.
SALIDAS = RAIZ / 'reports/eda05_bivariado'  # Define tablas de salida.
FIGURAS = RAIZ / 'reports/figures/eda05_bivariado'  # Define figuras de salida.
INFERENCIA = DATOS / 'inferencia'  # Define el producto para diseño muestral.
SALIDAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de tablas.
FIGURAS.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de gráficos.
INFERENCIA.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de inferencia.
CONFIG = json.loads((RAIZ / 'config/eda05_bivariado_v1.json').read_text(encoding='utf-8'))  # Recupera decisiones congeladas.
ETIQUETAS = json.loads((DATOS / 'etiquetas_oficiales.json').read_text(encoding='utf-8'))  # Recupera etiquetas oficiales.
AZUL = '#0072B2'  # Usa azul accesible.
NARANJA = '#E69F00'  # Usa naranja accesible.
VERDE = '#009E73'  # Usa verde accesible.
ROJO = '#D55E00'  # Usa rojo anaranjado accesible.
GRIS = '#6B7280'  # Usa gris para la referencia total.
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 12, 'axes.labelsize': 9})  # Fija estilo reproducible.

# BLOQUE 2: funciones de etiquetas, cálculo y exportación.
def sha256(ruta):  # Calcula SHA-256 de un archivo.
    h = hashlib.sha256()  # Inicializa el acumulador.
    with ruta.open('rb') as archivo:  # Abre el archivo sin modificarlo.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Lee en bloques de un megabyte.
            h.update(bloque)  # Incorpora cada bloque.
    return h.hexdigest()  # Devuelve la huella hexadecimal.

def limpiar_codigo(valor):  # Normaliza códigos categóricos.
    texto = str(valor).strip()  # Convierte el código a texto.
    return texto[:-2] if texto.endswith('.0') else texto  # Retira solamente un decimal artificial.

def etiqueta(variable, valor):  # Traduce códigos con metadatos oficiales.
    codigo = limpiar_codigo(valor)  # Normaliza el código observado.
    if variable == 'grupo_edad':  # Reconoce intervalos creados por el estudio.
        return codigo  # Conserva la etiqueta del intervalo.
    catalogo = ETIQUETAS.get(variable, {})  # Recupera el catálogo correspondiente.
    opciones = [codigo, f'{codigo}.0']  # Contempla las dos formas de los códigos oficiales.
    hallada = next((catalogo[opcion] for opcion in opciones if opcion in catalogo), codigo)  # Selecciona etiqueta o código.
    return str(hallada).strip()  # Retira espacios exteriores.

def tasa_ponderada(tabla):  # Calcula la proporción ponderada de empleo adecuado.
    suma_pesos = tabla['fexp'].sum()  # Suma pesos del denominador.
    suma_adecuado = (tabla['fexp'] * tabla['adecuado_descriptivo']).sum()  # Suma pesos del numerador.
    return 100 * suma_adecuado / suma_pesos  # Devuelve porcentaje ponderado.

def resumir_grupos(tabla, variable, tasa_total):  # Resume tasas, tamaños y diferencias de una variable.
    filas = []  # Inicializa una fila por categoría.
    referencia = CONFIG['referencias'].get(variable)  # Recupera el código de referencia predefinido.
    for codigo, grupo in tabla.groupby(variable, observed=True, dropna=False):  # Recorre categorías observadas.
        codigo_texto = limpiar_codigo(codigo)  # Normaliza la categoría.
        peso = grupo['fexp']  # Obtiene pesos del grupo.
        resultado = grupo['adecuado_descriptivo']  # Obtiene el indicador binario.
        tasa = tasa_ponderada(grupo)  # Calcula la tasa ponderada.
        n_efectivo = peso.sum() ** 2 / (peso.pow(2).sum())  # Calcula tamaño efectivo de Kish debido solo a pesos.
        upm_estrato = grupo.groupby('estrato', observed=True)['upm'].nunique()  # Cuenta UPM observadas por estrato dentro del subgrupo.
        filas.append({'variable': variable, 'codigo': codigo_texto, 'etiqueta': etiqueta(variable, codigo_texto), 'n': len(grupo), 'n_adecuado': int(resultado.sum()), 'porcentaje_no_ponderado': 100 * resultado.mean(), 'suma_pesos': peso.sum(), 'suma_pesos_adecuado': (peso * resultado).sum(), 'porcentaje_ponderado': tasa, 'diferencia_total_pp': tasa - tasa_total, 'upm': grupo['upm'].nunique(), 'estratos': grupo['estrato'].nunique(), 'n_efectivo_pesos_kish': n_efectivo, 'estratos_una_upm_en_subgrupo': int((upm_estrato == 1).sum()), 'codigo_referencia': referencia})  # Registra estimación y diagnóstico.
    resumen = pd.DataFrame(filas)  # Convierte filas en tabla.
    if referencia is None:  # Trata territorio sin provincia de referencia arbitraria.
        resumen['etiqueta_referencia'] = 'Total nacional del dominio'  # Declara la comparación total.
        resumen['diferencia_referencia_pp'] = resumen['diferencia_total_pp']  # Usa diferencia frente al total.
    else:  # Trata variables con referencia sustantiva.
        tasa_referencia = resumen.loc[resumen['codigo'] == referencia, 'porcentaje_ponderado'].iloc[0]  # Recupera la tasa de referencia.
        etiqueta_referencia = resumen.loc[resumen['codigo'] == referencia, 'etiqueta'].iloc[0]  # Recupera su nombre.
        resumen['etiqueta_referencia'] = etiqueta_referencia  # Documenta el grupo base.
        resumen['diferencia_referencia_pp'] = resumen['porcentaje_ponderado'] - tasa_referencia  # Calcula puntos porcentuales.
    return resumen  # Devuelve el resumen completo.

def guardar_figura(figura, nombre):  # Exporta un gráfico en formatos complementarios.
    figura.savefig(FIGURAS / f'{nombre}.png', dpi=200, bbox_inches='tight', facecolor='white')  # Guarda PNG para documentos.
    figura.savefig(FIGURAS / f'{nombre}.svg', bbox_inches='tight', facecolor='white')  # Guarda SVG editable.
    plt.close(figura)  # Libera memoria.

def nota(figura, texto):  # Añade fuente, denominador y limitación.
    figura.text(0.01, 0.005, texto, ha='left', va='bottom', fontsize=7, color='#374151')  # Escribe una nota homogénea.

def grafico_tasas(datos, titulo, nombre, color=AZUL, ordenar=False, alto=None):  # Dibuja tasas ponderadas sin intervalos.
    grafico = datos.sort_values('porcentaje_ponderado', ascending=True).copy() if ordenar else datos.iloc[::-1].copy()  # Define el orden visual.
    altura = alto if alto else max(4.2, 0.38 * len(grafico) + 1.8)  # Ajusta el lienzo al número de grupos.
    figura, eje = plt.subplots(figsize=(8.6, altura))  # Crea el gráfico.
    eje.barh(grafico['etiqueta'], grafico['porcentaje_ponderado'], color=color)  # Dibuja tasas ponderadas.
    eje.axvline(TASA_TOTAL, color=GRIS, linestyle='--', linewidth=1.2, label=f'Total: {TASA_TOTAL:.1f}%')  # Añade referencia global.
    eje.set_xlim(0, 100)  # Usa la escala completa de una proporción.
    eje.set_xlabel('Empleo adecuado ponderado (%)')  # Define la métrica.
    eje.set_title(titulo, loc='left', fontweight='bold')  # Define el título.
    eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Facilita comparación.
    eje.set_axisbelow(True)  # Coloca la cuadrícula detrás.
    eje.legend(frameon=False, loc='lower right')  # Identifica la referencia.
    for parche, valor in zip(eje.patches, grafico['porcentaje_ponderado']):  # Recorre barras y tasas.
        eje.text(min(valor + 0.6, 97), parche.get_y() + parche.get_height() / 2, f'{valor:.1f}', va='center', fontsize=8)  # Etiqueta valores.
    nota(figura, 'Fuente: ENEMDU anual 2025. PEA de 15+ con nivel superior y título (n=39 551). fexp. Diferencias descriptivas; IC de diseño pendientes.')  # Declara alcance.
    figura.tight_layout(rect=(0, 0.045, 1, 1))  # Reserva espacio para la nota.
    guardar_figura(figura, nombre)  # Exporta el gráfico.

# BLOQUE 3: carga del dominio y construcción del grupo de edad.
columnas = ['adecuado_descriptivo', 'fexp', 'estrato', 'upm', 'p02', 'area', 'edad_limite_inferior', 'p10a', 'prov']  # Define campos necesarios.
tipos = {'adecuado_descriptivo': 'Int8', 'fexp': 'float64', 'estrato': 'string', 'upm': 'string', 'p02': 'string', 'area': 'string', 'edad_limite_inferior': 'Int16', 'p10a': 'string', 'prov': 'string'}  # Conserva códigos y tipos.
dominio = pd.read_csv(DATOS / 'dominio_educacion_superior.csv', usecols=columnas, dtype=tipos, encoding='utf-8-sig')  # Lee el dominio descriptivo completo.
assert len(dominio) == 39551  # Confirma el denominador previsto.
assert dominio['adecuado_descriptivo'].notna().all()  # Exige resultado descriptivo completo.
assert dominio['fexp'].gt(0).all()  # Exige pesos positivos.
intervalos = np.array(CONFIG['intervalos_edad'], dtype=float)  # Recupera cortes de edad.
etiquetas_edad = [f'{int(a)}–{int(b - 1)}' for a, b in zip(intervalos[:-2], intervalos[1:-1])] + ['98+']  # Construye rótulos y categoría abierta.
dominio['grupo_edad'] = pd.cut(dominio['edad_limite_inferior'], bins=intervalos, labels=etiquetas_edad, right=False, include_lowest=True).astype('string')  # Agrupa edades sin tratar 98+ como exacta.
TASA_TOTAL = tasa_ponderada(dominio)  # Calcula el punto de referencia del dominio.
total = pd.DataFrame([{'variable': 'total', 'codigo': 'total', 'etiqueta': 'Total del dominio', 'n': len(dominio), 'n_adecuado': int(dominio['adecuado_descriptivo'].sum()), 'porcentaje_no_ponderado': 100 * dominio['adecuado_descriptivo'].mean(), 'suma_pesos': dominio['fexp'].sum(), 'suma_pesos_adecuado': (dominio['fexp'] * dominio['adecuado_descriptivo']).sum(), 'porcentaje_ponderado': TASA_TOTAL, 'diferencia_total_pp': 0.0, 'upm': dominio['upm'].nunique(), 'estratos': dominio['estrato'].nunique(), 'n_efectivo_pesos_kish': dominio['fexp'].sum() ** 2 / dominio['fexp'].pow(2).sum(), 'estratos_una_upm_en_subgrupo': int((dominio.groupby('estrato')['upm'].nunique() == 1).sum()), 'codigo_referencia': 'total', 'etiqueta_referencia': 'Total del dominio', 'diferencia_referencia_pp': 0.0}])  # Registra la tasa total y diagnósticos.

# BLOQUE 4: tasas y diferencias para las cinco dimensiones.
resumenes = {variable: resumir_grupos(dominio, variable, TASA_TOTAL) for variable in CONFIG['variables']}  # Calcula cada dimensión.
tasas = pd.concat([total] + [resumenes[variable] for variable in CONFIG['variables']], ignore_index=True)  # Reúne resultados en formato largo.
tasas.to_csv(SALIDAS / '01_tasas_empleo_adecuado_grupos.csv', index=False, encoding='utf-8-sig')  # Exporta la tabla principal editable.
diferencias = tasas.loc[tasas['variable'] != 'total', ['variable', 'codigo', 'etiqueta', 'porcentaje_ponderado', 'diferencia_total_pp', 'codigo_referencia', 'etiqueta_referencia', 'diferencia_referencia_pp', 'n', 'upm', 'estratos']].copy()  # Selecciona comparaciones descriptivas.
diferencias.to_csv(SALIDAS / '02_diferencias_ponderadas_pp.csv', index=False, encoding='utf-8-sig')  # Exporta diferencias en puntos porcentuales.
diagnostico = tasas[['variable', 'codigo', 'etiqueta', 'n', 'upm', 'estratos', 'n_efectivo_pesos_kish', 'estratos_una_upm_en_subgrupo']].copy()  # Selecciona información de precisión futura.
diagnostico['advertencia'] = np.where(diagnostico['n'] < 100, 'n menor que 100; interpretar con cautela', np.where(diagnostico['estratos_una_upm_en_subgrupo'] > 0, 'algunos estratos tienen una UPM con casos; conservar diseño completo', 'sin alerta descriptiva'))  # Añade alertas transparentes.
diagnostico.to_csv(SALIDAS / '03_diagnostico_diseno_grupos.csv', index=False, encoding='utf-8-sig')  # Exporta diagnóstico para inferencia.

# BLOQUE 5: archivo compacto con todas las filas para la inferencia posterior.
columnas_diseno = ['estrato', 'upm', 'fexp', 'dominio_estudio', 'adecuado_descriptivo', 'p02', 'area', 'edad_limite_inferior', 'p10a', 'prov']  # Define insumos mínimos del diseño.
tipos_diseno = {'estrato': 'string', 'upm': 'string', 'fexp': 'float64', 'dominio_estudio': 'boolean', 'adecuado_descriptivo': 'Int8', 'p02': 'string', 'area': 'string', 'edad_limite_inferior': 'Int16', 'p10a': 'string', 'prov': 'string'}  # Define tipos explícitos.
diseno = pd.read_csv(DATOS / 'personas_tratada_completa.csv.gz', usecols=columnas_diseno, dtype=tipos_diseno, encoding='utf-8-sig')  # Lee la muestra completa tratada.
diseno['grupo_edad'] = pd.cut(diseno['edad_limite_inferior'], bins=intervalos, labels=etiquetas_edad, right=False, include_lowest=True).astype('string')  # Crea el mismo grupo de edad.
diseno['numerador_adecuado'] = (diseno['dominio_estudio'].fillna(False) & diseno['adecuado_descriptivo'].eq(1)).astype('Int8')  # Crea contribución al numerador.
diseno['denominador_dominio'] = diseno['dominio_estudio'].fillna(False).astype('Int8')  # Crea contribución al denominador.
ruta_diseno = INFERENCIA / 'diseno_bivariado.csv.gz'  # Define el producto compacto.
diseno.to_csv(ruta_diseno, index=False, encoding='utf-8-sig', compression={'method': 'gzip', 'mtime': 0})  # Guarda todas las filas con compresión reproducible.
control_diseno = pd.DataFrame([{'filas': len(diseno), 'estratos': diseno['estrato'].nunique(), 'upm': diseno['upm'].nunique(), 'grados_libertad_diseno': diseno['upm'].nunique() - diseno['estrato'].nunique(), 'filas_dominio': int(diseno['denominador_dominio'].sum()), 'numerador_adecuado': int(diseno['numerador_adecuado'].sum()), 'pesos_positivos': bool(diseno['fexp'].gt(0).all()), 'sha256': sha256(ruta_diseno)}])  # Resume integridad del archivo.
control_diseno.to_csv(SALIDAS / '04_control_archivo_inferencia.csv', index=False, encoding='utf-8-sig')  # Exporta el control del diseño.

# BLOQUE 6: gráficos de tasas y diferencias descriptivas.
grafico_tasas(resumenes['p02'], 'Empleo adecuado por sexo', '01_empleo_adecuado_sexo', AZUL)  # Grafica sexo.
grafico_tasas(resumenes['area'], 'Empleo adecuado por área de residencia', '02_empleo_adecuado_area', VERDE)  # Grafica área.
grafico_tasas(resumenes['grupo_edad'], 'Empleo adecuado por grupo de edad', '03_empleo_adecuado_edad', NARANJA, alto=7.0)  # Grafica edad.
grafico_tasas(resumenes['p10a'], 'Empleo adecuado por nivel de instrucción reportado', '04_empleo_adecuado_educacion', ROJO)  # Grafica educación.
grafico_tasas(resumenes['prov'], 'Empleo adecuado por provincia', '05_empleo_adecuado_provincia', AZUL, ordenar=True, alto=9.0)  # Grafica territorio ordenado.
comparacion = pd.concat([resumenes['p02'], resumenes['area']], ignore_index=True)  # Reúne comparaciones principales.
comparacion = comparacion.loc[comparacion['diferencia_referencia_pp'].abs() > 1e-12].copy()  # Omite los grupos de referencia iguales a cero.
figura, eje = plt.subplots(figsize=(8.2, 4.5))  # Crea el gráfico de brechas.
colores = [VERDE if valor >= 0 else ROJO for valor in comparacion['diferencia_referencia_pp']]  # Distingue signos sin implicar causalidad.
rotulos = comparacion['variable'].map({'p02': 'Sexo', 'area': 'Área'}) + ': ' + comparacion['etiqueta'] + ' vs. ' + comparacion['etiqueta_referencia']  # Construye comparaciones explícitas.
eje.barh(rotulos, comparacion['diferencia_referencia_pp'], color=colores)  # Dibuja diferencias en puntos porcentuales.
eje.axvline(0, color='#111827', linewidth=0.8)  # Marca ausencia de diferencia.
eje.set_xlabel('Diferencia ponderada (puntos porcentuales)')  # Define la unidad correcta.
eje.set_title('Brechas descriptivas por sexo y área', loc='left', fontweight='bold')  # Titula el gráfico.
eje.grid(axis='x', color='#D1D5DB', linewidth=0.6)  # Añade guías.
eje.set_axisbelow(True)  # Coloca guías detrás.
for parche, valor in zip(eje.patches, comparacion['diferencia_referencia_pp']):  # Recorre diferencias.
    eje.text(valor + (0.2 if valor >= 0 else -0.2), parche.get_y() + parche.get_height() / 2, f'{valor:+.1f}', ha='left' if valor >= 0 else 'right', va='center', fontsize=8)  # Etiqueta magnitud y signo.
nota(figura, 'Fuente: ENEMDU anual 2025. Diferencias ponderadas sin IC ni prueba de hipótesis; no implican causalidad.')  # Declara límite.
figura.tight_layout(rect=(0, 0.06, 1, 1))  # Ajusta la figura.
guardar_figura(figura, '06_brechas_sexo_area')  # Exporta brechas.

# BLOQUE 7: resumen, manifiesto y controles.
sexo = resumenes['p02'].set_index('codigo')  # Indexa tasas por sexo.
area = resumenes['area'].set_index('codigo')  # Indexa tasas por área.
educacion = resumenes['p10a'].set_index('codigo')  # Indexa tasas por nivel.
provincia = resumenes['prov'].sort_values('porcentaje_ponderado')  # Ordena provincias.
resumen = {'estado': 'completado', 'filas_dominio': len(dominio), 'tasa_total_ponderada': TASA_TOTAL, 'tasa_hombres': float(sexo.loc['1', 'porcentaje_ponderado']), 'tasa_mujeres': float(sexo.loc['2', 'porcentaje_ponderado']), 'brecha_mujeres_menos_hombres_pp': float(sexo.loc['2', 'diferencia_referencia_pp']), 'tasa_urbana': float(area.loc['1', 'porcentaje_ponderado']), 'tasa_rural': float(area.loc['2', 'porcentaje_ponderado']), 'brecha_rural_menos_urbana_pp': float(area.loc['2', 'diferencia_referencia_pp']), 'tasa_superior_no_universitaria': float(educacion.loc['8', 'porcentaje_ponderado']), 'tasa_superior_universitaria': float(educacion.loc['9', 'porcentaje_ponderado']), 'tasa_posgrado': float(educacion.loc['10', 'porcentaje_ponderado']), 'provincia_tasa_minima': provincia.iloc[0]['etiqueta'], 'tasa_provincial_minima': float(provincia.iloc[0]['porcentaje_ponderado']), 'provincia_tasa_maxima': provincia.iloc[-1]['etiqueta'], 'tasa_provincial_maxima': float(provincia.iloc[-1]['porcentaje_ponderado']), 'filas_archivo_inferencia': len(diseno), 'upm_archivo_inferencia': diseno['upm'].nunique(), 'estratos_archivo_inferencia': diseno['estrato'].nunique(), 'grados_libertad_diseno': diseno['upm'].nunique() - diseno['estrato'].nunique(), 'intervalos_confianza_calculados': False, 'prueba_predictiva_evaluada': False}  # Consolida hallazgos descriptivos.
(SALIDAS / '00_resumen_eda05.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el resumen.
productos = sorted(list(SALIDAS.glob('0*.csv')) + list(FIGURAS.glob('*.*')) + [ruta_diseno])  # Reúne productos materiales.
manifiesto = pd.DataFrame([{'archivo': str(ruta.relative_to(RAIZ)).replace('\\', '/'), 'bytes': ruta.stat().st_size, 'sha256': sha256(ruta)} for ruta in productos])  # Registra tamaños y huellas.
manifiesto.to_csv(SALIDAS / '05_manifiesto_productos.csv', index=False, encoding='utf-8-sig')  # Exporta trazabilidad.
assert np.isclose(total.loc[0, 'porcentaje_ponderado'], TASA_TOTAL)  # Verifica consistencia total.
assert tasas['porcentaje_ponderado'].between(0, 100).all()  # Exige tasas válidas.
assert len(diseno) == 334786 and diseno['denominador_dominio'].sum() == len(dominio)  # Reconcilia muestra y dominio.
assert diseno['numerador_adecuado'].sum() == dominio['adecuado_descriptivo'].sum()  # Reconcilia numerador.
verificacion = {'estado': 'verificado', 'tasas_en_rango': True, 'filas_dominio_reconciliadas': True, 'numerador_reconciliado': True, 'archivo_inferencia_con_muestra_completa': True, 'intervalos_confianza_calculados': False, 'prueba_predictiva_evaluada': False, 'figuras_png': len(list(FIGURAS.glob('*.png'))), 'figuras_svg': len(list(FIGURAS.glob('*.svg')))}  # Reúne controles automáticos.
(SALIDAS / '06_verificacion_eda05.json').write_text(json.dumps(verificacion, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda evidencia.
print(json.dumps(resumen, ensure_ascii=False, indent=2))  # Presenta resultados al ejecutar.
