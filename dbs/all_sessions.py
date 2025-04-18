from flask import flash, session


def create_coordinador_session(dbData):
    session['coordinador_grupo'] = dbData[9]
    session['coordinador_cedula'] = dbData[6]
    session['coordinador_loged'] = "Yes"
    return session


def create_instructor_session(dbData):
    session['instructor_grupo'] = dbData[10]
    session['instructor_name'] = dbData[3]
    session['instructor_lastname'] = dbData[4]
    session['instructor_cedula'] = dbData[6]
    session['instructor_loged'] = "Yes"
    return session


def create_aprendiz_session(dbData):
    session['aprendiz_grupo'] = dbData[12]
    session['ficha'] = dbData[9]
    session['aprendiz_name'] = dbData[3]
    session['aprendiz_lastname'] = dbData[4]
    session['aprendiz_cedula'] = dbData[6]
    session['aprendiz_loged'] = "Yes"
    return session

