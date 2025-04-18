import os
import hashlib
import pandas as pd
from datetime import datetime, date, timedelta
from dbs.dbs import save_db
from utils import create_coordinator_folder, clean_data_coordinacion, clean_data_preguntas

timing = datetime.today().date()
dateEndCoordination = 15
dateEndPhoto = dateEndCoordination + 7
dateEndEvalua = dateEndCoordination + 7 + 15

def startapp(filepath):
    # Process the Excel file
    dataframe = pd.read_excel(filepath, 'Coordinaciones') 

    # Extract info from Coordinaciones
    dfcoord = dataframe.drop(dataframe.index[0:1])
    dfcoord.reset_index(drop=True, inplace=True)
    dfcoord.columns = dfcoord.iloc[0]
    dfcoord = dfcoord[1:8]
    dfcoord = clean_data_coordinacion(dfcoord)
    dfcoord = dfcoord.dropna()

    # Create assign group for Coordinaciones
    for i, row in dfcoord.iterrows():
        dfcoord.at[i, 'GRUPO'] = "Coordinador"
        centroFormacion = row['CENTRO_DE_FORMACION']
        dfcoord['FECHA_DE_UPLOAD'] = datetime.today().strftime('%m/%d/%Y %H:%M:%S')

        # Extract the last 5 digits to hash it for use as password 
        string = str(row['NUMERO_DOCUMENTO'])
        passcode = string[-5:]
        dfcoord.at[i, 'PASSWORD'] = hashlib.md5(passcode.encode()).hexdigest()

        # Create directory if it doesn't exist
        endDir = create_coordinator_folder()
        
        # Save to CSV files
        dfcoord.to_csv(os.path.join(endDir, f"Coordinacion_{centroFormacion}_{timing}.csv"), index=False)

    # Calculate dates
    startdateDf = dfcoord.at[1, 'FECHA_DE_COMIENZO']
    endCoordination = startdateDf + timedelta(days=dateEndCoordination)
    endInstPhoto = startdateDf + timedelta(days=dateEndPhoto)
    endEvaluation = startdateDf + timedelta(days=dateEndEvalua)
    
    times = {
        "STARTDATE": startdateDf,
        "ENDCOORDATE": endCoordination,
        "ENDPHOTODATE": endInstPhoto,
        "ENDEVALUACION": endEvaluation 
    }
    evalDates = pd.DataFrame([times])

    # Extract questions
    dfquestion = pd.read_excel(filepath, 'Preguntas')
    dfquestion = dfquestion.drop(dfquestion.index[0:1])
    dfquestion.reset_index(drop=True, inplace=True)
    dfquestion.columns = dfquestion.iloc[0]
    dfquestion = dfquestion[1:13]
    dfquestion = clean_data_preguntas(dfquestion)

    # Save to CSV files
    dfquestion.to_csv(os.path.join(endDir, f"Preguntas_{centroFormacion}_{timing}.csv"), index=False)
    
    # Save to database
    save_db(dfcoord, "Coordinadores")
    save_db(dfquestion, "Preguntas")
    save_db(evalDates, "EvalFechas")

    return times