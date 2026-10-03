# ETAPA 9: dashboard profesional del Observatorio ENEMDU 2025.
# ARCHIVO: app.py; integra filtros, inferencia, ingresos, asociaciones y modelos.
# BLOQUE 1: dependencias, rutas y configuración visual.
import json  # Lee la configuración científica.
from pathlib import Path  # Maneja rutas portables.
import numpy as np  # Ejecuta cálculos numéricos simples.
import pandas as pd  # Maneja tablas del dashboard.
import plotly.express as px  # Genera gráficos interactivos de alto nivel.
import plotly.graph_objects as go  # Genera gráficos científicos personalizados.
import streamlit as st  # Construye la aplicación web en Python.
from metricas import aplicar_filtros, contrastar_grupos, cuantil_ponderado, estimar_tasa, histograma_ponderado, preparar_diseno  # Importa el motor estadístico auditado.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto.
CONFIG = json.loads((RAIZ / 'config/dashboard_v1.json').read_text(encoding='utf-8'))  # Lee textos y decisiones del tablero.
AZUL = '#0B5C7A'  # Define azul institucional oscuro.
CELESTE = '#2A9D8F'  # Define acento verde azulado.
NARANJA = '#E9A23B'  # Define acento para comparaciones.
ROJO = '#C94C4C'  # Define alertas.
GRIS = '#64748B'  # Define texto secundario.
FONDO = '#F5F7FA'  # Define fondo suave.
st.set_page_config(page_title='Observatorio ENEMDU 2025', page_icon='📊', layout='wide', initial_sidebar_state='expanded')  # Configura la ventana.
st.markdown("""<style>
.stApp {background: #F5F7FA; color: #172033;}
[data-testid="stSidebar"] {background: #FFFFFF; border-right: 1px solid #DCE3EA;}
.hero {background: linear-gradient(120deg,#073B4C,#0B5C7A 55%,#2A9D8F); padding: 1.45rem 1.7rem; border-radius: 18px; color: white; margin-bottom: 1rem; box-shadow: 0 8px 24px rgba(7,59,76,.16);}
.hero h1 {font-size: 1.8rem; line-height: 1.15; margin: 0 0 .35rem 0;}
.hero p {margin: 0; opacity: .9;}
.eyebrow {font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .09em; color: #A7F3D0; margin-bottom: .45rem;}
.panel-note {background: white; border-left: 4px solid #2A9D8F; padding: .8rem 1rem; border-radius: 8px; color: #334155; margin: .5rem 0 1rem 0;}
.precision-alta {color:#087F5B;font-weight:700}.precision-moderada {color:#B56A00;font-weight:700}.precision-precaución {color:#B42318;font-weight:700}
div[data-testid="stMetric"] {background:white;border:1px solid #E2E8F0;padding:1rem;border-radius:14px;box-shadow:0 3px 12px rgba(15,23,42,.05)}
div[data-testid="stMetricLabel"] {color:#475569;font-weight:600}
.footer {font-size:.78rem;color:#64748B;border-top:1px solid #DCE3EA;padding-top:1rem;margin-top:1.4rem}
</style>""", unsafe_allow_html=True)  # Aplica una identidad visual profesional.

# BLOQUE 2: carga en caché de datos y resultados congelados.
@st.cache_data(show_spinner='Cargando base analítica…')  # Evita releer archivos en cada interacción.
def cargar_datos():  # Reúne datos del observatorio.
    datos = pd.read_parquet(RAIZ / 'data/dashboard/observatorio_enemdu_2025.parquet')  # Lee microdatos sin identificadores.
    pares = pd.read_parquet(RAIZ / 'data/dashboard/diseno_upm.parquet')  # Lee todas las UPM del diseño.
    asociaciones = pd.read_csv(RAIZ / 'reports/eda07_modelado/09_asociaciones_ajustadas_or.csv')  # Lee razones de momios ajustadas.
    wald = pd.read_csv(RAIZ / 'reports/eda07_modelado/10_pruebas_wald_ajustadas.csv')  # Lee pruebas globales.
    globales = pd.read_csv(RAIZ / 'reports/eda08_evaluacion/01_metricas_prueba_globales.csv')  # Lee métricas finales.
    intervalos = pd.read_csv(RAIZ / 'reports/eda08_evaluacion/02_metricas_prueba_ic95.csv')  # Lee IC de prueba.
    comparacion = pd.read_csv(RAIZ / 'reports/eda08_evaluacion/03_comparacion_pareada_modelos.csv')  # Lee diferencias entre modelos.
    calibracion = pd.read_csv(RAIZ / 'reports/eda08_evaluacion/04_calibracion_prueba_deciles.csv')  # Lee calibración final.
    grupos = pd.read_csv(RAIZ / 'reports/eda08_evaluacion/05_metricas_prueba_por_grupo.csv', dtype={'codigo_grupo': 'string'})  # Lee desempeño por grupos.
    brechas = pd.read_csv(RAIZ / 'reports/eda08_evaluacion/06_brechas_desempeno_ic95.csv')  # Lee brechas con incertidumbre.
    importancia = pd.read_csv(RAIZ / 'reports/eda07_modelado/08_importancia_permutacion_resumen.csv')  # Lee interpretación OOF.
    return datos, pares, asociaciones, wald, globales, intervalos, comparacion, calibracion, grupos, brechas, importancia  # Devuelve productos en memoria.

datos, pares, asociaciones, wald, modelos_globales, modelos_ic, comparacion_modelos, calibracion_modelos, modelos_grupos, brechas_modelos, importancia = cargar_datos()  # Carga todos los productos una vez.
diseno = preparar_diseno(pares)  # Prepara matrices de diseño reutilizables.

# BLOQUE 3: funciones visuales del tablero.
def formato_numero(valor, decimales=1):  # Formatea números en español.
    if pd.isna(valor):  # Detecta ausencia.
        return '—'  # Devuelve un guion largo.
    texto = f'{valor:,.{decimales}f}'  # Formatea con separadores estándar.
    return texto.replace(',', 'X').replace('.', ',').replace('X', '.')  # Intercambia separadores.

def tarjeta_indicador(nombre, resultado):  # Presenta una tasa y su incertidumbre.
    valor = f"{formato_numero(resultado['porcentaje'])}%"  # Formatea el punto.
    intervalo = f"IC 95 %: {formato_numero(resultado['ic95_inferior'])}–{formato_numero(resultado['ic95_superior'])}%"  # Formatea el intervalo.
    st.metric(nombre, valor)  # Dibuja la tarjeta sin flechas de variación temporal.
    clase = resultado['precision'].lower()  # Construye la clase CSS.
    st.markdown(f"<small>{intervalo}<br>n={resultado['n']:,} · {resultado['upm']:,} UPM · CV={formato_numero(resultado['cv_porcentaje'])}% · <span class='precision-{clase}'>{resultado['precision']}</span></small>", unsafe_allow_html=True)  # Añade intervalo, soporte y precisión.

def grafico_tasas(tabla, titulo):  # Dibuja tasas con intervalos asimétricos.
    figura = go.Figure()  # Crea una figura vacía.
    figura.add_trace(go.Bar(x=tabla['grupo'], y=tabla['porcentaje'], marker_color=CELESTE, error_y={'type': 'data', 'symmetric': False, 'array': tabla['ic95_superior'] - tabla['porcentaje'], 'arrayminus': tabla['porcentaje'] - tabla['ic95_inferior']}, hovertemplate='<b>%{x}</b><br>%{y:.1f}%<extra></extra>'))  # Añade barras e IC.
    figura.update_layout(title=titulo, yaxis_title='Porcentaje ponderado', xaxis_title='', yaxis_range=[0, 100], height=430, margin=dict(l=30, r=20, t=60, b=80), plot_bgcolor='white', paper_bgcolor='white')  # Ajusta el diseño.
    figura.update_xaxes(tickangle=-25, gridcolor='#E2E8F0')  # Mejora etiquetas.
    figura.update_yaxes(gridcolor='#E2E8F0', ticksuffix='%')  # Añade escala porcentual.
    return figura  # Devuelve el gráfico.

def tabla_tasas_por(datos_filtrados, variable, indicador):  # Estima categorías visibles.
    filas = []  # Reserva resultados.
    for grupo in sorted(datos_filtrados[variable].dropna().unique()):  # Recorre grupos observados.
        resultado = estimar_tasa(datos_filtrados.loc[datos_filtrados[variable].eq(grupo)], diseno, indicador)  # Estima la tasa.
        filas.append({'grupo': grupo, **{clave: valor for clave, valor in resultado.items() if clave != 'influencia_upm'}})  # Conserva resultados publicables.
    return pd.DataFrame(filas)  # Devuelve la tabla.

def estilo_figura(figura):  # Homogeneiza figuras Plotly.
    figura.update_layout(font={'family': 'Arial, sans-serif', 'color': '#263244'}, title_font={'size': 18, 'color': AZUL}, hoverlabel={'bgcolor': 'white'}, legend_title_text='')  # Aplica tipografía y color.
    return figura  # Devuelve la figura.

# BLOQUE 4: cabecera y filtros globales.
st.markdown(f"<div class='hero'><div class='eyebrow'>Observatorio científico · versión 1.0</div><h1>{CONFIG['titulo']}</h1><p>{CONFIG['subtitulo']}</p></div>", unsafe_allow_html=True)  # Presenta la portada.
st.sidebar.markdown('## Filtros del análisis')  # Titula la barra lateral.
st.sidebar.caption('Los filtros actualizan las secciones descriptivas e inferenciales.')  # Explica el alcance.
provincias_disponibles = sorted(datos['provincia'].dropna().unique())  # Enumera provincias.
sexos_disponibles = ['Hombre', 'Mujer']  # Ordena sexos.
areas_disponibles = ['Urbana', 'Rural']  # Ordena áreas.
niveles_disponibles = ['Superior no universitaria', 'Superior universitaria', 'Posgrado']  # Ordena educación.
meses_disponibles = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']  # Ordena meses.
todas_provincias = st.sidebar.checkbox('Todas las provincias', value=True)  # Evita mostrar 24 etiquetas por defecto.
provincias = provincias_disponibles if todas_provincias else st.sidebar.multiselect('Provincia', provincias_disponibles, default=['Pichincha'], help='Puede seleccionar una o varias provincias.')  # Crea filtro provincial cuando se necesita.
sexos = st.sidebar.multiselect('Sexo', sexos_disponibles, default=sexos_disponibles)  # Crea filtro de sexo.
areas = st.sidebar.multiselect('Área', areas_disponibles, default=areas_disponibles)  # Crea filtro de área.
niveles = st.sidebar.multiselect('Nivel educativo reportado', niveles_disponibles, default=niveles_disponibles)  # Crea filtro educativo.
edad_minima = int(datos['edad_limite_inferior'].min())  # Obtiene edad mínima.
edad_maxima = int(datos['edad_limite_inferior'].max())  # Obtiene edad máxima.
rango_edad = st.sidebar.slider('Edad', edad_minima, edad_maxima, (edad_minima, edad_maxima), help='El valor 98 representa 98 años o más.')  # Crea filtro de edad.
with st.sidebar.expander('Filtro temporal'):  # Agrupa el filtro menos frecuente.
    meses = st.multiselect('Mes', meses_disponibles, default=meses_disponibles)  # Crea filtro mensual.
if not all([provincias, sexos, areas, niveles, meses]):  # Detecta filtros vacíos.
    st.warning('Seleccione al menos una categoría en cada filtro para continuar.')  # Informa el problema.
    st.stop()  # Detiene la aplicación de forma segura.
filtrados = aplicar_filtros(datos, provincias, sexos, areas, niveles, rango_edad, meses)  # Aplica todos los filtros.
if len(filtrados) == 0:  # Detecta una intersección sin observaciones.
    st.warning('La combinación de filtros no contiene observaciones. Amplíe la selección para continuar.')  # Orienta al usuario.
    st.stop()  # Evita cálculos y gráficos vacíos.
st.sidebar.markdown('---')  # Separa metadatos.
st.sidebar.metric('Registros seleccionados', f'{len(filtrados):,}')  # Muestra tamaño actual.
st.sidebar.caption(CONFIG['universo'])  # Recuerda el universo.
st.sidebar.caption(CONFIG['privacidad'])  # Expone privacidad.

# BLOQUE 5: pestaña de panorama.
tab_panorama, tab_brechas, tab_ingresos, tab_asociaciones, tab_modelos, tab_metodo = st.tabs(['Panorama', 'Brechas', 'Ingresos', 'Asociaciones', 'Modelos', 'Metodología'])  # Crea la navegación principal.
with tab_panorama:  # Abre el panorama.
    st.subheader('Indicadores laborales ponderados')  # Titula indicadores.
    st.markdown("<div class='panel-note'>Las tres tasas usan el mismo denominador descriptivo dentro del universo seleccionado.</div>", unsafe_allow_html=True)  # Aclara el denominador.
    resultados_indicadores = {nombre: estimar_tasa(filtrados, diseno, columna) for nombre, columna in CONFIG['indicadores'].items()}  # Estima los tres indicadores.
    columnas_kpi = st.columns(3)  # Crea tres tarjetas.
    for contenedor, (nombre, resultado) in zip(columnas_kpi, resultados_indicadores.items()):  # Recorre indicadores.
        with contenedor:  # Activa la tarjeta.
            tarjeta_indicador(nombre, resultado)  # Presenta resultado.
    st.markdown('#### Empleo adecuado por provincia')  # Introduce comparación territorial.
    tabla_provincias = tabla_tasas_por(filtrados, 'provincia', 'adecuado_descriptivo')  # Estima provincias visibles.
    tabla_provincias = tabla_provincias.sort_values('porcentaje', ascending=False)  # Ordena tasas.
    st.plotly_chart(estilo_figura(grafico_tasas(tabla_provincias, 'Tasa ponderada e IC 95 %')), width='stretch', config={'displaylogo': False})  # Muestra el gráfico.
    with st.expander('Ver tabla y descargar'):  # Ofrece detalle editable.
        tabla_visible = tabla_provincias.drop(columns=['suma_pesos'], errors='ignore').copy()  # Simplifica la tabla.
        st.dataframe(tabla_visible, width='stretch', hide_index=True)  # Muestra datos.
        st.download_button('Descargar CSV', tabla_visible.to_csv(index=False).encode('utf-8-sig'), 'tasas_provincia_filtradas.csv', 'text/csv')  # Permite descarga.
    st.markdown('#### Evolución mensual del empleo adecuado')  # Introduce la serie mensual.
    tabla_meses = tabla_tasas_por(filtrados, 'nombre_mes', 'adecuado_descriptivo')  # Estima meses seleccionados.
    tabla_meses['orden'] = tabla_meses['grupo'].map({mes: indice for indice, mes in enumerate(meses_disponibles)})  # Recupera orden calendario.
    tabla_meses = tabla_meses.sort_values('orden')  # Ordena temporalmente.
    figura_mes = go.Figure(go.Scatter(x=tabla_meses['grupo'], y=tabla_meses['porcentaje'], mode='lines+markers', line={'color': AZUL, 'width': 3}, error_y={'type': 'data', 'symmetric': False, 'array': tabla_meses['ic95_superior'] - tabla_meses['porcentaje'], 'arrayminus': tabla_meses['porcentaje'] - tabla_meses['ic95_inferior']}, hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'))  # Dibuja tendencia e IC.
    figura_mes.update_layout(yaxis_title='Empleo adecuado ponderado', xaxis_title='', yaxis_range=[0, 100], height=390, plot_bgcolor='white')  # Ajusta la serie.
    figura_mes.update_yaxes(ticksuffix='%', gridcolor='#E2E8F0')  # Formatea eje.
    st.plotly_chart(estilo_figura(figura_mes), width='stretch', config={'displaylogo': False})  # Presenta la serie.

# BLOQUE 6: pestaña de brechas e incertidumbre.
with tab_brechas:  # Abre la sección de comparación.
    st.subheader('Comparación de dos grupos')  # Titula la herramienta.
    st.caption('La diferencia se calcula como grupo A menos grupo B y conserva la covarianza del diseño.')  # Explica el signo.
    col_control_1, col_control_2 = st.columns(2)  # Organiza controles.
    with col_control_1:  # Activa primer control.
        indicador_nombre = st.selectbox('Indicador', list(CONFIG['indicadores']))  # Elige el resultado.
        dimension_nombre = st.selectbox('Dimensión', ['Sexo', 'Área', 'Nivel educativo', 'Provincia'])  # Elige la dimensión.
    mapa_dimension = {'Sexo': 'sexo', 'Área': 'area_residencia', 'Nivel educativo': 'nivel_educativo', 'Provincia': 'provincia'}  # Traduce dimensiones.
    variable_dimension = mapa_dimension[dimension_nombre]  # Recupera variable.
    opciones_grupo = sorted(filtrados[variable_dimension].dropna().unique())  # Enumera grupos visibles.
    if len(opciones_grupo) < 2:  # Detecta falta de comparación.
        st.info('La selección actual contiene menos de dos grupos en esta dimensión. Amplíe los filtros laterales.')  # Orienta al usuario.
    else:  # Continúa con grupos suficientes.
        with col_control_2:  # Activa segundo control.
            grupo_a = st.selectbox('Grupo A', opciones_grupo, index=1 if len(opciones_grupo) > 1 else 0)  # Elige primer grupo.
            opciones_b = [opcion for opcion in opciones_grupo if opcion != grupo_a]  # Excluye duplicidad.
            grupo_b = st.selectbox('Grupo B', opciones_b, index=0)  # Elige referencia.
        contraste = contrastar_grupos(filtrados, diseno, CONFIG['indicadores'][indicador_nombre], variable_dimension, grupo_a, grupo_b)  # Estima la diferencia.
        k1, k2, k3 = st.columns(3)  # Crea tarjetas comparativas.
        k1.metric(str(grupo_a), f"{formato_numero(contraste['tasa_a'])}%")  # Muestra tasa A.
        k1.caption(f"n={contraste['n_a']:,}")  # Añade soporte del grupo A.
        k2.metric(str(grupo_b), f"{formato_numero(contraste['tasa_b'])}%")  # Muestra tasa B.
        k2.caption(f"n={contraste['n_b']:,}")  # Añade soporte del grupo B.
        k3.metric('Diferencia A − B', f"{formato_numero(contraste['diferencia_pp'])} pp")  # Muestra brecha.
        k3.caption(f"IC 95 %: {formato_numero(contraste['ic95_inferior'])} a {formato_numero(contraste['ic95_superior'])}")  # Añade el intervalo sin flecha.
        figura_contraste = go.Figure(go.Scatter(x=[contraste['diferencia_pp']], y=[f'{grupo_a} − {grupo_b}'], mode='markers', marker={'size': 12, 'color': NARANJA}, error_x={'type': 'data', 'symmetric': False, 'array': [contraste['ic95_superior'] - contraste['diferencia_pp']], 'arrayminus': [contraste['diferencia_pp'] - contraste['ic95_inferior']]}, hovertemplate='%{x:.2f} pp<extra></extra>'))  # Dibuja diferencia e IC.
        figura_contraste.add_vline(x=0, line_color='#1E293B', line_width=1)  # Marca igualdad.
        figura_contraste.update_layout(title='Diferencia ponderada con IC 95 %', xaxis_title='Puntos porcentuales', yaxis_title='', height=300, plot_bgcolor='white')  # Ajusta la figura.
        figura_contraste.update_xaxes(gridcolor='#E2E8F0')  # Añade guías.
        st.plotly_chart(estilo_figura(figura_contraste), width='stretch', config={'displaylogo': False})  # Muestra el contraste.
        st.caption(f"Valor p bilateral: {contraste['valor_p']:.4f}. Precisión: {grupo_a}={contraste['precision_a']}; {grupo_b}={contraste['precision_b']}.")  # Expone evidencia.
    st.markdown('#### Todas las categorías de la dimensión')  # Introduce panorama de grupos.
    tabla_dimension = tabla_tasas_por(filtrados, variable_dimension, CONFIG['indicadores'][indicador_nombre])  # Estima categorías.
    st.plotly_chart(estilo_figura(grafico_tasas(tabla_dimension, indicador_nombre)), width='stretch', config={'displaylogo': False})  # Presenta categorías.

# BLOQUE 7: pestaña de ingresos laborales.
with tab_ingresos:  # Abre análisis de ingresos.
    st.subheader('Distribución de ingresos laborales observados')  # Titula la sección.
    ingresos = filtrados.loc[filtrados['ingreso_monto_observado'].fillna(False).astype(bool) & filtrados['ingreso_laboral_monto'].notna() & filtrados['ingreso_laboral_monto'].ge(0)].copy()  # Selecciona montos utilizables.
    st.caption('Ocupados con monto numérico no negativo; no se imputan faltantes ni códigos especiales. El recorte visual no altera los cuantiles.')  # Explica la política.
    if len(ingresos) == 0:  # Detecta ausencia de montos.
        st.info('No hay ingresos observados con los filtros actuales.')  # Informa al usuario.
    else:  # Continúa con ingresos disponibles.
        cuantiles = cuantil_ponderado(ingresos['ingreso_laboral_monto'], ingresos['fexp'], [0.25, 0.5, 0.75, 0.9, 0.99])  # Calcula resumen ponderado.
        tarjetas_ingreso = st.columns(4)  # Crea tarjetas.
        tarjetas_ingreso[0].metric('Ingresos observados', f'{len(ingresos):,}')  # Muestra n.
        tarjetas_ingreso[1].metric('Mediana ponderada', f"USD {formato_numero(cuantiles[1], 0)}")  # Muestra mediana.
        tarjetas_ingreso[2].metric('P25–P75', f"USD {formato_numero(cuantiles[0], 0)}–{formato_numero(cuantiles[2], 0)}")  # Muestra rango intercuartílico.
        tarjetas_ingreso[3].metric('P90', f"USD {formato_numero(cuantiles[3], 0)}")  # Muestra percentil alto.
        maximo_visual = st.slider('Límite superior del gráfico (USD)', 500, max(500, int(np.ceil(cuantiles[4] / 100) * 100)), min(3000, max(500, int(np.ceil(cuantiles[4] / 100) * 100))), step=100)  # Permite explorar la cola.
        visibles = ingresos.loc[ingresos['ingreso_laboral_monto'].le(maximo_visual)]  # Aplica recorte solo visual.
        histograma = histograma_ponderado(visibles['ingreso_laboral_monto'], visibles['fexp'], maximo_visual)  # Agrega el histograma.
        figura_ingreso = px.bar(histograma, x='ingreso', y='porcentaje_ponderado', labels={'ingreso': 'Ingreso laboral mensual (USD)', 'porcentaje_ponderado': 'Distribución ponderada (%)'}, color_discrete_sequence=[CELESTE])  # Construye el histograma.
        figura_ingreso.update_layout(title=f'Distribución hasta USD {maximo_visual:,}', height=430, plot_bgcolor='white', bargap=0.04)  # Ajusta diseño.
        figura_ingreso.update_yaxes(gridcolor='#E2E8F0', ticksuffix='%')  # Formatea porcentaje.
        st.plotly_chart(estilo_figura(figura_ingreso), width='stretch', config={'displaylogo': False})  # Muestra ingresos.
        st.caption(f"El {100 * (1 - visibles['fexp'].sum() / ingresos['fexp'].sum()):.1f}% del peso con ingreso observado queda fuera del límite visual seleccionado.")  # Cuantifica el recorte.

# BLOQUE 8: pestaña de asociaciones ajustadas.
with tab_asociaciones:  # Abre asociaciones.
    st.subheader('Asociaciones ajustadas con empleo adecuado')  # Titula la sección.
    st.markdown("<div class='panel-note'>Razones de momios condicionales de la regresión ponderada. Son asociaciones contemporáneas, no efectos causales.</div>", unsafe_allow_html=True)  # Advierte interpretación.
    familias = {'Sexo': 'p02[', 'Área': 'area[', 'Educación': 'p10a[', 'Estado civil': 'p06[', 'Asistencia educativa': 'p07[', 'Etnia': 'p15[', 'Provincia': 'prov[', 'Mes': 'mes[', 'Edad': 'edad_'}  # Define familias de términos.
    familia = st.selectbox('Familia de variables', list(familias), index=2)  # Elige una familia.
    datos_or = asociaciones.loc[asociaciones['termino'].str.startswith(familias[familia])].copy()  # Selecciona términos.
    etiquetas_or = {'p02[2]': 'Mujer vs. hombre', 'area[2]': 'Rural vs. urbana', 'p10a[8]': 'Superior no universitaria vs. universitaria', 'p10a[10]': 'Posgrado vs. universitaria', 'edad_decadas_c40': 'Edad: término lineal por década', 'edad_decadas_c40_cuadrado': 'Edad: término cuadrático'}  # Traduce términos principales.
    datos_or['etiqueta'] = datos_or['termino'].map(etiquetas_or).fillna(datos_or['termino'])  # Aplica etiquetas disponibles.
    datos_or = datos_or.sort_values('razon_momios')  # Ordena razones.
    figura_or = go.Figure(go.Scatter(x=datos_or['razon_momios'], y=datos_or['etiqueta'], mode='markers', marker={'size': 9, 'color': AZUL}, error_x={'type': 'data', 'symmetric': False, 'array': datos_or['ic95_superior'] - datos_or['razon_momios'], 'arrayminus': datos_or['razon_momios'] - datos_or['ic95_inferior']}, customdata=np.column_stack([datos_or['valor_p']]), hovertemplate='OR=%{x:.2f}<br>p=%{customdata[0]:.4f}<extra></extra>'))  # Dibuja OR e IC.
    figura_or.add_vline(x=1, line_color='#1E293B', line_width=1)  # Marca ausencia de asociación.
    figura_or.update_xaxes(type='log', title='Razón de momios ajustada (escala log)', gridcolor='#E2E8F0')  # Configura escala.
    figura_or.update_layout(title=f'Asociaciones: {familia}', yaxis_title='', height=max(340, 36 * len(datos_or) + 150), plot_bgcolor='white')  # Ajusta altura.
    st.plotly_chart(estilo_figura(figura_or), width='stretch', config={'displaylogo': False})  # Muestra bosque.
    prueba_global = wald.loc[wald['variable'].eq({'Sexo': 'p02', 'Área': 'area', 'Educación': 'p10a', 'Estado civil': 'p06', 'Asistencia educativa': 'p07', 'Etnia': 'p15', 'Provincia': 'prov', 'Mes': 'mes', 'Edad': 'edad'}[familia])]  # Recupera Wald global.
    if len(prueba_global):  # Comprueba disponibilidad.
        st.caption(f"Prueba global de Wald: χ²={prueba_global['estadistico_wald'].iloc[0]:.2f}; gl={int(prueba_global['grados_libertad_prueba'].iloc[0])}; p={prueba_global['valor_p'].iloc[0]:.4g}.")  # Presenta prueba.
    st.dataframe(datos_or[['etiqueta', 'razon_momios', 'ic95_inferior', 'ic95_superior', 'valor_p']], width='stretch', hide_index=True)  # Presenta tabla.

# BLOQUE 9: pestaña de modelos y errores entre grupos.
with tab_modelos:  # Abre evaluación predictiva.
    st.subheader('Comparación final de modelos')  # Titula la sección.
    st.markdown(f"<div class='panel-note'>{CONFIG['nota_modelos']}</div>", unsafe_allow_html=True)  # Presenta la conclusión congelada.
    metricas_modelo = ['roc_auc', 'pr_auc', 'brier', 'exactitud_balanceada']  # Selecciona métricas principales.
    datos_modelo = modelos_ic.loc[modelos_ic['modelo'].isin(['logistica', 'boosting']) & modelos_ic['metrica'].isin(metricas_modelo)].copy()  # Selecciona resultados.
    etiquetas_metricas = {'roc_auc': 'ROC-AUC', 'pr_auc': 'PR-AUC', 'brier': 'Brier', 'exactitud_balanceada': 'Exactitud balanceada'}  # Define etiquetas.
    metrica_modelo = st.selectbox('Métrica para comparar', metricas_modelo, format_func=lambda valor: etiquetas_metricas[valor])  # Elige métrica.
    vista_modelo = datos_modelo.loc[datos_modelo['metrica'].eq(metrica_modelo)]  # Filtra la métrica.
    figura_modelo = go.Figure(go.Scatter(x=vista_modelo['estimacion'], y=vista_modelo['modelo'].str.capitalize(), mode='markers', marker={'size': 12, 'color': [AZUL, NARANJA]}, error_x={'type': 'data', 'symmetric': False, 'array': vista_modelo['ic95_superior'] - vista_modelo['estimacion'], 'arrayminus': vista_modelo['estimacion'] - vista_modelo['ic95_inferior']}, hovertemplate='%{x:.3f}<extra></extra>'))  # Dibuja métricas e IC.
    figura_modelo.update_layout(title=f"{etiquetas_metricas[metrica_modelo]} en prueba reservada", xaxis_title=etiquetas_metricas[metrica_modelo], yaxis_title='', height=320, plot_bgcolor='white')  # Ajusta figura.
    figura_modelo.update_xaxes(gridcolor='#E2E8F0')  # Añade guías.
    st.plotly_chart(estilo_figura(figura_modelo), width='stretch', config={'displaylogo': False})  # Muestra comparación.
    st.markdown('#### Diferencia pareada: boosting menos logística')  # Introduce comparación directa.
    comparacion_visible = comparacion_modelos.copy()  # Copia resultados.
    comparacion_visible['incluye_cero'] = (comparacion_visible['ic95_inferior'] <= 0) & (comparacion_visible['ic95_superior'] >= 0)  # Marca incertidumbre.
    st.dataframe(comparacion_visible, width='stretch', hide_index=True)  # Presenta diferencias.
    st.markdown('#### Calibración en prueba')  # Introduce calibración.
    figura_cal = px.line(calibracion_modelos, x='prediccion_media', y='proporcion_observada', color='modelo', markers=True, color_discrete_map={'base': GRIS, 'logistica': AZUL, 'boosting': NARANJA}, labels={'prediccion_media': 'Probabilidad predicha', 'proporcion_observada': 'Proporción observada', 'modelo': 'Modelo'})  # Construye curvas.
    figura_cal.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line={'dash': 'dash', 'color': '#1E293B'}, name='Ideal'))  # Añade diagonal.
    figura_cal.update_layout(height=430, plot_bgcolor='white', xaxis_range=[0, 1], yaxis_range=[0, 1])  # Ajusta escala.
    figura_cal.update_xaxes(gridcolor='#E2E8F0', tickformat='.0%')  # Formatea eje x.
    figura_cal.update_yaxes(gridcolor='#E2E8F0', tickformat='.0%')  # Formatea eje y.
    st.plotly_chart(estilo_figura(figura_cal), width='stretch', config={'displaylogo': False})  # Muestra calibración.
    st.markdown('#### Desempeño por sexo y área')  # Introduce auditoría.
    modelo_auditoria = st.radio('Modelo', ['logistica', 'boosting'], horizontal=True, format_func=lambda valor: valor.capitalize())  # Elige modelo.
    metrica_auditoria = st.selectbox('Métrica por grupo', ['roc_auc', 'brier', 'sensibilidad', 'especificidad'])  # Elige métrica.
    vista_grupos = modelos_grupos.loc[modelos_grupos['modelo'].eq(modelo_auditoria)].copy()  # Filtra modelo.
    etiquetas_grupo = {('p02', '1'): 'Hombre', ('p02', '2'): 'Mujer', ('area', '1'): 'Urbana', ('area', '2'): 'Rural'}  # Traduce grupos.
    vista_grupos['grupo'] = [etiquetas_grupo.get((fila.variable_grupo, str(fila.codigo_grupo)), str(fila.codigo_grupo)) for fila in vista_grupos.itertuples()]  # Aplica etiquetas.
    figura_grupos = px.bar(vista_grupos, x='grupo', y=metrica_auditoria, color='variable_grupo', barmode='group', color_discrete_map={'p02': AZUL, 'area': CELESTE}, labels={'grupo': '', metrica_auditoria: metrica_auditoria.replace('_', ' ').title(), 'variable_grupo': 'Dimensión'})  # Dibuja grupos.
    figura_grupos.update_layout(height=390, plot_bgcolor='white')  # Ajusta figura.
    figura_grupos.update_yaxes(gridcolor='#E2E8F0')  # Añade guías.
    st.plotly_chart(estilo_figura(figura_grupos), width='stretch', config={'displaylogo': False})  # Muestra auditoría.
    brechas_visibles = brechas_modelos.loc[(brechas_modelos['modelo'].eq(modelo_auditoria)) & (brechas_modelos['metrica'].eq(metrica_auditoria))]  # Recupera IC de brechas.
    st.dataframe(brechas_visibles, width='stretch', hide_index=True)  # Presenta diferencias e IC.
    st.markdown('#### Importancia predictiva fuera de pliegue')  # Introduce interpretación.
    importancia_visible = importancia.loc[importancia['modelo'].eq(modelo_auditoria)].sort_values('caida_auc_media')  # Ordena importancia.
    figura_importancia = px.bar(importancia_visible, x='caida_auc_media', y='variable', orientation='h', error_x='caida_auc_de', color_discrete_sequence=[NARANJA if modelo_auditoria == 'boosting' else AZUL], labels={'caida_auc_media': 'Caída media de ROC-AUC al permutar', 'variable': ''})  # Dibuja importancia.
    figura_importancia.update_layout(height=430, plot_bgcolor='white')  # Ajusta figura.
    figura_importancia.update_xaxes(gridcolor='#E2E8F0')  # Añade guías.
    st.plotly_chart(estilo_figura(figura_importancia), width='stretch', config={'displaylogo': False})  # Muestra importancia.
    st.caption('La importancia por permutación describe dependencia predictiva, no causalidad ni relevancia social.')  # Limita interpretación.

# BLOQUE 10: pestaña metodológica y pie.
with tab_metodo:  # Abre documentación.
    st.subheader('Metodología y lectura responsable')  # Titula la sección.
    st.markdown(f"**Universo:** {CONFIG['universo']}.")  # Describe población.
    st.markdown('**Diseño:** ponderación anual `fexp`, 150 estratos y 7.780 UPM; 7.630 grados de libertad.')  # Describe diseño.
    st.markdown(f"**Incertidumbre dinámica:** {CONFIG['nota_inferencia']}")  # Describe intervalos.
    st.markdown('**Evaluación predictiva:** una sola aplicación a 7.791 personas de 1.269 UPM reservadas; IC mediante 1.000 réplicas bootstrap de UPM dentro de estrato.')  # Describe prueba.
    st.markdown('**Separación analítica:** las tasas descriptivas, las asociaciones ajustadas y la evaluación predictiva responden preguntas diferentes y se presentan en secciones distintas.')  # Explica separación.
    st.markdown('**Limitaciones:** estudio transversal; no demuestra causalidad ni pronostica automáticamente el empleo futuro. El nivel educativo reportado no identifica necesariamente el título más alto obtenido.')  # Expone límites.
    st.markdown('**Precisión:** “Alta” requiere n≥200 y CV≤10 %; “Moderada”, n≥100 y CV≤20 %; las demás selecciones se marcan “Precaución”.')  # Explica semáforo.
    st.info('Los resultados filtrados son exploratorios. Para citar cifras principales utilice las tablas científicas congeladas del proyecto.')  # Orienta uso académico.
    st.markdown('#### Archivos científicos utilizados')  # Introduce fuentes internas.
    st.code('data/dashboard/observatorio_enemdu_2025.parquet\nreports/eda06_inferencia/\nreports/eda07_modelado/\nreports/eda08_evaluacion/', language=None)  # Enumera fuentes reproducibles.

st.markdown("<div class='footer'>ENEMDU anual 2025 · Proyecto académico de Python para Ciencia de Datos e IA · Resultados agregados y reproducibles.</div>", unsafe_allow_html=True)  # Cierra la aplicación.
