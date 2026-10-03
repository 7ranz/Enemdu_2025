# ETAPA 3 DEL EDA: leer los CSV tratados conservando códigos, ceros iniciales y tipos.
# ARCHIVO: 02a_leer_bases.py. Evita que la lectura automática convierta identificadores en números.
# BLOQUE 1: rutas y esquema de los archivos preparados.
import json  # Lee el esquema de tipos y columnas.
from pathlib import Path  # Construye rutas portables.
import pandas as pd  # Carga las tablas con tipos explícitos.

RAIZ = Path(__file__).resolve().parents[1]  # Localiza el proyecto.
DATOS = RAIZ / 'data/processed'  # Ubica los archivos tratados.

def cargar_base(nombre, columnas=None):  # Lee un producto conocido, completo o con columnas seleccionadas.
    esquema = json.loads((DATOS / 'esquema_lectura.json').read_text(encoding='utf-8'))  # Recupera el contrato de lectura.
    if nombre not in esquema['archivos']:  # No adivina el formato de archivos ajenos al conjunto preparado.
        raise ValueError(f'Archivo fuera del esquema: {nombre}')  # Explica el nombre no reconocido.
    seleccion = esquema['archivos'][nombre] if columnas is None else columnas  # Elige las columnas solicitadas.
    if not set(seleccion).issubset(esquema['archivos'][nombre]):  # Comprueba que todas existan en ese producto.
        raise ValueError('Se solicitaron columnas que no están en este archivo.')  # Evita una selección silenciosamente incompleta.
    tipos = {campo: esquema['tipos'][campo] for campo in seleccion}  # Obtiene el tipo de cada campo.
    tabla = pd.read_csv(DATOS / nombre, encoding='utf-8-sig', sep=',', decimal='.', dtype=tipos, usecols=seleccion, keep_default_na=False, na_values=[''])  # Respeta vacíos, categorías, identificadores y enteros anulables.
    return tabla.loc[:, seleccion]  # Devuelve las columnas en el orden explícito solicitado.

def cargar_modelado(particion='entrenamiento'):  # Separa predictores, etiqueta y contexto, sin entrenar ningún modelo.
    if particion not in {'entrenamiento', 'prueba'}:  # Admite únicamente las dos particiones definidas.
        raise ValueError('La partición debe ser entrenamiento o prueba.')  # Explica cómo corregir el argumento.
    nombre = 'modelado/entrenamiento.csv' if particion == 'entrenamiento' else 'modelado/prueba_reservada.csv'  # Selecciona el archivo correspondiente.
    tabla = cargar_base(nombre)  # Recupera los datos con sus tipos.
    esquema = json.loads((DATOS / 'esquema_lectura.json').read_text(encoding='utf-8'))  # Recupera la lista permitida.
    X = tabla[esquema['predictores']].copy()  # Selecciona solo las diez características preespecificadas.
    y = tabla['y_adecuado'].copy()  # Mantiene la etiqueta separada de X.
    metadatos = tabla[[campo for campo in esquema['columnas_contexto_no_predictoras'] if campo != 'y_adecuado']].copy()  # Mantiene pesos, grupos y pliegues fuera de X.
    return X, y, metadatos  # Devuelve tres objetos con finalidades diferentes.
