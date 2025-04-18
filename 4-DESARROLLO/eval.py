import os
import json
import hashlib
import pandas as pd
import sqlite3 as sql3
from datetime import datetime, date, timedelta
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from dbs.dbs import *
from dbs.all_sessions import create_coordinador_session, create_instructor_session, create_aprendiz_session
from start.startapp import startapp
from start.instructorapp import instructorapp
from start.aprendizapp import joinAprenticeFiles, aprendizapp
from start.email_templates import coordination_email_template, instructor_email_template

with open("dbs/evalins.json") as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = config['SECRET_KEY']

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587, # 465 for MAIL_USE_SSL - 587 for MAIL_USE_TLS
    MAIL_USE_TLS=True,
    MAIL_USERNAME=config['EMAIL_USER'],
    MAIL_PASSWORD=config['EMAIL_PASSWORD'],
    MAIL_DEFAULT_SENDER=config['EMAIL_USER']
)
mail = Mail(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOAD_PATH = (BASE_DIR + "/dbs/data/activate" )
LOAD_PATH_APRENT = (BASE_DIR + "/dbs/data/activate/aprendices" )
LOAD_PATH_PHOTO = (BASE_DIR + "/static/img/photos" )
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


@app.route("/", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def home():
    # Check evaluation dates (should be moved to a separate function)
    try:
        sqlQuery = """SELECT ENDEVALUACION FROM EvalFechas"""
        firstDate = call_db(sqlQuery)
        start_date = datetime.strptime(firstDate[0][0], '%Y-%m-%d %H:%M:%S').date()
    except Exception as e:
        # If dates aren't set, redirect to activation
        session['grupo'] = "Administrador"
        flash('El aplicativo aún no está configurado', 'warning')
        return redirect(url_for('load_activation'))

    if request.method == "POST":
        # get data from home form
        email = request.form.get('email') # docid = .. ('docid') para usar la cc como nombre de usuario. (see template "home")
        password = request.form.get('password')
        
        passwordHash = hashlib.md5(password.encode()).hexdigest()
        
        # Check user types in sequence
        user_types = [
            ('Coordinadores', 'Coordinador'),
            ('Instructores', 'Instructor'),
            ('Aprendices', 'Aprendiz')
        ]
        
        for table, role in user_types:
            try:
                dbData = call_db_one(f"SELECT * FROM {table} WHERE EMAIL = ?", (email,)) # WHERE NUMERO_DOCUMENTO .. (docid) para usar la cc como nombre de usuario.
                if role == 'Coordinador':
                    PASSWORD = dbData[11]
                    GRUPO = dbData[9]
                    if PASSWORD == passwordHash and GRUPO == role:
                        create_coordinador_session(dbData)
                        return redirect(url_for('loadings'))
                elif role == 'Instructor':
                    PASSWORD = dbData[12]
                    GRUPO = dbData[10]
                    if PASSWORD == passwordHash and GRUPO == role:
                        create_instructor_session(dbData)
                        return redirect(url_for('upload_photo'))
                elif role == 'Aprendiz':
                    PASSWORD = dbData[11]
                    GRUPO = dbData[12]
                    if PASSWORD == passwordHash and GRUPO == role:
                        create_aprendiz_session(dbData)
                        return redirect(url_for('create_data_testing'))
                    else:
                        PASSWORD == "NA"
                        estado = dbData[8]
                        if estado == "EN FORMACION":
                            flash(f'El Aprendiz parece que ya calificó a todos sus instructores.', 'danger')
                            return redirect(url_for('home'))
                        else:
                            flash(f'El aprendiz no está habilitado para calificar instructores. Su estado es {estado}', 'danger')
                            return redirect(url_for('home'))
  
            except Exception as e:
                # Log the error for debugging
                app.logger.error(f"Error checking {table}: {str(e)}")
                continue
        
        # If no user found
        session.clear()
        flash('Credenciales incorrectas o usuario no encontrado', 'danger')
        return redirect(url_for('home'))

    # GET request
    return render_template("home.html", start_date=start_date)


@app.route('/about')
def about():

    return render_template("about.html")


def allowed_file(filename):

    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/load_activation')
def load_activation():
    try:
        if session['grupo'] == "Administrador":
            grupo = session['grupo']
            return render_template("loads/loadActivation.html", title="Subir Archivo de Activación", grupo=grupo)
    except:
        session.clear()
        flash("No tiene autorización para entrar")
        return redirect(url_for('home'))


@app.route('/activation', methods=['POST'])
def activation():
    if request.method == "POST":
        inFile = request.files['activationFileIn']
        if inFile and allowed_file(inFile.filename):
            filename = secure_filename(inFile.filename)
            filepath = os.path.join(LOAD_PATH, filename)
            inFile.save(filepath)

        # Process the Excel file
        times = startapp(filepath)

        # Send email to coordinations
        coordinaciones = call_db("SELECT * FROM Coordinadores")
        for coord in coordinaciones:
            mail_data = {
                'startdate': times['STARTDATE'],
                'endCoordination': times['ENDCOORDATE'],
                'endInstPhoto': times['ENDPHOTODATE'],
                'endEvaluation': times['ENDEVALUACION'],
                'REGIONAL': coord[0],
                'CENTRO': coord[1],
                'COORDINACION': coord[2],
                'NOMBRES': coord[3],
                'APELLIDOS': coord[4],
                'TIPO_DOCUMENTO': coord[5],
                'NUMERO_DOCUMENTO': coord[6],
                'EMAIL': coord[7],
                'HASH': coord[8],
                'PASSWORD': coord[10],
                'subject': "Activación del aplicativo para evaluar a los Instructores",
            }

            message = coordination_email_template(mail_data)
            msg = Message(
                subject=mail_data['subject'],
                sender=config['EMAIL_USER'],
                recipients=[mail_data['EMAIL']],
            )
            msg.body = message

            try:
                mail.send(msg)
            except Exception as e:
                flash(f'Error al procesar el archivo "LoadActivation": {str(e)}')
                return redirect(url_for('home'))

        flash('El aplicativo se activó exitosamente y los correos a las coordinaciones se enviaron', "info")
        return redirect(url_for('logout'))

    return redirect(url_for('home'))


@app.route("/logout") 
def logout():
    if session:
        session.clear()
        flash("Ha salido de la plataforma con exito.", "info")
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route('/loadings')
def loadings():
    try:
        if session['coordinador_grupo'] == "Coordinador":
            docid = session['coordinador_cedula']
            sqlQuery = "SELECT * FROM Coordinadores WHERE NUMERO_DOCUMENTO =?"
            adition = (docid,)
            coordinador = call_db_one(sqlQuery, adition)
            return render_template('loads/loadings.html', title='Subir Listas', coordinador=coordinador)
    except:
        session.clear()
        flash("No tiene autorización para entrar")
        return redirect(url_for('home'))


@app.route('/load_instructores', methods=['POST'])
def load_instructores():
    if request.method == "POST":
        inFile = request.files['instructorFileIn']

        if inFile and allowed_file(inFile.filename):
            filename = secure_filename(inFile.filename)
            filepath = os.path.join(LOAD_PATH, filename)
            inFile.save(filepath)

        # Process the Excel file
        instructorapp(filepath)

        flash('El registro de las listas de los instructores se realizó exitosamente.')
        return redirect(url_for('loadings'))

    return redirect('/')


@app.route('/load_aprendices_many', methods=['POST'])
def load_aprendices_many():
    if request.method == 'POST':
        files = request.files.getlist('aprendfileinn')

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(LOAD_PATH_APRENT, filename)
                file.save(filepath)
                allApren = joinAprenticeFiles(filepath)
        
        if not allApren:
            flash('No se encontraron listados o algo salió mal. Revise que los listados estén en la carpeta correcta.')
            return redirect(url_for('loadings'))

        aprendizapp(allApren)

        flash('El registro de las listas de los aprendices se realizó exitosamente.')
        return redirect(url_for('loadings'))

    return redirect('/')


@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    instructor = session
    if session and request.method == 'POST':
        file = request.files['PHOTO']
        numero_de_documento = session['instructor_cedula']
        
        if file.filename == '':
            flash('No selected file')
            return redirect('/')
            
        if file and numero_de_documento:
            try:
                # Get instructor
                sqlInstr = "SELECT * FROM Instructores WHERE NUMERO_DOCUMENTO = ?"
                instructor = call_db_one_dict(sqlInstr, (numero_de_documento,))
                lastName = instructor["APELLIDOS"]
                
                if not instructor:
                    flash('El Instructor no se encontró en los registros.')
                    return redirect('/')
                
                # Save file
                filename = secure_filename(f"{lastName}_{file.filename}")
                filepath = os.path.join(LOAD_PATH_PHOTO, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                
                # Update database
                sqlQuery = "UPDATE Instructores SET PHOTO = ? WHERE NUMERO_DOCUMENTO = ?"
                update_db(sqlQuery, (filename), (numero_de_documento))

                # Get fresh instructor
                sqlInstr = "SELECT * FROM Instructores WHERE NUMERO_DOCUMENTO = ?"
                instructor = call_db_one_dict(sqlInstr, (numero_de_documento,))

                # LogOut
                session.clear()

                flash('La foto se monto al sistema correctamente, Gracias por su pronta respuesta')
                return render_template('loads/instructor.html', instructor=instructor)
                
            except Exception as e:
                flash(f'Error al procesar la foto: {str(e)}')
                return redirect('/')
    
    return render_template('loads/uploadPhoto.html', title="Load Foto", instructor=instructor)


@app.route('/create_data_testing')
def create_data_testing():

    aprid = session['aprendiz_cedula']
    ficha = session['ficha']

    try:
        apSqlQuery = "SELECT * FROM ToTest WHERE DOCAPRENDIZ =?"
        listToTest = call_db_all_dict(apSqlQuery, (aprid,))

        if listToTest:
            return redirect(url_for('aprendiz'))
        else:
            instructores_to_test = []
            inSqlQuery = "SELECT * FROM Instructores WHERE FICHAS =?"
            adition = (ficha,)
            instructores = call_db_all_dict(inSqlQuery, adition)
            
            for instructor in instructores:
                data = {
                    "FICHA": ficha,
                    "PROGFORMACION": instructor['PROGRAMA_DE_FORMACION'],
                    "DOCAPRENDIZ": aprid,
                    "APRENDIZ_NAME": session['aprendiz_name'],
                    "APRENDIZ_LAST": session['aprendiz_lastname'],
                    "DOCINSTRUCTOR": instructor['NUMERO_DOCUMENTO'],
                    "INSTRUCTOR_NAME": instructor['NOMBRES'],
                    "INSTRUCTOR_LAST": instructor['APELLIDOS'], 
                }
                instructores_to_test.append(data)
            instructores_to_test = pd.DataFrame(instructores_to_test)
            save_response(instructores_to_test, 'ToTest')
            return redirect(url_for('aprendiz'))

    except Exception as e:
        flash(f'Algo salio mal, Intentelo de nuevo!": {str(e)}')
        return redirect(url_for('home'))
    

@app.route('/aprendiz')
def aprendiz():
    aprendiz = []
    instructoresTest = []

    if session['aprendiz_grupo'] == "Aprendiz":
        ficha = session['ficha']
        aprid = session['aprendiz_cedula']
        
        apSqlQuery = "SELECT * FROM ToTest WHERE DOCAPRENDIZ =?"
        listToTest = call_db_all_dict(apSqlQuery, (aprid,))

        if listToTest:
            inSqlQuery = "SELECT * FROM Instructores WHERE FICHAS =?"
            instructores = call_db_all_dict(inSqlQuery, (ficha,))

            for aprend in listToTest:
                aprendiz.append({'FICHA':aprend['FICHA'], 'PROGFORMACION':aprend['PROGFORMACION'], 'DOCAPRENDIZ':aprend['DOCAPRENDIZ'], 'APRENDIZ_NAME':aprend['APRENDIZ_NAME'], 'APRENDIZ_LAST':aprend['APRENDIZ_LAST']})
                break
            
            for instru in listToTest:
                for intructor in instructores:
                    if instru['DOCINSTRUCTOR'] == intructor['NUMERO_DOCUMENTO']:
                        instructoresTest.append(intructor)

            return render_template('evalua/aprendiz.html', title='Aprendiz', aprendiz=aprendiz, instructoresTest=instructoresTest)
        
        else:
            aprid = session['aprendiz_cedula']
            apSqlQuery = "SELECT * FROM Aprendices WHERE NUMERO_DOCUMENTO =?"
            aprendiz = call_db_one_dict(apSqlQuery, (aprid,))
            email = aprendiz['EMAIL']

            sqlQuery = "UPDATE Aprendices SET PASSWORD =? WHERE NUMERO_DOCUMENTO =?"
            update_db(sqlQuery, "NA", aprid)
            session.clear()

            flash(f"Ya evaluó a todos los instructores. Gracias por su colaboración.")
            return redirect(url_for('home'))


@app.route('/questionary/<pk>', methods=['GET', 'POST'])
def questionary(pk):
    data = pk
    aprendiz = []
    ficha = session['ficha']
    aprid = session['aprendiz_cedula']

    inSqlQuery = "SELECT * FROM ToTest WHERE DOCAPRENDIZ =? AND DOCINSTRUCTOR =?"
    testInstructor = call_db_two_all(inSqlQuery, aprid, pk)

    preguntas = call_db("SELECT * FROM Preguntas")

    return render_template('evalua/questions.html', title='Evaluacion', testInstructor=testInstructor, preguntas=preguntas)


@app.route('/save_answers', methods=['GET', 'POST'])
def save_answers():
    if request.method == "POST":
        # Get Aprentice data from session
        aprid = session['aprendiz_cedula']
        # Get Instructor data from session
        insid = request.form.get('instructor')

        # Call db ToTest to select Instructor in question for verification and data
        toTestQuery = "SELECT * FROM ToTest WHERE DOCAPRENDIZ =? AND DOCINSTRUCTOR =?"
        toTest = call_db_two_all_dict(toTestQuery, aprid, insid)

        # Get answers from form
        respuestas = request.form
        respuestas_data = {
            "FICHA": toTest['FICHA'],
            "DOCAPRENDIZ": aprid,
            "APRENDIZ_NAME": toTest['APRENDIZ_NAME'],
            "APRENDIZ_LAST": toTest['APRENDIZ_LAST'],
            "DOCINSTRUCTOR": insid,
            "INSTRUCTOR_NAME": toTest['INSTRUCTOR_NAME'],
            "INSTRUCTOR_LAST": toTest['INSTRUCTOR_LAST'],
            "P1": respuestas.get('1'),
            "P2": respuestas.get('2'),
            "P3": respuestas.get('3'),
            "P4": respuestas.get('4'),
            "P5": respuestas.get('5'),
            "P6": respuestas.get('6'),
            "P7": respuestas.get('7'),
            "P8": respuestas.get('8'),
            "P9": respuestas.get('9'),
            "P10": respuestas.get('10'),
            "P11": respuestas.get('11'),
            "P12": respuestas.get('12'),
        }

        # Convert to DataFrame and save to db
        evalInstr = pd.DataFrame([respuestas_data])
        print(evalInstr)
        save_response(evalInstr, "Informe")

        INSTRUCTOR_NAME = toTest['INSTRUCTOR_NAME']
        INSTRUCTOR_LAST = toTest['INSTRUCTOR_LAST']

        # Delete Instructor from ToTest db
        toTestQuery = "DELETE FROM ToTest WHERE DOCAPRENDIZ =? AND DOCINSTRUCTOR =?"
        toTest = delete_two_db(toTestQuery, aprid, insid)

        flash(f"El/La instructor(a) {INSTRUCTOR_NAME} {INSTRUCTOR_LAST} ya quedo evaluado(a), Gracias")
        return redirect('aprendiz')


if __name__ == "__main__":
    app.run(debug=True,port=5001)
