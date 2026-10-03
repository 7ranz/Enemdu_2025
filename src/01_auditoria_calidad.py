# ETAPA 2 DEL EDA: calidad, identificadores y consistencia mensual de ENEMDU anual 2025.
# ARCHIVO: 01_auditoria_calidad.py. Audita los originales; no limpia ni elimina registros.
# BLOQUE 1: dependencias y rutas. Ejecutar desde cualquier carpeta con Python 3.10 o posterior.
import hashlib  # Calcula huellas para verificar que los originales no cambiaron.
import json  # Guarda el resumen de la ejecución.
import platform  # Registra la versión de Python utilizada.
import argparse  # Permite reutilizar únicamente perfiles ya verificados de la misma fuente.
from datetime import datetime, timezone  # Registra la fecha y hora con zona horaria.
from pathlib import Path  # Construye rutas independientes del equipo.
from zipfile import ZipFile  # Lee las tablas sin descomprimir ni editar el ZIP.
import numpy as np  # Evalúa números finitos y calcula resúmenes numéricos.
import pandas as pd  # Procesa tablas y agrupaciones de registros.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza la raíz del proyecto desde el archivo.
ZIP = RAIZ / 'data/raw/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip'  # Identifica la fuente oficial.
SALIDA = RAIZ / 'reports/calidad'  # Ubica todos los resultados de esta etapa.
SALIDA.mkdir(parents=True, exist_ok=True)  # Crea la carpeta de reportes si no existe.

def guardar(tabla, nombre):  # Guarda una tabla agregada sin modificar los microdatos.
    tabla.to_csv(SALIDA / nombre, index=False, encoding='utf-8-sig')  # Usa CSV compatible con Python y Excel.

def numero(serie):  # Convierte una copia numérica respetando la coma decimal del archivo.
    return pd.to_numeric(serie.str.replace(',', '.', regex=False).replace('', np.nan), errors='coerce')  # Deja lo no convertible como ausente.

def perfilar(tabla, nombre):  # Examina cada columna y mes, incluidos campos fuera del modelo.
    filas = []  # Acumula las medidas de calidad por variable y periodo.
    grupos = [('ANUAL', tabla)] + list(tabla.groupby('mes', sort=True))  # Incluye el total y cada mes observado.
    for mes, grupo in grupos:  # Recorre cada corte temporal.
        for campo in grupo.columns:  # Revisa todas las variables disponibles.
            original = grupo[campo]  # Conserva el texto original sin sobrescribirlo.
            texto = original.str.strip()  # Detecta espacios externos en una copia.
            vacio = texto.eq('')  # Identifica vacíos físicos, no todos los tipos de no respuesta.
            numeros = numero(texto)  # Intenta interpretar números sin afirmar que los códigos sean magnitudes.
            finitos = numeros[np.isfinite(numeros)]  # Retiene números finitos solo para describir el rango.
            filas.append({'tabla': nombre, 'mes': mes, 'variable': campo, 'n': len(grupo), 'vacios': int(vacio.sum()), 'pct_vacios': float(vacio.mean()*100), 'distintos_no_vacios': int(texto[~vacio].nunique()), 'espacios_externos': int(original.ne(texto).sum()), 'no_numericos_no_vacios': int((~vacio & numeros.isna()).sum()), 'min_numerico': finitos.min() if len(finitos) else None, 'max_numerico': finitos.max() if len(finitos) else None})  # Resume sin imputar ni recodificar.
    return pd.DataFrame(filas)  # Devuelve el perfil completo de esta tabla.

def auditar(reutilizar_perfil=False):  # Define el procedimiento reproducible; por defecto recalcula todo.
    huella_antes = hashlib.sha256(ZIP.read_bytes()).hexdigest()  # Registra la integridad del original al iniciar.
    with ZipFile(ZIP) as archivo:  # Abre el archivo fuente en modo lectura.
        danado = archivo.testzip()  # Revisa CRC de todos sus miembros.
        if danado is not None:  # No continúa sobre un contenedor dañado.
            raise ValueError(f'Miembro ZIP dañado: {danado}')  # Explica qué archivo falló.
        p = pd.read_csv(archivo.open('BDDenemdu_personas_2025_anual.csv'), sep=';', encoding='utf-8-sig', dtype=str, keep_default_na=False, on_bad_lines='error')  # Lee personas preservando ceros y vacíos.
        v = pd.read_csv(archivo.open('BDDenemdu_vivienda_2025_anual.csv'), sep=';', encoding='utf-8-sig', dtype=str, keep_default_na=False, on_bad_lines='error')  # Lee vivienda-hogar con las mismas reglas.
    print('Tablas leídas; perfilando todas las columnas y meses.', flush=True)  # Comunica el avance sin mostrar registros personales.

    # BLOQUE 2: perfiles completos y cambios de disponibilidad entre meses.
    previo = SALIDA / '00_resumen_auditoria.json'  # Localiza evidencia de una ejecución anterior.
    cache_valida = reutilizar_perfil and previo.exists() and (SALIDA / '01_perfil_variables_mes.csv').exists()  # Exige archivos previos antes de reutilizar.
    if cache_valida:  # Comprueba que el perfil pertenece exactamente al mismo original.
        cache_valida = json.loads(previo.read_text(encoding='utf-8'))['sha256_original'] == huella_antes  # Compara huellas de la fuente.
    if cache_valida:  # Reutiliza el perfil solo cuando se solicita y la fuente coincide.
        perfiles = pd.read_csv(SALIDA / '01_perfil_variables_mes.csv', dtype={'mes': str})  # Lee el perfil sin cambiar su contenido.
    else:  # Recalcula por defecto o cuando la fuente no coincide.
        perfiles = pd.concat([perfilar(p, 'personas'), perfilar(v, 'vivienda_hogar')], ignore_index=True)  # Combina perfiles de ambas tablas.
    guardar(perfiles, '01_perfil_variables_mes.csv')  # Publica faltantes, tipos aparentes y rangos.
    cambios = perfiles.loc[perfiles['mes'].ne('ANUAL')].groupby(['tabla', 'variable']).agg(pct_vacio_min=('pct_vacios', 'min'), pct_vacio_max=('pct_vacios', 'max'), meses_totalmente_vacios=('pct_vacios', lambda s: int(s.eq(100).sum()))).reset_index()  # Resume variación de disponibilidad.
    cambios['diferencia_pp'] = cambios['pct_vacio_max'] - cambios['pct_vacio_min']  # Calcula amplitud entre meses en puntos porcentuales.
    guardar(cambios.sort_values('diferencia_pp', ascending=False), '02_cambios_disponibilidad.csv')  # Ordena señales que requieren interpretación de flujos.
    p = p.apply(lambda columna: columna.str.strip())  # Normaliza espacios solo en la copia de auditoría; los vacíos de origen incluyen espacios.
    v = v.apply(lambda columna: columna.str.strip())  # Aplica la misma convención a vivienda-hogar antes de comprobar relaciones.
    reglas = []  # Acumula resultados de controles explícitos.

    def control(codigo, descripcion, mascara, ambito=None, tipo='consistencia'):  # Registra alertas con su denominador, anual y mensual.
        ambito = pd.Series(True, index=p.index) if ambito is None else ambito.fillna(False)  # Define registros a los que aplica la regla.
        alerta = mascara.fillna(False) & ambito  # Cuenta solo alertas dentro del dominio válido de la regla.
        for mes in ['ANUAL'] + sorted(p['mes'].unique().tolist()):  # Genera evidencia del total y los meses.
            seleccion = ambito if mes == 'ANUAL' else ambito & p['mes'].eq(mes)  # Restringe el denominador al mes elegido.
            reglas.append({'regla': codigo, 'descripcion': descripcion, 'tipo': tipo, 'mes': mes, 'n_aplicables': int(seleccion.sum()), 'n_alertas': int((alerta & seleccion).sum())})  # Conserva resultados interpretables.

    # BLOQUE 3: códigos documentados, faltantes estructurales y coherencia de población.
    edad = numero(p['p03'])  # Obtiene una copia numérica de edad.
    peso = numero(p['fexp'])  # Interpreta la coma decimal del factor de expansión.
    condicion = numero(p['condact'])  # Obtiene códigos laborales numéricos.
    superior = p['p10a'].isin(['8', '9', '10'])  # Identifica el flujo de educación superior.
    pea = condicion.between(1, 8)  # Define PEA conforme a sintaxis oficial.
    ocupado = condicion.between(1, 6)  # Define población ocupada conforme a sintaxis oficial.
    candidato_previo = edad.ge(15) & superior & p['p12a'].eq('1') & pea  # Reproduce la selección inicial para compararla.
    candidato = candidato_previo & edad.ne(99)  # Evita interpretar el código documentado 99 como edad real.
    control('Q01', 'Edad vacía o no numérica', edad.isna(), tipo='formato')  # Comprueba convertibilidad de edad.
    control('Q02', 'Edad 99: código de no respuesta según guía; revisar también manual', edad.eq(99), tipo='codigo_especial')  # Separa ausencia codificada de edad observada.
    control('Q04', 'Edad 98: categoría abierta 98 y más según etiquetas SPSS 2025', edad.eq(98), tipo='codigo_especial')  # Evita interpretar el extremo superior como edad exacta.
    control('Q03', 'Edad negativa, mayor de 99 o no entera: revisión', edad.lt(0) | edad.gt(99) | edad.mod(1).ne(0), edad.notna(), 'revision')  # Localiza valores fuera del rango operativo.
    dominios = {'area': {'1', '2'}, 'p02': {'1', '2'}, 'p06': set(map(str, range(1, 7))), 'p07': {'1', '2'}, 'p10a': set(map(str, range(1, 11))), 'p12a': {'1', '2'}, 'p15': set(map(str, range(1, 9))), 'condact': set(map(str, range(10))), 'mes': {f'{m:02}' for m in range(1, 13)}}  # Usa categorías del formulario y sintaxis, no etiquetas supuestas.
    for campo, permitidos in dominios.items():  # Revisa el dominio categórico documentado.
        control(f'D_{campo}', f'Código no vacío fuera de dominio en {campo}', ~p[campo].isin(permitidos), p[campo].ne(''), 'dominio')  # Distingue inválidos de ausencias.
    for campo in ['area', 'p02', 'p03', 'condact', 'prov', 'mes', 'periodo', 'upm', 'estrato', 'id_vivienda', 'id_hogar', 'id_persona']:  # Enumera campos estructurales imprescindibles.
        control(f'F_{campo}', f'Campo estructural vacío: {campo}', p[campo].eq(''), tipo='faltante')  # Cuenta faltantes sin imputarlos.
    for campo in ['p10a', 'p07', 'p15']:  # Evalúa preguntas de personas de cinco años o más.
        control(f'E_{campo}', f'{campo} vacío en personas con edad conocida >=5', p[campo].eq(''), edad.ge(5) & edad.ne(99), 'flujo')  # No acusa como error la ausencia en menores.
    control('E_titulo', 'Respuesta de título ausente o inválida en nivel superior', ~p['p12a'].isin(['1', '2']), superior, 'flujo')  # Valida la variable decisiva de selección.
    control('E_fuera_flujo', 'Respuesta de título fuera de niveles 8–10', p['p12a'].ne(''), ~superior, 'flujo')  # Revisa coherencia del salto educativo.
    control('E_codigo_titulo', 'Título declarado sin código p12b', p['p12b'].eq(''), superior & p['p12a'].eq('1'), 'flujo')  # No infiere especialidad cuando falta código.
    control('E_codigo_sin_titulo', 'Código p12b informado sin respuesta afirmativa p12a', p['p12b'].ne(''), ~p['p12a'].eq('1'), 'flujo')  # Identifica contradicciones potenciales.
    control('E_edad_titulo', 'Título superior con edad conocida menor de 18: revisar', edad.lt(18), superior & p['p12a'].eq('1') & edad.ne(99), 'revision')  # Es una señal de revisión, no una exclusión automática.
    control('L_menor15', 'Menor de 15 años con condact distinto de 0', condicion.ne(0), edad.lt(15), 'consistencia')  # Contrasta la regla etaria oficial.
    control('L_adulto0', 'Edad conocida >=15 con condact=0', condicion.eq(0), edad.ge(15) & edad.ne(99), 'consistencia')  # Revisa códigos no esperados en edad laboral.
    control('L_empleo', 'Indicador empleo=1 discrepa de condact 1–6', p['empleo'].eq('1').ne(ocupado), tipo='consistencia')  # Comprueba indicadores derivados.
    control('L_desempleo', 'Indicador desempleo=1 discrepa de condact 7–8', p['desempleo'].eq('1').ne(condicion.isin([7, 8])), tipo='consistencia')  # Comprueba desempleo derivado.
    control('T_periodo', 'Periodo distinto de 2025 seguido del mes', p['periodo'].ne('2025' + p['mes']), tipo='consistencia')  # Valida coherencia de fechas.
    control('W_peso', 'Factor de expansión ausente, no finito o no positivo', ~np.isfinite(peso) | peso.le(0), tipo='diseno')  # Revisa aptitud matemática de los pesos.
    for campo in ['p02', 'p06', 'p07', 'p10a', 'p12a', 'p15', 'prov', 'area', 'p10b']:  # Examina disponibilidad de covariables del estudio.
        control(f'C_{campo}', f'{campo} vacío en población candidata', p[campo].eq(''), candidato, 'faltante_candidato')  # Cuenta solo vacíos dentro del dominio educativo.
    especial = ['p63', 'p64b', 'p65', 'p66', 'p67', 'p68b', 'p69', 'p70b', 'p71b', 'p72b', 'p73b', 'p74b', 'p76', 'p78']  # Enumera ingresos con código 999999 en la guía.
    for campo in especial:  # Separa no respuesta codificada de cantidades monetarias.
        control(f'NR_{campo}', f'No respuesta 999999 en {campo}', numero(p[campo]).eq(999999), tipo='codigo_especial')  # No transforma el código en ingreso real.
    for campo in ['ingrl', 'ingpc']:  # Examina ingresos derivados sin decidir aún su limpieza.
        ingreso = numero(p[campo])  # Interpreta una copia del campo.
        control(f'I_{campo}_negativo', f'Valor negativo de {campo}; revisar semántica de código', ingreso.lt(0), tipo='revision')  # No supone que un negativo sea ingreso válido o error.
        control(f'I_{campo}_alto', f'{campo} >=999999; revisar códigos especiales', ingreso.ge(999999), tipo='revision')  # Detecta valores que requieren documentación adicional.
    control('I_faltante_ocupado', 'Ingreso laboral vacío entre ocupados candidatos', p['ingrl'].eq(''), candidato & ocupado, 'revision')  # Acota la futura muestra de ingresos.
    control('L_no_clasificado', 'Empleo no clasificado dentro de candidatos', condicion.eq(6), candidato, 'decision_analitica')  # Cuantifica la etiqueta que requiere sensibilidad.

    # BLOQUE 4: identificadores, duplicados y relaciones entre tablas.
    print('Perfiles listos; verificando claves, relaciones y repeticiones.', flush=True)  # Informa progreso.
    duplicados = []  # Acumula controles de unicidad por unidad.
    for nombre, tabla, clave in [('personas', p, ['id_persona']), ('personas_mes', p, ['id_persona', 'mes']), ('vivienda_hogar', v, ['id_hogar']), ('vivienda_hogar_mes', v, ['id_hogar', 'mes'])]:  # Distingue claves personales de claves de hogar.
        duplicados.append({'tabla': nombre, 'clave': '+'.join(clave), 'filas': len(tabla), 'claves_distintas': len(tabla[clave].drop_duplicates()), 'filas_en_claves_repetidas': int(tabla.duplicated(clave, keep=False).sum()), 'repeticiones_adicionales': int(tabla.duplicated(clave).sum())})  # No elimina repeticiones.
    for nombre, tabla in [('personas', p), ('vivienda_hogar', v)]:  # Revisa también duplicación exacta de todas las columnas.
        duplicados.append({'tabla': nombre, 'clave': 'TODAS_LAS_COLUMNAS', 'filas': len(tabla), 'claves_distintas': len(tabla.drop_duplicates()), 'filas_en_claves_repetidas': int(tabla.duplicated(keep=False).sum()), 'repeticiones_adicionales': int(tabla.duplicated().sum())})  # Separa duplicados exactos de coincidencias de clave.
    guardar(pd.DataFrame(duplicados), '04_duplicados.csv')  # Guarda el resumen de unicidad.
    formulas = {'id_vivienda': p['upm'] + p['panelm'] + p['vivienda'] + p['mes'], 'id_hogar': p['upm'] + p['panelm'] + p['vivienda'] + p['hogar'] + p['mes'], 'id_persona': p['upm'] + p['panelm'] + p['vivienda'] + p['hogar'] + p['p01'] + p['mes']}  # Formula hipótesis a partir del formato realmente observado.
    reconstruccion_correcta = True  # Controla si es legítimo retirar el sufijo mensual.
    for campo, reconstruido in formulas.items():  # Contrasta cada hipótesis en todas las filas.
        discrepancia = p[campo].ne(reconstruido)  # Localiza claves que no se reconstruyen con sus componentes.
        control(f'ID_{campo}', f'{campo}: discrepancia con reconstrucción UPM/componentes/mes', discrepancia, tipo='identificador')  # Registra la comprobación exhaustiva.
        reconstruccion_correcta = reconstruccion_correcta and not discrepancia.any()  # Solo habilita claves sin mes si todo coincide.
    control('ID_upm_geografia', 'Prefijo de UPM distinto de ciudad normalizada; conservar y revisar geografía', p['upm'].str[:6].ne(p['ciudad'].str.zfill(6)), tipo='revision_cartografica')  # Señala diferencias, sin declarar que ciudad deba reconstruir la UPM histórica.
    control('ID_provincia', 'Provincia distinta del prefijo de ciudad', numero(p['prov']).ne(numero(p['ciudad'].str.zfill(6).str[:2])), tipo='identificador')  # Contrasta dos codificaciones territoriales.
    dependencias = []  # Registra correspondencias que deberían ser únicas dentro de una clave.
    for clave, atributos in [('id_persona', ['id_hogar', 'id_vivienda', 'upm', 'mes']), ('id_hogar', ['id_vivienda', 'upm', 'mes', 'estrato', 'prov', 'area']), ('upm', ['estrato', 'prov', 'area'])]:  # Define relaciones funcionales necesarias.
        maximos = p.groupby(clave)[atributos].nunique(dropna=False)  # Cuenta valores distintos por identificador.
        for atributo in atributos:  # Registra cada relación por separado.
            dependencias.append({'clave': clave, 'atributo': atributo, 'n_claves': len(maximos), 'claves_con_mas_de_un_valor': int(maximos[atributo].gt(1).sum())})  # Una señal no altera los datos automáticamente.
    guardar(pd.DataFrame(dependencias), '05_dependencias_identificadores.csv')  # Conserva la evidencia de jerarquías.
    enlace = p[['id_hogar', 'mes', 'area', 'upm', 'estrato', 'fexp']].merge(v[['id_hogar', 'mes', 'area', 'upm', 'estrato', 'fexp']], on=['id_hogar', 'mes'], how='left', validate='many_to_one', indicator=True, suffixes=('_p', '_v'))  # Verifica unión sin multiplicar personas.
    union = [{'control': 'personas_sin_hogar_en_tabla_vivienda', 'n': int(enlace['_merge'].ne('both').sum())}, {'control': 'hogares_tabla_vivienda_sin_personas', 'n': int((~v['id_hogar'].isin(p['id_hogar'])).sum())}]  # Comprueba cobertura en ambas direcciones.
    for campo in ['area', 'upm', 'estrato', 'fexp']:  # Compara campos comunes de los registros enlazados.
        diferencia = enlace[f'{campo}_p'].ne(enlace[f'{campo}_v']) if campo != 'fexp' else ~np.isclose(numero(enlace['fexp_p']), numero(enlace['fexp_v']), rtol=1e-10, atol=1e-10)  # Tolera únicamente redondeo numérico de pesos.
        union.append({'control': f'diferencia_{campo}_persona_vivienda', 'n': int((diferencia & enlace['_merge'].eq('both')).sum())})  # Cuenta discrepancias sin sobrescribir valores.
    guardar(pd.DataFrame(union), '06_integridad_personas_hogares.csv')  # Publica integridad referencial.

    # BLOQUE 5: repeticiones longitudinales y matriz de solapamiento mensual.
    repeticion = []  # Resume repetición de claves sin mes, sin atribuir identidad personal cierta.
    cambios_persona = []  # Cuantifica incompatibilidades en posiciones del hogar repetidas.
    if reconstruccion_correcta:  # Evita retirar caracteres de identificadores no comprendidos.
        for campo in ['id_vivienda', 'id_hogar', 'id_persona']:  # Examina cada nivel de agrupación.
            base = p[campo].str[:-2]  # Retira el sufijo mensual comprobado en todas las filas.
            n_meses = pd.DataFrame({'base': base, 'mes': p['mes']}).groupby('base')['mes'].nunique()  # Cuenta meses en cada clave estructural.
            repeticion.append({'nivel': campo, 'claves_sin_mes': len(n_meses), 'claves_en_varios_meses': int(n_meses.gt(1).sum()), 'max_meses': int(n_meses.max()), 'filas_en_claves_repetidas': int(base.isin(n_meses[n_meses.gt(1)].index).sum())})  # Distingue claves de personas físicas.
            conjuntos = {mes: set(base[p['mes'].eq(mes)]) for mes in sorted(p['mes'].unique())}  # Construye conjuntos de claves por mes.
            solapamiento = [{'mes_a': a, 'mes_b': b, 'claves_a': len(conjuntos[a]), 'claves_b': len(conjuntos[b]), 'claves_compartidas': len(conjuntos[a] & conjuntos[b])} for a in conjuntos for b in conjuntos]  # Compara todas las parejas de meses.
            guardar(pd.DataFrame(solapamiento), f'07_solapamiento_{campo}.csv')  # Permite revisar el patrón de rotación.
        base_persona = p['id_persona'].str[:-2]  # Identifica posiciones repetidas en hogares sin afirmar seguimiento individual.
        pares = pd.DataFrame({'base': base_persona, 'mes': numero(p['mes']), 'edad': edad.mask(edad.isin([98, 99])), 'sexo': p['p02'], 'titulo': p['p12a'], 'nivel': p['p10a']}).sort_values(['base', 'mes'])  # Compara solo edades exactas, excluyendo categoría abierta y no respuesta.
        anterior = pares.groupby('base').shift(1)  # Obtiene la observación anterior dentro de cada clave.
        comparable = anterior['mes'].notna()  # Selecciona solo pares repetidos.
        for nombre, mascara in [('sexo_cambia', pares['sexo'].ne(anterior['sexo'])), ('edad_disminuye_o_aumenta_mas_de_un_ano', (pares['edad'] - anterior['edad']).lt(0) | (pares['edad'] - anterior['edad']).gt(1)), ('titulo_si_a_no', anterior['titulo'].eq('1') & pares['titulo'].eq('2'))]:  # Define señales de posible cambio de informante, composición o respuesta.
            cambios_persona.append({'revision': nombre, 'pares_comparables': int((comparable & (pares['edad'].notna() & anterior['edad'].notna() if nombre.startswith('edad') else True)).sum()), 'pares_con_senal': int((comparable & mascara).sum())})  # No declara errores ni pérdidas reales de títulos.
        guardar(pd.DataFrame(cambios_persona), '08_cambios_claves_persona.csv')  # Documenta por qué no se asumirán trayectorias individuales.
    guardar(pd.DataFrame(repeticion), '09_repeticion_sin_mes.csv')  # Guarda el tamaño del solapamiento estructural.

    # BLOQUE 6: diseño y cobertura mensual, sin explorar asociaciones predictivas.
    mensual = []  # Recoge tamaños, pesos y selección inicial de cada mes.
    for mes, indices in p.groupby('mes').groups.items():  # Recorre la muestra mensual.
        grupo = p.loc[indices]  # Obtiene los registros correspondientes.
        w = peso.loc[indices]  # Obtiene los pesos anuales de esas observaciones.
        mensual.append({'mes': mes, 'registros': len(grupo), 'hogares_observacion': grupo['id_hogar'].nunique(), 'viviendas_observacion': grupo['id_vivienda'].nunique(), 'upm': grupo['upm'].nunique(), 'estratos': grupo['estrato'].nunique(), 'provincias': grupo['prov'].nunique(), 'candidatos': int(candidato.loc[indices].sum()), 'candidatos_previamente': int(candidato_previo.loc[indices].sum()), 'edad_99': int(edad.loc[indices].eq(99).sum()), 'peso_min': w.min(), 'peso_mediana': w.median(), 'peso_p99': w.quantile(.99), 'peso_max': w.max(), 'suma_pesos_anuales_del_mes': w.sum()})  # No confunde peso anual por mes con estimación mensual oficial.
    guardar(pd.DataFrame(mensual), '10_cobertura_mensual.csv')  # Guarda comparaciones descriptivas de cobertura.
    diseno = p[['estrato', 'upm']].drop_duplicates().groupby('estrato').size().rename('upm_muestra_completa').reset_index()  # Cuenta UPM distintas por estrato en toda la muestra.
    dominio = p.loc[candidato, ['estrato', 'upm']].drop_duplicates().groupby('estrato').size().rename('upm_con_candidatos').reset_index()  # Cuenta presencia del dominio educativo sin redefinir el diseño.
    diseno = diseno.merge(dominio, on='estrato', how='left').fillna({'upm_con_candidatos': 0})  # Conserva estratos sin miembros del dominio.
    guardar(diseno, '11_upm_por_estrato.csv')  # Permite anticipar problemas de estimación de dominios.
    categorias = []  # Prepara distribuciones para revisar estabilidad de códigos.
    for campo in ['area', 'p02', 'p06', 'p07', 'p10a', 'p12a', 'p15', 'prov', 'condact', 'empleo', 'desempleo', 'periodo', 'panelm']:  # Selecciona variables estructurales y del estudio.
        frecuencias = p.groupby(['mes', campo]).size().rename('n').reset_index().rename(columns={campo: 'codigo'})  # Cuenta sin ponderación ni contrastes de hipótesis.
        frecuencias['variable'] = campo  # Identifica qué variable describe cada distribución.
        categorias.append(frecuencias)  # Acumula los resúmenes mensuales.
    guardar(pd.concat(categorias, ignore_index=True), '12_codigos_por_mes.csv')  # Publica categorías observadas sin inventar etiquetas.
    guardar(pd.DataFrame(reglas), '03_reglas_calidad.csv')  # Guarda todas las reglas con denominadores mensuales.
    ingresos = []  # Resume ingresos sin ocultar códigos sospechosos.
    for campo in ['ingrl', 'ingpc']:  # Examina las dos variables derivadas de ingresos.
        x = numero(p[campo])  # Obtiene números sin reemplazar códigos especiales.
        for etiqueta, mascara in [('todos', pd.Series(True, index=p.index)), ('ocupados_candidatos', candidato & ocupado)]:  # Separa universo y dominio pertinente.
            valores = x[mascara]  # Obtiene los valores del dominio.
            ingresos.append({'variable': campo, 'dominio': etiqueta, 'registros': int(mascara.sum()), 'vacios_o_no_numericos': int(valores.isna().sum()), 'negativos': int(valores.lt(0).sum()), 'ceros': int(valores.eq(0).sum()), 'codigo_999999': int(valores.eq(999999).sum()), 'p50_sin_limpieza': valores.median(), 'p99_sin_limpieza': valores.quantile(.99), 'max_sin_limpieza': valores.max()})  # Los cuantiles son diagnósticos, no resultados de ingresos del estudio.
    guardar(pd.DataFrame(ingresos), '13_diagnostico_ingresos.csv')  # Expone límites de los ingresos originales.

    # BLOQUE 7: reconciliaciones internas y trazabilidad de los resultados.
    if sum(fila['registros'] for fila in mensual) != len(p):  # Verifica que los meses recuperan todas las filas.
        raise AssertionError('Los recuentos mensuales no concuerdan con el total')  # Impide una salida aparentemente correcta.
    if len(enlace) != len(p):  # Verifica que la unión no haya multiplicado los registros.
        raise AssertionError('La unión alteró el número de registros de personas')  # Señala una violación de cardinalidad.
    huella_despues = hashlib.sha256(ZIP.read_bytes()).hexdigest()  # Vuelve a medir la integridad del original.
    if huella_antes != huella_despues:  # Comprueba que la auditoría dejó intacta la fuente.
        raise AssertionError('El ZIP original cambió durante la ejecución')  # Detiene la validación si cambia.
    resumen = {'ejecutado_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__, 'sha256_original': huella_antes, 'original_sin_cambios': True, 'filas_personas': len(p), 'columnas_personas': len(p.columns), 'filas_vivienda_hogar': len(v), 'columnas_vivienda_hogar': len(v.columns), 'meses': sorted(p['mes'].unique().tolist()), 'reglas_distintas': len({r['regla'] for r in reglas}), 'candidatos_previamente': int(candidato_previo.sum()), 'candidatos_edad_conocida': int(candidato.sum()), 'candidatos_condact6': int((candidato & condicion.eq(6)).sum()), 'reconstruccion_identificadores_completa': bool(reconstruccion_correcta), 'estratos': len(diseno), 'estratos_una_upm_muestra': int(diseno['upm_muestra_completa'].eq(1).sum()), 'estratos_una_upm_dominio': int(diseno['upm_con_candidatos'].eq(1).sum()), 'peso_total': float(peso.sum()), 'reglas_con_alertas': [r for r in reglas if r['mes']=='ANUAL' and r['n_alertas']>0], 'repeticion': repeticion, 'cambios_posicion_persona': cambios_persona, 'integridad_relacional': union, 'limite': 'Auditoría automatizada exhaustiva de estructura y perfiles; reglas semánticas para variables del estudio. No certifica todas las respuestas ni reconstruye cada salto del cuestionario.'}  # Explicita alcance y resultados.
    (SALIDA / '00_resumen_auditoria.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda un resumen reutilizable.
    print(json.dumps({k: resumen[k] for k in ['filas_personas', 'filas_vivienda_hogar', 'reglas_distintas', 'candidatos_edad_conocida', 'reconstruccion_identificadores_completa', 'estratos_una_upm_muestra']}, ensure_ascii=False, indent=2), flush=True)  # Muestra únicamente conclusiones estructurales.
    return resumen  # Permite usar la auditoría desde el cuaderno didáctico.

if __name__ == '__main__':  # Evita ejecutar el análisis cuando solo se importa el módulo.
    argumentos = argparse.ArgumentParser(description='Auditoría ENEMDU anual 2025')  # Describe las opciones de ejecución.
    argumentos.add_argument('--reutilizar-perfil', action='store_true', help='Reutiliza perfil de columnas si coincide SHA-256; recalcula todas las reglas.')  # Acelera revisiones de reglas sin repetir perfiles invariantes.
    opciones = argumentos.parse_args()  # Lee las opciones indicadas por el usuario.
    auditar(reutilizar_perfil=opciones.reutilizar_perfil)  # Inicia controles completos, con reutilización explícita opcional.
