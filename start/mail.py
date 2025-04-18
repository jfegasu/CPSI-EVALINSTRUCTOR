from dbs.dbs import call_db
from flask_mail import Mail, Message
from start.email_templates import coordination_email_template


def send_instructor_email():
    """Send emails to instructors"""
    instructores = call_db("SELECT * FROM Instructores")
    eval_fechas = call_db("SELECT * FROM EvalFechas")[0]
    
    dates = {
        'endCoordination': eval_fechas[1],
        'endInstPhoto': eval_fechas[2],
        'endEvaluation': eval_fechas[3]
    }
    
    for instructor in instructores:
        mail_data = {
            'endCoordination': dates['endCoordination'],
            'endInstPhoto': dates['endInstPhoto'],
            'endEvaluation': dates['endEvaluation'],
            'NOMBRE': instructor[3],
            'APELLIDOS': instructor[4],
            'CORREO_INSTRUCTOR': instructor[7],
            'HASH': instructor[9],
            'REGIONAL': instructor[12],
            'CENTRO': instructor[13],
            'subject': "Activación del aplicativo para evaluar a los Instructores"
        }
        
        message = instructor_email_template(mail_data)
        
        msg = Message(
            subject=mail_data['subject'],
            recipients=[mail_data['CORREO_INSTRUCTOR']],
            body=message
        )
        
        mail.send(msg)
    

