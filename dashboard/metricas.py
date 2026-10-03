# ETAPA 9: motor estadístico reutilizable del dashboard.
# ARCHIVO: metricas.py; calcula estimaciones ponderadas, intervalos y contrastes de diseño.
# BLOQUE 1: dependencias.
import numpy as np  # Ejecuta álgebra y agregación.
import pandas as pd  # Maneja filtros y tablas.
from scipy import stats  # Obtiene cuantiles t y valores p.

# BLOQUE 2: estructura del diseño.
def preparar_diseno(pares):  # Prepara índices que se reutilizan en cada filtro.
    pares = pares[['estrato', 'upm']].drop_duplicates().sort_values(['estrato', 'upm']).reset_index(drop=True)  # Ordena UPM completas.
    mapa = pd.Series(np.arange(len(pares)), index=pd.MultiIndex.from_frame(pares))  # Asigna un código entero.
    estratos = pares['estrato'].to_numpy()  # Conserva el estrato de cada UPM.
    grados_libertad = len(pares) - pares['estrato'].nunique()  # Calcula UPM menos estratos.
    return {'pares': pares, 'mapa': mapa, 'estratos': estratos, 'gl': grados_libertad, 't95': stats.t.ppf(0.975, df=grados_libertad)}  # Devuelve el diseño preparado.

def _varianza_upm(totales, estratos):  # Estima covarianza de Taylor desde totales de UPM.
    matriz = np.asarray(totales, dtype=float)  # Convierte a matriz.
    matriz = matriz[:, None] if matriz.ndim == 1 else matriz  # Admite una o varias columnas.
    covarianza = np.zeros((matriz.shape[1], matriz.shape[1]))  # Inicializa la covarianza.
    for estrato in np.unique(estratos):  # Recorre estratos completos.
        bloque = matriz[estratos == estrato]  # Selecciona sus UPM.
        if len(bloque) > 1:  # Protege estratos con al menos dos UPM.
            centrado = bloque - bloque.mean(axis=0, keepdims=True)  # Centra dentro del estrato.
            covarianza += len(bloque) / (len(bloque) - 1) * centrado.T @ centrado  # Acumula la aproximación con reemplazo.
    return covarianza  # Devuelve la matriz.

# BLOQUE 3: estimación de una proporción filtrada.
def estimar_tasa(datos, diseno, indicador):  # Estima una razón de totales y su IC.
    if len(datos) == 0:  # Detecta una selección vacía.
        return {'n': 0, 'upm': 0, 'suma_pesos': 0.0, 'porcentaje': np.nan, 'error_estandar_pp': np.nan, 'ic95_inferior': np.nan, 'ic95_superior': np.nan, 'cv_porcentaje': np.nan, 'precision': 'Sin datos', 'influencia_upm': np.zeros(len(diseno['pares']))}  # Devuelve estructura vacía.
    y = pd.to_numeric(datos[indicador], errors='coerce').to_numpy(dtype=float)  # Recupera el indicador binario.
    w = datos['fexp'].to_numpy(dtype=float)  # Recupera pesos.
    validos = np.isfinite(y) & np.isfinite(w) & (w > 0)  # Identifica observaciones válidas.
    datos_validos = datos.loc[validos]  # Conserva claves válidas.
    y = y[validos]  # Conserva resultados válidos.
    w = w[validos]  # Conserva pesos válidos.
    if len(y) == 0 or w.sum() == 0:  # Detecta denominador nulo.
        return estimar_tasa(datos.iloc[0:0], diseno, indicador)  # Reutiliza la salida vacía.
    proporcion = float(np.sum(w * y) / np.sum(w))  # Calcula la razón ponderada.
    linealizada = w * (y - proporcion) / np.sum(w)  # Calcula influencia individual.
    claves = pd.MultiIndex.from_frame(datos_validos[['estrato', 'upm']])  # Construye claves UPM.
    codigos = diseno['mapa'].loc[claves].to_numpy(dtype=int)  # Recupera códigos de UPM.
    influencia = np.bincount(codigos, weights=linealizada, minlength=len(diseno['pares']))  # Agrega contribuciones por UPM.
    varianza = float(_varianza_upm(influencia, diseno['estratos'])[0, 0])  # Calcula varianza de diseño.
    error = np.sqrt(max(varianza, 0))  # Calcula error estándar.
    if 0 < proporcion < 1 and error > 0:  # Comprueba que puede usar logit.
        centro = np.log(proporcion / (1 - proporcion))  # Transforma el punto.
        error_logit = error / (proporcion * (1 - proporcion))  # Aplica método delta.
        inferior = expit_local(centro - diseno['t95'] * error_logit)  # Calcula límite inferior.
        superior = expit_local(centro + diseno['t95'] * error_logit)  # Calcula límite superior.
    else:  # Usa intervalo lineal en los límites.
        inferior = max(0.0, proporcion - diseno['t95'] * error)  # Trunca el límite inferior.
        superior = min(1.0, proporcion + diseno['t95'] * error)  # Trunca el límite superior.
    cv = 100 * error / proporcion if proporcion > 0 else np.nan  # Calcula coeficiente de variación.
    precision = clasificar_precision(len(y), cv)  # Clasifica la estabilidad.
    return {'n': int(len(y)), 'upm': int(datos_validos['upm'].nunique()), 'suma_pesos': float(w.sum()), 'porcentaje': 100 * proporcion, 'error_estandar_pp': 100 * error, 'ic95_inferior': 100 * inferior, 'ic95_superior': 100 * superior, 'cv_porcentaje': cv, 'precision': precision, 'influencia_upm': influencia}  # Devuelve resultados completos.

def expit_local(valor):  # Evalúa la inversa del logit sin otra dependencia.
    return float(1 / (1 + np.exp(-valor)))  # Devuelve una probabilidad.

def clasificar_precision(n, cv):  # Resume calidad de una estimación para la interfaz.
    if n >= 200 and np.isfinite(cv) and cv <= 10:  # Evalúa el nivel más estable.
        return 'Alta'  # Devuelve nivel alto.
    if n >= 100 and np.isfinite(cv) and cv <= 20:  # Evalúa el nivel intermedio.
        return 'Moderada'  # Devuelve nivel moderado.
    return 'Precaución'  # Advierte tamaños o CV limitados.

# BLOQUE 4: contraste entre dos grupos con covarianza compartida.
def contrastar_grupos(datos, diseno, indicador, variable, grupo_a, grupo_b):  # Compara A menos B.
    resultado_a = estimar_tasa(datos.loc[datos[variable].eq(grupo_a)], diseno, indicador)  # Estima el primer grupo.
    resultado_b = estimar_tasa(datos.loc[datos[variable].eq(grupo_b)], diseno, indicador)  # Estima la referencia.
    diferencia = resultado_a['porcentaje'] - resultado_b['porcentaje']  # Calcula diferencia en puntos.
    influencia = resultado_a['influencia_upm'] - resultado_b['influencia_upm']  # Conserva covarianza.
    varianza = float(_varianza_upm(influencia, diseno['estratos'])[0, 0])  # Calcula varianza conjunta.
    error_pp = 100 * np.sqrt(max(varianza, 0))  # Convierte error a puntos porcentuales.
    inferior = diferencia - diseno['t95'] * error_pp  # Calcula límite inferior.
    superior = diferencia + diseno['t95'] * error_pp  # Calcula límite superior.
    estadistico = diferencia / error_pp if error_pp > 0 else np.nan  # Calcula estadístico t.
    valor_p = 2 * stats.t.sf(abs(estadistico), df=diseno['gl']) if np.isfinite(estadistico) else np.nan  # Calcula valor p bilateral.
    return {'grupo_a': grupo_a, 'grupo_b': grupo_b, 'tasa_a': resultado_a['porcentaje'], 'tasa_b': resultado_b['porcentaje'], 'diferencia_pp': diferencia, 'error_estandar_pp': error_pp, 'ic95_inferior': inferior, 'ic95_superior': superior, 'valor_p': valor_p, 'n_a': resultado_a['n'], 'n_b': resultado_b['n'], 'precision_a': resultado_a['precision'], 'precision_b': resultado_b['precision']}  # Devuelve el contraste.

# BLOQUE 5: utilidades de filtros e ingresos.
def aplicar_filtros(datos, provincias, sexos, areas, niveles, rango_edad, meses):  # Aplica filtros simultáneos.
    mascara = datos['provincia'].isin(provincias) & datos['sexo'].isin(sexos) & datos['area_residencia'].isin(areas) & datos['nivel_educativo'].isin(niveles) & datos['nombre_mes'].isin(meses)  # Combina categorías.
    mascara &= datos['edad_limite_inferior'].between(rango_edad[0], rango_edad[1], inclusive='both')  # Aplica edad.
    return datos.loc[mascara].copy()  # Devuelve la selección.

def cuantil_ponderado(valores, pesos, cuantiles):  # Calcula cuantiles con pesos.
    valores = np.asarray(valores, dtype=float)  # Convierte valores.
    pesos = np.asarray(pesos, dtype=float)  # Convierte pesos.
    orden = np.argsort(valores)  # Ordena montos.
    valores = valores[orden]  # Reordena montos.
    pesos = pesos[orden]  # Reordena pesos.
    acumulado = (np.cumsum(pesos) - 0.5 * pesos) / pesos.sum()  # Calcula posiciones ponderadas.
    return np.interp(np.atleast_1d(cuantiles), acumulado, valores)  # Interpola cuantiles.

def histograma_ponderado(valores, pesos, maximo, bins=30):  # Resume ingresos sin dibujar cada registro.
    bordes = np.linspace(0, maximo, bins + 1)  # Define intervalos comunes.
    frecuencias, _ = np.histogram(valores, bins=bordes, weights=pesos)  # Suma población ponderada.
    centros = (bordes[:-1] + bordes[1:]) / 2  # Calcula centros.
    porcentaje = 100 * frecuencias / frecuencias.sum() if frecuencias.sum() > 0 else frecuencias  # Convierte a porcentaje visible.
    return pd.DataFrame({'ingreso': centros, 'porcentaje_ponderado': porcentaje})  # Devuelve datos graficables.
