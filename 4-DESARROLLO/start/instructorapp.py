import os
import hashlib
import pandas as pd
from datetime import datetime
from dbs.dbs import save_db
from utils import crear_instructor_folder, clean_data_instructor

timing = datetime.today().date()


def instructorapp(filepath):
    # Process the Excel file
    dataframe = pd.read_excel(filepath)

    # Extract and clean data
    dfinstructor = dataframe.drop(dataframe.index[0:1])
    dfinstructor.reset_index(drop=True, inplace=True)
    dfinstructor.columns = dfinstructor.iloc[0]
    dfinstructor = clean_data_instructor(dfinstructor)

    # Create hash
    for i, row in dfinstructor.iterrows():
        dfinstructor.at[i, 'GRUPO'] = "Instructor"
        centroFormacion = row['CENTRO_DE_FORMACION']
        dfinstructor['FECHA_DE_UPLOAD'] = datetime.today().strftime('%m/%d/%Y %H:%M:%S')

        # Extract the last 5 digits from hash for password 
        string = str(row['NUMERO_DOCUMENTO'])
        passcode = string[-5:]
        dfinstructor.at[i, 'PASSWORD'] = hashlib.md5(passcode.encode()).hexdigest()

    # Add extra info
    dfinstructor['GRUPO'] = 'Instructor'
    dfinstructor['PHOTO'] = 'static/img/person.jpg'
    dfinstructor['FECHA_DEL_REPORTE'] = datetime.now()
    dfinstructor.reset_index(drop=True, inplace=True)

    # Create directory if it doesn't exist
    endDir = crear_instructor_folder()

    # Save to database and CSV
    dfinstructor.to_csv(os.path.join(endDir, f"instructores_{timing}.csv"), index=False)

    # Save to database
    save_db(dfinstructor, "Instructores")

