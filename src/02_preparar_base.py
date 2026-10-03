# ETAPA 3 DEL EDA: crear bases tratadas y reservar grupos para evaluación predictiva.
# ARCHIVO: 02_preparar_base.py. Las reglas están predefinidas en config/preparacion_v1.json.
# BLOQUE 1: herramientas y rutas independientes del equipo.
import hashlib  # Calcula huellas y órdenes reproducibles de grupos.
import json  # Lee decisiones y guarda metadatos.
import math  # Redondea la cantidad de UPM de prueba sin depender del resultado laboral.
from datetime import datetime, timezone  # Registra el momento real de ejecución.
from pathlib import Path  # Maneja rutas de forma portable.
from zipfile import ZipFile  # Lee el original comprimido sin modificarlo.
import numpy as np  # Comprueba números finitos.
import pandas as pd  # Transforma tablas mediante reglas explícitas.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto desde este programa.
CONFIG = RAIZ / 'config/preparacion_v1.json'  # Localiza las decisiones metodológicas congeladas.
DATOS = RAIZ / 'data/processed'  # Define dónde guardar las bases tratadas.
REPORTES = RAIZ / 'reports/preparacion'  # Define dónde guardar los reportes de transformación.

def huella(ruta):  # Calcula SHA-256 de un archivo sin cargarlo completo en memoria.
    calculo = hashlib.sha256()  # Inicializa el cálculo.
    with ruta.open('rb') as archivo:  # Abre el archivo como bytes de solo lectura.
        for bloque in iter(lambda: archivo.read(1024 * 1024), b''):  # Recorre bloques de un megabyte.
            calculo.update(bloque)  # Incorpora cada bloque a la huella.
    return calculo.hexdigest()  # Devuelve la identidad del archivo.

def numerica(serie):  # Interpreta una copia numérica de una columna original.
    return pd.to_numeric(serie.str.replace(',', '.', regex=False), errors='coerce')  # Convierte coma decimal sin asignar cero a vacíos.

def guardar_csv(tabla, ruta):  # Guarda texto con formato explícito y compresión reproducible cuando corresponde.
    compresion = {'method': 'gzip', 'mtime': 0} if ruta.suffix == '.gz' else None  # Evita que la hora cambie la huella del gzip.
    tabla.to_csv(ruta, index=False, encoding='utf-8-sig', decimal='.', na_rep='', compression=compresion)  # Conserva vacíos como vacíos y usa decimal estándar para Python.

def preparar():  # Encapsula toda la preparación para ejecutarla también desde el cuaderno.
    reglas = json.loads(CONFIG.read_text(encoding='utf-8'))  # Lee las reglas antes de observar cualquier resultado de prueba.
    origen = RAIZ / 'data/raw/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip'  # Señala el original auditado.
    if huella(origen) != reglas['sha256_fuente_csv']:  # No mezcla silenciosamente una versión nueva de datos.
        raise ValueError('La fuente cambió; revisar la auditoría antes de preparar otra versión.')  # Explica por qué se detiene.
    for carpeta in [DATOS, DATOS / 'modelado', REPORTES]:  # Prepara destinos de esta etapa.
        carpeta.mkdir(parents=True, exist_ok=True)  # Crea carpetas sin borrar archivos anteriores.
    catalogo = json.loads((RAIZ / 'reports/calidad/14_catalogo_spss_oficial.json').read_text(encoding='utf-8'))  # Carga etiquetas oficiales verificadas.
    with ZipFile(origen) as archivo:  # Abre la fuente sin extraer ni modificar sus tablas.
        base = pd.read_csv(archivo.open('BDDenemdu_personas_2025_anual.csv'), sep=';', encoding='utf-8-sig', dtype=str, keep_default_na=False, on_bad_lines='error')  # Conserva todos los campos y ceros de códigos.
    originales = list(base.columns)  # Guarda el inventario de las 139 columnas originales.
    transformaciones = []  # Acumula una bitácora cuantificada de cada transformación.

    # BLOQUE 2: normalizar únicamente espacios, ausencias y el tipo de los pesos.
    for campo in originales:  # Trata cada columna manteniendo su nombre original.
        antes = base[campo]  # Conserva el texto para contar cambios.
        despues = antes.str.strip().astype('string')  # Retira espacios exteriores sin recodificar categorías.
        transformaciones.append({'variable': campo, 'operacion': 'espacios_exteriores_y_vacio_a_ausente', 'celdas_con_espacios_retirados': int(antes.ne(despues).sum()), 'celdas_ausentes': int(despues.eq('').sum()), 'filas_eliminadas': 0})  # Registra magnitud y ausencia de eliminación.
        base[campo] = despues.mask(despues.eq(''), pd.NA)  # Representa vacíos como ausentes, no como ceros.
    base['fexp'] = numerica(base['fexp']).astype('float64')  # Convierte el peso anual a número, conservando su escala.
    assert base['fexp'].notna().all() and np.isfinite(base['fexp']).all() and base['fexp'].gt(0).all()  # Exige pesos válidos antes de exportar.
    guardar_csv(pd.DataFrame(transformaciones), REPORTES / '01_bitacora_transformaciones.csv')  # Guarda la trazabilidad de la normalización.
    print('Original normalizado en memoria; creando indicadores y dominios.', flush=True)  # Informa el avance.
    diccionario = []  # Acumula definiciones de todas las columnas entregadas.
    for campo in originales:  # Describe también los campos que no usarán los modelos.
        diccionario.append({'variable': campo, 'origen': campo, 'descripcion': catalogo['etiquetas_variables'].get(campo, campo), 'tipo': str(base[campo].dtype), 'rol': 'original_normalizado', 'regla': 'fexp: coma decimal a float64, sin reponderar' if campo=='fexp' else 'texto original sin espacios exteriores; vacío a ausente; códigos y ceros conservados', 'ausente_significa': 'Consultar flujo del cuestionario; no convertir automáticamente en cero'})  # Diferencia esquema técnico de significado.

    def agregar(nombre, valores, origenes, descripcion, rol, regla, ausente='No aplicable o desconocido según dominio'):  # Crea una columna y documenta su regla en el mismo lugar.
        if nombre in base.columns:  # Impide sobrescribir una variable original inadvertidamente.
            raise ValueError(f'Columna ya existente: {nombre}')  # Identifica el conflicto.
        base[nombre] = valores  # Añade la variable derivada.
        diccionario.append({'variable': nombre, 'origen': origenes, 'descripcion': descripcion, 'tipo': str(base[nombre].dtype), 'rol': rol, 'regla': regla, 'ausente_significa': ausente})  # Documenta su construcción y uso.

    # BLOQUE 3: definir edad, elegibilidad y resultados con denominadores explícitos.
    edad_codigo = numerica(base['p03'])  # Conserva el código original y crea una copia numérica.
    edad_conocida = edad_codigo.between(0, reglas['edad_categoria_abierta']).fillna(False)  # Reconoce 98 como límite inferior válido y 99 como desconocido.
    agregar('edad_limite_inferior', edad_codigo.where(edad_conocida).astype('Int16'), 'p03', 'Edad en años; 98 es límite inferior de 98 y más', 'predictor_numerico', '0..97 edad exacta; 98 límite inferior; 99 o vacío ausente')  # Evita presentar 98 como edad exacta.
    agregar('edad_98_mas', edad_codigo.eq(98).where(edad_conocida).astype('Int8'), 'p03', 'Indicador de categoría de edad abierta', 'predictor_numerico', '1 si p03=98; 0 si 0..97; ausente si edad desconocida')  # Permite representar la censura superior.
    pea = base['condact'].isin(reglas['codigos_pea'])  # Identifica PEA por definición oficial.
    ocupado = base['condact'].isin(reglas['codigos_ocupados'])  # Identifica ocupación oficial.
    superior = base['p10a'].isin(reglas['niveles_superiores'])  # Identifica el nivel compatible con título superior.
    titulo = base['p12a'].eq(reglas['titulo_afirmativo']).fillna(False)  # Identifica título declarado sin imputar respuestas.
    condiciones = [~edad_conocida, edad_codigo.lt(15).fillna(False), base['condact'].isna(), ~pea, base['p10a'].isna(), ~superior, base['p12a'].isna(), ~titulo]  # Ordena causas de no elegibilidad para evitar doble conteo.
    razones = ['edad_desconocida', 'menor_de_15', 'condicion_desconocida', 'fuera_de_pea', 'nivel_desconocido', 'sin_nivel_superior', 'titulo_desconocido', 'sin_titulo_superior']  # Nombra causas excluyentes según el orden del filtro.
    motivo = pd.Series(np.select([c.to_numpy(dtype=bool) for c in condiciones], razones, default='incluido'), index=base.index, dtype='string')  # Asigna exactamente una razón por registro.
    elegible = motivo.eq('incluido')  # Define el dominio principal del estudio.
    agregar('motivo_elegibilidad', motivo, 'p03,condact,p10a,p12a', 'Primera razón de exclusión o inclusión', 'trazabilidad', 'Edad conocida >=15; PEA; nivel 8..10; p12a=1, en ese orden', 'Nunca ausente')  # Mantiene explícitas las exclusiones.
    agregar('dominio_estudio', elegible, 'motivo_elegibilidad', 'PEA con título superior declarado y edad compatible', 'dominio_inferencia', 'True si motivo_elegibilidad=incluido', 'Nunca ausente')  # Conserva la muestra completa para inferencia de dominio.
    agregar('dominio_ingresos', elegible & ocupado, 'dominio_estudio,condact', 'Ocupados del dominio educativo', 'dominio_ingresos', 'dominio_estudio y condact en 1..6', 'Nunca ausente')  # Separa ocupación de la PEA.
    y_descriptivo = base['condact'].eq('1').where(elegible).astype('Int8')  # Construye el indicador oficial dentro de su denominador.
    agregar('adecuado_descriptivo', y_descriptivo, 'condact,dominio_estudio', 'Pertenencia a categoría oficial de empleo adecuado', 'resultado_descriptivo', '1 si condact=1; 0 si 2..8 dentro del dominio', 'Fuera del dominio del estudio')  # No confunde 0 con inadecuación comprobada de condact=6.
    en_modelo = elegible & base['condact'].ne('6').fillna(False)  # Deja sin etiqueta principal los casos no clasificados.
    agregar('en_modelo_principal', en_modelo, 'dominio_estudio,condact', 'Registros con etiqueta principal utilizable', 'dominio_predictivo', 'dominio_estudio excluyendo condact=6', 'Nunca ausente')  # Documenta el cambio de denominador.
    agregar('y_adecuado', y_descriptivo.where(en_modelo).astype('Int8'), 'adecuado_descriptivo,en_modelo_principal', 'Etiqueta binaria para clasificación principal', 'resultado_predictivo', '1 adecuado; 0 condact 2..5,7..8; ausente condact=6 o fuera del dominio')  # Crea el objetivo sin imputar no clasificados.
    for nombre, codigos in [('subempleo_descriptivo', ['2', '3']), ('desempleo_descriptivo', ['7', '8'])]:  # Prepara otros indicadores solicitados para el futuro dashboard.
        agregar(nombre, base['condact'].isin(codigos).where(elegible).astype('Int8'), 'condact,dominio_estudio', nombre.replace('_', ' '), 'resultado_descriptivo', f'1 si condact en {codigos}; 0 otras categorías PEA; ausente fuera del dominio')  # Mantiene el mismo denominador descriptivo.

    # BLOQUE 4: conservar cantidad y estado del ingreso como variables diferentes.
    ingreso = numerica(base['ingrl'])  # Interpreta la columna sin sobrescribir sus códigos originales.
    estado = pd.Series('fuera_ocupacion_oficial', index=base.index, dtype='string')  # No presume que cada fila deba informar ingreso laboral.
    estado.loc[ocupado] = 'valor_no_interpretable'  # Hace visible cualquier caso no previsto en las reglas.
    estado.loc[ocupado & base['ingrl'].isna()] = 'vacio_otro_ocupado'  # Distingue ausencia en ocupados.
    estado.loc[ocupado & base['ingrl'].isna() & base['condact'].eq('5')] = 'vacio_no_remunerado'  # Preserva la ausencia asociada a empleo no remunerado.
    estado.loc[ocupado & ingreso.eq(-1).fillna(False)] = 'gasta_mas_de_lo_que_gana'  # Aplica el significado oficial, no una pérdida exacta de un dólar.
    estado.loc[ocupado & ingreso.eq(999999).fillna(False)] = 'no_informa'  # Identifica no respuesta codificada.
    estado.loc[ocupado & ingreso.eq(0).fillna(False)] = 'cero_declarado'  # Mantiene ceros reales diferenciados de ausencias.
    estado.loc[ocupado & ingreso.gt(0).fillna(False) & ingreso.ne(999999).fillna(False)] = 'monto_positivo'  # Reconoce cantidades positivas distintas del código especial.
    utilizable = estado.isin(['cero_declarado', 'monto_positivo'])  # Define observaciones aptas para una distribución monetaria principal.
    agregar('estado_ingreso_laboral', estado, 'ingrl,condact', 'Significado del valor o ausencia de ingreso', 'calidad_ingreso', 'Clasificación separada de no remuneración, vacío, -1, 999999, cero y positivo', 'Nunca ausente')  # Documenta el estado sin imputar.
    agregar('ingreso_laboral_monto', ingreso.where(utilizable).astype('Float64'), 'ingrl,estado_ingreso_laboral', 'Monto observado no negativo utilizable; sin imputación', 'resultado_secundario', 'Solo ceros declarados y montos positivos de ocupados; excluir códigos -1 y 999999', 'Estado no cuantificable o fuera de ocupación oficial')  # Evita incorporar códigos a medias y logaritmos.
    agregar('ingreso_monto_observado', base['dominio_ingresos'] & utilizable, 'dominio_ingresos,estado_ingreso_laboral', 'Subdominio con monto utilizable', 'dominio_ingresos', 'dominio_ingresos y estado cero_declarado o monto_positivo', 'Nunca ausente')  # No sustituye el dominio total de ocupados.
    assert not estado.eq('valor_no_interpretable').any()  # Detiene la preparación si aparece un caso monetario no contemplado.

    # BLOQUE 5: añadir etiquetas oficiales sin perder los códigos originales.
    for campo, nombre in [('p02', 'sexo_etiqueta'), ('p06', 'estado_civil_etiqueta'), ('p07', 'asistencia_etiqueta'), ('p10a', 'nivel_reportado_etiqueta'), ('p15', 'etnia_etiqueta'), ('prov', 'provincia_etiqueta'), ('area', 'area_etiqueta'), ('condact', 'condicion_etiqueta')]:  # Selecciona etiquetas útiles para lectura y dashboard.
        mapa = {str(int(float(codigo))): etiqueta.strip() for codigo, etiqueta in catalogo['etiquetas_valores'][campo].items()}  # Normaliza códigos de metadatos sin cambiar su significado.
        etiquetas = base[campo].map(mapa).astype('string')  # Traduce códigos conservando valores desconocidos como ausentes.
        assert not (base[campo].notna() & etiquetas.isna()).any()  # Evita etiquetas inventadas para categorías nuevas.
        agregar(nombre, etiquetas, campo, f'Etiqueta oficial de {campo}', 'etiqueta_descriptiva', 'Mapeo del catálogo SPSS anual 2025; original conservado')  # Documenta el origen de cada texto.

    # BLOQUE 6: validar claves antes de crear agrupaciones sin mes.
    for campo, componentes in [('id_vivienda', ['upm', 'panelm', 'vivienda', 'mes']), ('id_hogar', ['upm', 'panelm', 'vivienda', 'hogar', 'mes']), ('id_persona', ['upm', 'panelm', 'vivienda', 'hogar', 'p01', 'mes'])]:  # Define la composición confirmada en EDA 02.
        reconstruida = base[componentes[0]].copy()  # Inicia la concatenación con UPM original.
        for componente in componentes[1:]:  # Añade componentes conservando sus ceros y anchuras.
            reconstruida = reconstruida + base[componente]  # Concatena texto, no suma números.
        assert base[campo].eq(reconstruida).all()  # Impide retirar el mes cuando la estructura no se cumple.
    for campo, nombre in [('id_vivienda', 'id_vivienda_sin_mes'), ('id_hogar', 'id_hogar_sin_mes'), ('id_persona', 'clave_posicion_sin_mes')]:  # Crea claves de agrupación documentadas.
        agregar(nombre, base[campo].str[:-2], campo, 'Clave estructural sin sufijo mensual; no identidad longitudinal garantizada', 'identificador_agrupacion', 'Retirar dos caracteres finales tras validar toda la composición')  # Mantiene la advertencia sobre seguimiento individual.

    # BLOQUE 7: asignar UPM a entrenamiento/prueba y a cinco pliegues, sin usar el resultado.
    assert base.groupby('upm')['estrato'].nunique().le(1).all()  # Exige que cada UPM pertenezca a un único estrato.
    asignacion = base[['upm', 'estrato']].drop_duplicates().sort_values(['estrato', 'upm']).reset_index(drop=True)  # Construye una tabla por conglomerado de la muestra completa.
    asignacion['particion_ml'] = 'entrenamiento'  # Inicializa todos los conglomerados como entrenamiento.
    asignacion['pliegue_cv'] = pd.Series(pd.NA, index=asignacion.index, dtype='Int8')  # Reserva la validación cruzada exclusivamente para entrenamiento.
    def orden_hash(upm, proposito):  # Produce un orden reproducible independiente de etiquetas o ingresos.
        return hashlib.sha256(f"{reglas['semilla']}|{proposito}|{upm}".encode()).hexdigest()  # Incluye semilla, propósito y grupo.
    for estrato, grupo in asignacion.groupby('estrato', sort=True):  # Asigna grupos dentro de cada estrato.
        orden = sorted(grupo.index, key=lambda i: orden_hash(asignacion.at[i, 'upm'], 'prueba'))  # Ordena UPM con una clave pseudoaleatoria estable.
        n_prueba = max(1, min(len(orden)-1, math.floor(len(orden)*reglas['fraccion_upm_prueba']+0.5)))  # Aproxima 20% de UPM conservando ambos conjuntos.
        assert len(orden) >= 2  # Evita una asignación imposible dentro de un estrato unitario.
        asignacion.loc[orden[:n_prueba], 'particion_ml'] = 'prueba'  # Asigna de una vez; no repite semillas para mejorar resultados.
        entrenamiento = sorted(orden[n_prueba:], key=lambda i: orden_hash(asignacion.at[i, 'upm'], 'validacion'))  # Usa un orden distinto para pliegues internos.
        for posicion, indice in enumerate(entrenamiento):  # Distribuye UPM de entrenamiento entre cinco pliegues.
            asignacion.at[indice, 'pliegue_cv'] = posicion % reglas['pliegues_validacion_entrenamiento'] + 1  # Mantiene juntas todas las filas de cada UPM.
    mapa = asignacion.set_index('upm')  # Prepara una correspondencia única por UPM.
    agregar('particion_ml', base['upm'].map(mapa['particion_ml']).astype('string'), 'upm,estrato', 'Asignación de UPM a entrenamiento o prueba', 'metadato_ml', 'SHA256 con semilla fija; aproximadamente 20% de UPM por estrato para prueba', 'Nunca ausente')  # Propaga la asignación a toda observación de la UPM.
    agregar('pliegue_cv', base['upm'].map(mapa['pliegue_cv']).astype('Int8'), 'upm,estrato', 'Pliegue de validación cruzada en entrenamiento', 'metadato_ml', '1..5 por UPM de entrenamiento; ausente en prueba', 'Conjunto de prueba reservado')  # No asigna pliegues a la prueba.
    guardar_csv(asignacion, DATOS / 'asignacion_upm.csv')  # Guarda la partición para reutilizarla en todas las etapas posteriores.

    # BLOQUE 8: comprobar disyunción de grupos y respetar la lista permitida de predictores.
    solapamientos = []  # Recoge pruebas de no mezcla de unidades observadas.
    for campo in ['upm', 'id_vivienda_sin_mes', 'id_hogar_sin_mes', 'clave_posicion_sin_mes']:  # Comprueba agrupación en todos los niveles disponibles.
        train = set(base.loc[base['particion_ml'].eq('entrenamiento'), campo].dropna())  # Obtiene claves de entrenamiento.
        test = set(base.loc[base['particion_ml'].eq('prueba'), campo].dropna())  # Obtiene claves reservadas.
        comun = len(train & test)  # Cuenta intersecciones sin exportar las claves personales.
        solapamientos.append({'clave': campo, 'claves_entrenamiento': len(train), 'claves_prueba': len(test), 'claves_compartidas': comun})  # Documenta cobertura de la verificación.
        assert comun == 0  # Detiene la exportación si una unidad observada cruza ambos conjuntos.
        assert base.loc[base['particion_ml'].eq('entrenamiento')].groupby(campo)['pliegue_cv'].nunique().le(1).all()  # También impide cruces de claves entre pliegues de entrenamiento.
    guardar_csv(pd.DataFrame(solapamientos), REPORTES / '04_solapamiento_particiones.csv')  # Publica comprobaciones agregadas.
    predictores = reglas['predictores_numericos'] + reglas['predictores_categoricos']  # Utiliza exclusivamente la lista preespecificada.
    assert not set(predictores) & set(reglas['prohibidos_como_predictores'])  # Rechaza cualquier cruce con campos excluidos.
    assert base.loc[en_modelo, predictores].notna().all().all()  # Confirma que no hace falta imputar los predictores de esta selección.
    contexto = ['id_persona', 'id_vivienda_sin_mes', 'id_hogar_sin_mes', 'clave_posicion_sin_mes', 'upm', 'estrato', 'fexp', 'particion_ml', 'pliegue_cv', 'y_adecuado']  # Separa identificadores, ponderación y etiqueta de las características predictoras.
    columnas_modelo = contexto + predictores  # Construye un archivo con esquema explícito; contexto no es X.
    modelo = base.loc[en_modelo, columnas_modelo].copy()  # Separa únicamente los registros etiquetados.
    assert modelo['y_adecuado'].isin([0, 1]).all()  # No entrega etiquetas vacías o categorías no binarias.

    # BLOQUE 9: registrar tamaños y balance de covariables sin evaluar el resultado en prueba.
    flujo = []  # Acumula recuentos de inclusión secuencial.
    mascara = pd.Series(True, index=base.index)  # Empieza con todos los registros originales.
    for etapa, filtro in [('Original completo', mascara.copy()), ('Edad conocida y al menos 15', edad_conocida & edad_codigo.ge(15).fillna(False)), ('Dentro de la PEA', pea), ('Nivel superior reportado', superior), ('Título superior declarado', titulo), ('Etiqueta laboral principal disponible', base['condact'].ne('6').fillna(False))]:  # Aplica filtros preestablecidos en el mismo orden de selección.
        antes = int(mascara.sum())  # Registra el denominador previo.
        mascara = mascara & filtro  # Retiene los registros que cumplen esta condición y las anteriores.
        flujo.append({'etapa': etapa, 'registros_antes': antes, 'registros_despues': int(mascara.sum()), 'excluidos_en_paso': antes-int(mascara.sum())})  # Evita sumar exclusiones superpuestas.
    guardar_csv(pd.DataFrame(flujo), REPORTES / '02_flujo_seleccion.csv')  # Guarda el flujo que acompañará al informe de investigación.
    guardar_csv(base.groupby('motivo_elegibilidad').size().rename('registros').reset_index(), REPORTES / '03_motivos_elegibilidad.csv')  # Expone razones excluyentes y desconocidos.
    tamanos = []  # Recoge tamaños de muestra por uso y conjunto, sin prevalencia del resultado.
    for nombre, tabla in [('muestra_completa', base), ('dominio_estudio', base.loc[elegible]), ('modelo_principal', modelo)]:  # Separa los tres denominadores principales.
        for particion, grupo in tabla.groupby('particion_ml'):  # Resume cada conjunto reservado.
            tamanos.append({'uso': nombre, 'particion': particion, 'registros': len(grupo), 'upm': grupo['upm'].nunique(), 'estratos': grupo['estrato'].nunique(), 'suma_fexp_original': float(grupo['fexp'].sum())})  # Los pesos siguen siendo anuales originales, no pesos nuevos del split.
    guardar_csv(pd.DataFrame(tamanos), REPORTES / '05_tamanos_particiones.csv')  # Guarda cobertura, no desempeño ni tasas de y.
    guardar_csv(modelo.loc[modelo['particion_ml'].eq('entrenamiento')].groupby('pliegue_cv').agg(registros=('upm', 'size'), upm=('upm', 'nunique')).reset_index(), REPORTES / '06_pliegues_entrenamiento.csv')  # Describe tamaños de validación interna.
    balance = []  # Examina balance de covariables con una partición fija.
    for campo in reglas['predictores_categoricos']:  # Revisa distribución de las características sin consultar su asociación con y.
        for particion, grupo in modelo.groupby('particion_ml'):  # Describe entrenamiento y prueba por separado.
            for categoria, segmento in grupo.groupby(campo):  # Obtiene cada categoría observada.
                balance.append({'variable': campo, 'codigo': categoria, 'particion': particion, 'n': len(segmento), 'proporcion_sin_peso': len(segmento)/len(grupo), 'proporcion_con_peso': float(segmento['fexp'].sum()/grupo['fexp'].sum())})  # No ajusta la semilla a estas diferencias.
    guardar_csv(pd.DataFrame(balance), REPORTES / '07_balance_covariables.csv')  # Publica el balance sin declarar equivalencia estadística.

    # BLOQUE 10: exportar conjuntos por finalidad y esquemas para volver a leerlos correctamente.
    print('Grupos verificados; exportando bases y diccionario.', flush=True)  # Comunica que la partición superó controles.
    conjuntos = {  # Define explícitamente cada archivo y su denominador.
        'personas_tratada_completa.csv.gz': base,  # Conserva las filas fuera del dominio para el diseño completo.
        'dominio_educacion_superior.csv': base.loc[elegible],  # Entrega el dominio principal en CSV editable sin compresión.
        'ocupados_ingresos.csv': base.loc[base['dominio_ingresos'], ['id_persona', 'upm', 'estrato', 'fexp', 'particion_ml', 'pliegue_cv', 'p02', 'prov', 'area', 'p10a', 'edad_limite_inferior', 'edad_98_mas', 'mes', 'condact', 'ingrl', 'estado_ingreso_laboral', 'ingreso_laboral_monto', 'ingreso_monto_observado']],  # Incluye ocupados sin monto utilizable para no ocultar ausencias.
        'modelado/entrenamiento.csv': modelo.loc[modelo['particion_ml'].eq('entrenamiento')],  # Entrega datos para desarrollo y validación agrupada.
        'modelado/prueba_reservada.csv': modelo.loc[modelo['particion_ml'].eq('prueba')],  # Reserva evaluación final; no se usa para ajustar modelos.
    }  # Cierra el catálogo de productos de datos.
    esquema = {'version': reglas['version'], 'codificacion': 'utf-8-sig', 'separador': ',', 'decimal': '.', 'ausentes': 'campo vacío', 'tipos': {campo: str(base[campo].dtype) for campo in base.columns}, 'predictores': predictores, 'columnas_contexto_no_predictoras': contexto, 'archivos': {nombre: list(tabla.columns) for nombre, tabla in conjuntos.items()}}  # Permite recuperar tipos y ceros iniciales al leer CSV.
    productos = []  # Acumula tamaños y huellas de salidas.
    for nombre, tabla in conjuntos.items():  # Guarda cada vista con su finalidad explícita.
        ruta = DATOS / nombre  # Resuelve la ruta final.
        guardar_csv(tabla, ruta)  # Escribe la tabla sin índice artificial.
        productos.append({'archivo': nombre, 'filas': len(tabla), 'columnas': len(tabla.columns), 'bytes': ruta.stat().st_size, 'sha256': huella(ruta)})  # Registra integridad para validación de lectura.
    (DATOS / 'esquema_lectura.json').write_text(json.dumps(esquema, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda reglas de lectura y lista permitida.
    guardar_csv(pd.DataFrame(diccionario), DATOS / 'diccionario_base_tratada.csv')  # Entrega diccionario editable con una fila por columna.
    (DATOS / 'etiquetas_oficiales.json').write_text(json.dumps(catalogo['etiquetas_valores'], ensure_ascii=False, indent=2), encoding='utf-8')  # Conserva catálogos sin inventar categorías.
    guardar_csv(pd.DataFrame(productos), REPORTES / '08_manifiesto_productos.csv')  # Guarda huellas y dimensiones de todos los conjuntos.
    assert len(base) == 334786 and int(elegible.sum()) == 39551 and len(modelo) == 39293  # Concilia con los recuentos independientes de EDA 02.
    assert huella(origen) == reglas['sha256_fuente_csv']  # Confirma que los originales no cambiaron.
    resumen = {'ejecutado_utc': datetime.now(timezone.utc).isoformat(), 'config_sha256': huella(CONFIG), 'fuente_sha256': huella(origen), 'asignacion_upm_sha256': huella(DATOS / 'asignacion_upm.csv'), 'semilla': reglas['semilla'], 'filas_completas': len(base), 'columnas_originales_conservadas': len(originales), 'columnas_derivadas': len(base.columns)-len(originales), 'filas_dominio': int(elegible.sum()), 'filas_modelo': len(modelo), 'sin_etiqueta_condact6': int((elegible & ~en_modelo).sum()), 'filas_ocupados': int(base['dominio_ingresos'].sum()), 'filas_ingreso_monto_observado': int(base['ingreso_monto_observado'].sum()), 'predictores': predictores, 'particiones': tamanos, 'filas_eliminadas_muestra_completa': 0, 'celdas_imputadas': 0, 'ingresos_recortados': 0, 'solapamientos': solapamientos, 'prueba_evaluada': False, 'productos': productos}  # Resume hechos y límites de esta etapa.
    (REPORTES / '00_resumen_preparacion.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Publica el resumen reproducible.
    print(json.dumps({k: resumen[k] for k in ['filas_completas', 'filas_dominio', 'filas_modelo', 'filas_ocupados', 'filas_ingreso_monto_observado', 'columnas_derivadas']}, ensure_ascii=False, indent=2), flush=True)  # Muestra recuentos sin explorar la prueba.
    return resumen  # Permite consultar resultados desde Jupyter.

if __name__ == '__main__':  # Ejecuta solo cuando se llama al archivo directamente.
    preparar()  # Inicia el proceso completo de preparación.
