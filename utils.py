import os
import csv
import json
import numpy as np
import pandas as pd
from datetime import datetime, date
from flask import current_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOAD_PATH_COORD = (BASE_DIR + "/dbs/data/csvs/coordinaciones" )
LOAD_PATH_INSTRUCTOR = (BASE_DIR + "/dbs/data/csvs/instructores" )
LOAD_PATH_APRENTICE = (BASE_DIR + "/dbs/data/csvs/aprendices" )


def semestre():
    """Determine the current trimester and return a directory suffix"""
    now = datetime.now()
    year = now.strftime("%Y")
    month = int(now.strftime("%m"))

    if month < 3:
        return "_I_TRIM_" + year + "/"
    elif 3 <= month < 6:
        return "_II_TRIM_" + year + "/"
    elif 6 <= month < 9:
        return "_III_TRIM_" + year + "/"
    else:
        return "_IV_TRIM_" + year + "/"


def csv_files(end_dir):
    """Create dataframe with all CSV files in a directory"""
    csv_files = []
    for file in os.listdir(end_dir):
        if file.endswith('.csv'):
            csv_files.append(file)
    
    df_dict = {}
    for file in csv_files:
        try:
            df_dict[file] = pd.read_csv(os.path.join(end_dir, file))
        except UnicodeDecodeError:
            df_dict[file] = pd.read_csv(os.path.join(end_dir, file), encoding="ISO-8859-1")
    
    return csv_files, df_dict


def clean_tbl_name(filename):
    """Clean table name from filename"""
    clean_name = (
        filename.upper()
        .replace(" ", "_").replace("-", "_").replace("$", "").replace("?", "")
        .replace("%", "").replace("Á", "A").replace("É", "E").replace("Í", "I")
        .replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N").replace("á", "A")
        .replace("é", "E").replace("í", "I").replace("ó", "O").replace("ú", "U")
        .replace("ñ", "N").replace("@", "").replace("#", "").replace("/", "_")
        .replace("\\", "_").replace("(", "").replace(")", "")
    )
    return clean_name.split('.')[0]


def clean_columns(dataframe):
    """Clean column names in a dataframe"""
    dataframe.columns = [
        col.upper()
        .replace(" ", "_").replace("-", "_").replace("$", "").replace("?", "")
        .replace("%", "").replace(".", "").replace("Á", "A").replace("É", "E")
        .replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N")
        .replace("á", "A").replace("é", "E").replace("í", "I").replace("ó", "O")
        .replace("ú", "U").replace("ñ", "N").replace("@", "").replace("#", "")
        .replace("/", "").replace("\\", "").replace("(", "").replace(")", "")
        .replace("\n_anomesdia", "").replace("\nanomesdia", "")
        for col in dataframe.columns
    ]
    return dataframe


def create_coordinator_folder():
    # Create coordination directory path
    new_dir = semestre()
    end_dir = os.path.join(LOAD_PATH_COORD, new_dir)
    os.makedirs(end_dir, exist_ok=True)
    return end_dir


def clean_data_coordinacion(dataframe):
    """Clean coordination data"""
    dataframe = clean_columns(dataframe)
    for col in ['REGION', 'CENTRO_DE_FORMACION', 'COORDINACION', 
               'NOMBRES', 'APELLIDOS', 'TIPO_DOCUMENTO', 'NUMERO_DOCUMENTO', 'EMAIL']:
        dataframe[col] = dataframe[col].astype(str).ffill(axis=0)
    return dataframe


def crear_instructor_folder():
    """Create or get instructor directory path"""
    new_dir = semestre()
    end_dir = os.path.join(LOAD_PATH_INSTRUCTOR, new_dir)
    os.makedirs(end_dir, exist_ok=True)
    return end_dir


def clean_data_instructor(dataframe):
    """Clean instructor data"""
    dataframe = clean_columns(dataframe)
    for col in ['REGION', 'CENTRO_DE_FORMACION', 'COORDINACION', 
               'NOMBRES', 'APELLIDOS', 'TIPO_DOCUMENTO', 'NUMERO_DOCUMENTO', 
               'EMAIL', 'FICHAS', 'PROGRAMA_DE_FORMACION']:
        dataframe[col] = dataframe[col].astype(str).ffill(axis=0)
    return dataframe


def crear_aprendiz_folder():
    """Create or get apprentice directory path"""
    new_dir = semestre()
    end_dir = os.path.join(LOAD_PATH_APRENTICE, new_dir)
    os.makedirs(end_dir, exist_ok=True)
    return end_dir


def clean_data_aprendiz(dataframe):
    """Clean apprentice data"""
    dataframe = clean_columns(dataframe)
    
    # Process specific columns
    dataframe['FICHAS'] = dataframe['FICHAS'].astype(str).str.replace(".0", "")
    dataframe['NUMERO_DOCUMENTO'] = dataframe['NUMERO_DOCUMENTO'].astype(str)
    dataframe['ESTADO'] = dataframe['ESTADO'].fillna(value='ND')
    
    return dataframe


def create_report_folder():
    """Create or get reports directory path"""
    new_dir = semestre()
    end_dir = os.path.join(current_app.config['REPORTS_DESTINY_PATH'], new_dir)
    os.makedirs(end_dir, exist_ok=True)
    return end_dir


def clean_data_preguntas(dataframe):
    """Clean questions data"""
    dataframe = clean_columns(dataframe)
    for col in ['PREGUNTA_NUMERO', 'PREGUNTA']:
        dataframe[col] = dataframe[col].astype(str).ffill(axis=0)
    return dataframe


def clean_data(dataframe):
    """Clean general data"""
    dataframe = clean_columns(dataframe)
    
    # Process specific columns
    dataframe['FICHA'] = (
        dataframe['FICHA']
        .astype(str)
        .ffill(axis=0)
        .str.replace(".0", "")
    )
    dataframe['PROGRAMA_DE_FORMACION'] = (
        dataframe['PROGRAMA_DE_FORMACION']
        .ffill(axis=0)
        .str.replace(".", "")
    )
    dataframe['TIPO_DE_DOCUMENTO'] = dataframe['TIPO_DE_DOCUMENTO'].fillna('CC')
    dataframe['NUMERO_DE_DOCUMENTO'] = dataframe['NUMERO_DE_DOCUMENTO'].astype(str).ffill(axis=0)
    dataframe['NOMBRE'] = dataframe['NOMBRE'].ffill(axis=0)
    dataframe['APELLIDOS'] = dataframe['APELLIDOS'].ffill(axis=0)
    
    return dataframe
