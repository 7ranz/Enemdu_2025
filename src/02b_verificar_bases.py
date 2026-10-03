# ETAPA 3 DEL EDA: verificar la exportación, la conservación de datos y la separación por grupos.
# ARCHIVO: 02b_verificar_bases.py. Relee los archivos finales y los compara con el original.
# BLOQUE 1: herramientas y lector de tipos de esta etapa.
import ast  # Comprueba la sintaxis de los programas entregados.
import hashlib  # Contrasta huellas de datos y configuración.
import importlib.util  # Carga el lector del proyecto por su ruta.
import json  # Lee manifiestos y guarda evidencia de validación.
from pathlib import Path  # Maneja rutas portables.
from zipfile import ZipFile  # Relee la fuente original sin modificarla.
import numpy as np  # Compara pesos numéricos con tolerancia de representación.
import pandas as pd  # Verifica tablas y grupos.

RAIZ = Path(__file__).resolve().parents[1]  # Ubica el proyecto.
DATOS = RAIZ / 'data/processed'  # Localiza productos finales.
REPORTES = RAIZ / 'reports/preparacion'  # Localiza sus reportes.
especificacion = importlib.util.spec_from_file_location('lector_bases', RAIZ / 'src/02a_leer_bases.py')  # Localiza el lector tipado.
lector = importlib.util.module_from_spec(especificacion)  # Prepara el módulo.
especificacion.loader.exec_module(lector)  # Carga sus funciones.
resumen = json.loads((REPORTES / '00_resumen_preparacion.json').read_text(encoding='utf-8'))  # Lee resultados esperados.
esquema = json.loads((DATOS / 'esquema_lectura.json').read_text(encoding='utf-8'))  # Recupera columnas y tipos esperados.
reglas = json.loads((RAIZ / 'config/preparacion_v1.json').read_text(encoding='utf-8'))  # Recupera decisiones metodológicas.
assert hashlib.sha256((RAIZ / 'config/preparacion_v1.json').read_bytes()).hexdigest() == resumen['config_sha256']  # Detecta cambios de reglas posteriores a la preparación.
origen = RAIZ / 'data/raw/2_BDD_DATOS_ABIERTOS_ENEMDU_2025_CSV.zip'  # Identifica los originales.
assert hashlib.sha256(origen.read_bytes()).hexdigest() == resumen['fuente_sha256']  # Comprueba que la fuente auditada sigue intacta.

# BLOQUE 2: comparar todas las columnas originales por bloques, sin alterar códigos ni registros.
comparadas = 0  # Cuenta filas efectivamente contrastadas con el original.
with ZipFile(origen) as archivo:  # Abre el original para la comprobación independiente.
    originales = pd.read_csv(archivo.open('BDDenemdu_personas_2025_anual.csv'), sep=';', encoding='utf-8-sig', dtype=str, keep_default_na=False, chunksize=20000)  # Lee bloques que preservan el texto original.
    tratados = pd.read_csv(DATOS / 'personas_tratada_completa.csv.gz', encoding='utf-8-sig', dtype=str, keep_default_na=False, chunksize=20000)  # Relee lo realmente guardado, no el objeto de memoria.
    for inicial, final in zip(originales, tratados, strict=True):  # Exige la misma cantidad de bloques en ambos archivos.
        assert len(inicial) == len(final)  # Exige el mismo número y orden de filas.
        for campo in inicial.columns:  # Contrasta los 139 campos originales, no solo unos ejemplos.
            normalizado = inicial[campo].str.strip()  # Aplica únicamente la limpieza de espacios autorizada.
            if campo == 'fexp':  # Trata la representación decimal del peso por separado.
                peso_original = pd.to_numeric(normalizado.str.replace(',', '.', regex=False))  # Recupera el número de origen.
                peso_final = pd.to_numeric(final[campo])  # Recupera el número exportado.
                assert np.allclose(peso_original, peso_final, rtol=1e-12, atol=0)  # Tolera representación decimal sin permitir reponderación.
            else:  # Compara códigos, identificadores y valores originales como texto.
                assert normalizado.reset_index(drop=True).equals(final[campo].reset_index(drop=True)), f'Cambió {campo}'  # Detecta cualquier cambio más allá de espacios.
        comparadas += len(inicial)  # Acumula las filas verificadas.
assert comparadas == resumen['filas_completas']  # Confirma cobertura del archivo entero.
print('Originales conservados en todas las filas; verificando productos y grupos.', flush=True)  # Informa el avance.

# BLOQUE 3: verificar dimensiones, tipos y huellas de cada producto exportado.
productos = []  # Registra comprobaciones de lectura de todos los archivos.
for producto in resumen['productos']:  # Recorre todas las bases de esta etapa.
    ruta = DATOS / producto['archivo']  # Localiza cada salida.
    assert hashlib.sha256(ruta.read_bytes()).hexdigest() == producto['sha256']  # Detecta modificaciones posteriores al manifiesto.
    nombres = esquema['archivos'][producto['archivo']]  # Recupera el orden esperado de columnas.
    tabla = lector.cargar_base(producto['archivo'], columnas=[c for c in nombres if c in {'id_persona', 'upm', 'estrato', 'fexp', 'particion_ml', 'pliegue_cv', 'dominio_estudio', 'en_modelo_principal', 'ingreso_monto_observado', 'y_adecuado'}])  # Prueba lectura tipada de metadatos y dominios.
    encabezado = pd.read_csv(ruta, encoding='utf-8-sig', nrows=0).columns.tolist()  # Lee el encabezado real del archivo.
    assert len(tabla) == producto['filas'] and encabezado == nombres  # Verifica forma completa de la salida.
    assert tabla['id_persona'].is_unique and tabla['id_persona'].notna().all()  # Conserva claves únicas de observación, sin afirmar personas físicas únicas.
    assert tabla['fexp'].gt(0).all()  # Revisa los pesos después de serializar y releer.
    productos.append({'archivo': producto['archivo'], 'filas_verificadas': len(tabla), 'columnas_verificadas': len(encabezado), 'sha256_correcto': True})  # Registra evidencia de cada producto.

# BLOQUE 4: comprobar coherencia de dominios, códigos especiales y etiqueta principal.
dominio = lector.cargar_base('dominio_educacion_superior.csv')  # Relee el dominio completo con sus tipos originales.
assert dominio['dominio_estudio'].all() and len(dominio) == 39551  # Concilia con la auditoría anterior.
assert dominio['p12a'].eq('1').all() and dominio['p10a'].isin(['8', '9', '10']).all()  # Verifica la selección educativa real exportada.
assert dominio['edad_limite_inferior'].ge(15).all()  # Verifica elegibilidad etaria.
assert dominio['y_adecuado'].isna().equals(dominio['condact'].eq('6').astype(bool))  # Exige ausencias de etiqueta exactamente en los no clasificados.
assert dominio.loc[dominio['en_modelo_principal'], 'y_adecuado'].astype(int).eq(dominio.loc[dominio['en_modelo_principal'], 'condact'].eq('1').astype(int)).all()  # Verifica significado del resultado, sin calcular prevalencias de prueba.
ingresos = lector.cargar_base('ocupados_ingresos.csv')  # Relee el conjunto secundario.
assert int(ingresos['ingreso_monto_observado'].sum()) == 35080  # Concilia disponibilidad monetaria con los códigos especiales auditados.
assert ingresos['ingreso_laboral_monto'].notna().equals(ingresos['ingreso_monto_observado'].astype(bool))  # Comprueba relación entre monto y estado.
assert ingresos.loc[ingresos['ingrl'].isin(['-1', '999999']), 'ingreso_laboral_monto'].isna().all()  # Impide tratar códigos como cantidades.
assert ingresos.loc[ingresos['ingrl'].eq('0'), 'ingreso_laboral_monto'].eq(0).all()  # Comprueba que los ceros declarados se preservaron.
assert ingresos.loc[ingresos['ingrl'].isna(), 'ingreso_laboral_monto'].isna().all()  # Comprueba que no se imputaron vacíos.

# BLOQUE 5: comprobar partición fija y pliegues en las unidades observadas.
asignacion = pd.read_csv(DATOS / 'asignacion_upm.csv', dtype={'upm': str, 'estrato': str, 'particion_ml': str, 'pliegue_cv': 'Int8'})  # Recupera el mapa por UPM.
assert asignacion['upm'].is_unique and len(asignacion) == 7780  # Verifica una sola asignación por UPM de la muestra completa.
assert hashlib.sha256((DATOS / 'asignacion_upm.csv').read_bytes()).hexdigest() == resumen['asignacion_upm_sha256']  # Comprueba congelación del mapa.
for estrato, grupo in asignacion.groupby('estrato'):  # Recalcula el criterio de reserva a partir de semilla y UPM, sin consultar y.
    orden = grupo['upm'].sort_values(key=lambda s: s.map(lambda u: hashlib.sha256(f"{reglas['semilla']}|prueba|{u}".encode()).hexdigest()))  # Obtiene un orden independiente del orden de las filas.
    cantidad = max(1, min(len(grupo)-1, int(len(grupo)*reglas['fraccion_upm_prueba']+0.5)))  # Reproduce el redondeo especificado.
    assert set(orden.iloc[:cantidad]) == set(grupo.loc[grupo['particion_ml'].eq('prueba'), 'upm'])  # Comprueba asignación exacta por estrato.
columnas_clave = ['upm', 'id_vivienda_sin_mes', 'id_hogar_sin_mes', 'clave_posicion_sin_mes', 'particion_ml', 'pliegue_cv']  # Revisa grupos sobre toda la muestra, no solo dominio.
completa = lector.cargar_base('personas_tratada_completa.csv.gz', columnas_clave)  # Relee las claves finales de todas las observaciones.
for campo in columnas_clave[:4]:  # Repite las comprobaciones sobre archivos guardados.
    assert completa.groupby(campo)['particion_ml'].nunique().max() == 1  # Exige disyunción entre entrenamiento y prueba.
    assert completa.loc[completa['particion_ml'].eq('entrenamiento')].groupby(campo)['pliegue_cv'].nunique().max() == 1  # Exige disyunción entre pliegues de entrenamiento.
assert completa.loc[completa['particion_ml'].eq('prueba'), 'pliegue_cv'].isna().all()  # No mezcla prueba con validación interna.
X, y, contexto = lector.cargar_modelado()  # Prueba la interfaz destinada a las próximas etapas sobre entrenamiento.
assert X.columns.tolist() == reglas['predictores_numericos'] + reglas['predictores_categoricos']  # Exige la lista permitida exacta.
assert not set(X.columns) & set(reglas['prohibidos_como_predictores'])  # Comprueba exclusión de campos peligrosos.
assert X.notna().all().all() and y.notna().all()  # No entrega faltantes inesperados al siguiente paso.
diccionario = pd.read_csv(DATOS / 'diccionario_base_tratada.csv')  # Relee el diccionario final.
assert diccionario['variable'].is_unique and set(diccionario['variable']) == set(esquema['tipos'])  # Exige una definición por cada columna, sin omisiones.
for programa in sorted((RAIZ / 'src').glob('02*.py')):  # Comprueba todos los programas de esta etapa.
    ast.parse(programa.read_text(encoding='utf-8'))  # Detecta sintaxis inválida sin ejecutar sus acciones.

# BLOQUE 6: acta de verificación y diagnóstico de cobertura sin volver a seleccionar grupos.
estratos_train = set(dominio.loc[dominio['particion_ml'].eq('entrenamiento'), 'estrato'])  # Obtiene cobertura del dominio en desarrollo.
estratos_test = set(dominio.loc[dominio['particion_ml'].eq('prueba'), 'estrato'])  # Obtiene cobertura del dominio reservado, sin mirar resultados.
balance = pd.read_csv(REPORTES / '07_balance_covariables.csv', dtype={'codigo': str})  # Lee comparación de covariables ya prevista.
amplitud = balance.pivot(index=['variable', 'codigo'], columns='particion', values='proporcion_sin_peso').fillna(0)  # Alinea categorías incluso cuando alguna no aparece en uno de los conjuntos.
amplitud['diferencia_pp_prueba_menos_entrenamiento'] = 100*(amplitud['prueba']-amplitud['entrenamiento'])  # Expresa diferencias sin declarar equivalencia estadística.
amplitud.reset_index().to_csv(REPORTES / '09_diferencias_balance.csv', index=False, encoding='utf-8-sig')  # Publica un diagnóstico que no altera la semilla.
acta = {'estado': 'verificado', 'filas_originales_contrastadas': comparadas, 'columnas_originales_contrastadas': 139, 'productos': productos, 'columnas_diccionario': len(diccionario), 'solapamientos_entre_particiones': 0, 'solapamientos_entre_pliegues': 0, 'asignacion_reproducida_sin_y': True, 'estratos_dominio_sin_casos_en_prueba': sorted(estratos_train-estratos_test), 'mayor_diferencia_covariable_pp_absoluta': float(amplitud['diferencia_pp_prueba_menos_entrenamiento'].abs().max()), 'prueba_evaluada': False, 'advertencia': 'Balance de covariables revisado una vez; no se cambiaron semilla ni partición. No se evaluaron modelos ni métricas sobre prueba.'}  # Resume verificaciones y límite de cobertura.
(REPORTES / '10_verificacion_bases.json').write_text(json.dumps(acta, ensure_ascii=False, indent=2), encoding='utf-8')  # Guarda el acta final.
print(json.dumps(acta, ensure_ascii=False, indent=2), flush=True)  # Presenta solo comprobaciones, no resultados predictivos.
