import os
import hashlib
import pandas as pd
from flask import flash, redirect
from datetime import datetime
from dbs.dbs import save_db
from utils import crear_aprendiz_folder, clean_data_aprendiz

timing = datetime.today().date()
allApren = []


def joinAprenticeFiles(filepath):
    try:
        # Process each file in Excel
        dataframe = pd.read_excel(filepath)
        
        # Extract and clean data
        dfaprendiz = dataframe.drop(dataframe.index[0:1])
        dfaprendiz.reset_index(drop=True, inplace=True)
        dfaprendiz.columns = dfaprendiz.iloc[0]
        dfaprendiz = clean_data_aprendiz(dfaprendiz)

        allApren.append(dfaprendiz)

    except Exception as e:
        flash(f'Error al procesar el archivo {filepath}: {str(e)}')

    return allApren


def aprendizapp(allApren):
    try:
        # Join all files in one dataframe
        dfaprendiz = pd.concat(allApren, axis=0, ignore_index=True)
        dfaprendiz.reset_index(drop=True, inplace=True)

        # Create hash
        for i, row in dfaprendiz.iterrows():
            # Extract the last 5 digits from hash for password 
            string = str(row['NUMERO_DOCUMENTO'])
            passcode = string[-5:]
            dfaprendiz.at[i, 'PASSWORD'] = hashlib.md5(passcode.encode()).hexdigest()

        # Create group and handle disabled users
        dfaprendiz['GRUPO'] = 'Aprendiz'
        dfaprendiz['NO_HABILITADO'] = "NA"
        
        disabled_states = ['RETIRO VOLUNTARIO', 'TRASLADADO', 'APLAZADO', 'CANCELADO']
        for state in disabled_states:
            mask = dfaprendiz.ESTADO == state
            dfaprendiz.loc[mask, 'NO_HABILITADO'] = dfaprendiz.loc[mask, 'EMAIL']
            dfaprendiz.loc[mask, 'PASSWORD'] = "NA"
            dfaprendiz.loc[mask, 'EMAIL'] = "NA"
        
        dfaprendiz['FECHA_DE_UPLOAD'] = datetime.today().strftime('%m/%d/%Y %H:%M:%S')
        dfaprendiz['FECHA_DEL_REPORTE'] = datetime.now()
        dfaprendiz.reset_index(drop=True, inplace=True)

        # Create directory if it doesn't exist
        endDir = crear_aprendiz_folder()

        # Save to database and CSV
        dfaprendiz.to_csv(os.path.join(endDir, f"aprendices_{timing}.csv"), index=False)

        # Save to database
        save_db(dfaprendiz, "Aprendices")

    except Exception as e:
        flash(f'Error al procesar los archivos: {str(e)}')
        return redirect('/')

