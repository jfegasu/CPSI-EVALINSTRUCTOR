def coordination_email_template(mail_data):
    return f'''
    Señor(a) Coordinador(a) {mail_data['NOMBRES']} {mail_data['APELLIDOS']}
    Regional: {mail_data['REGIONAL']}, Centro Educativo: {mail_data['CENTRO']}, Coordinación: {mail_data['COORDINACION']}

    Con el presente le solicitamos atentamente subir a la plataforma los listados de Instructores y Aprendices de las áreas a evaluar.
    Le rogamos tener en cuenta que los listados son caso sensitivo y si se cambia algo en la configuración de estos, 
    puede resultar que se monten mal o no se monten, por esto le solicitamos no alterar nada y solo completar los campos requeridos.

    El ingreso a la plataforma es "www.datasena.evalinstructor.com".
    El nombre de usuario es el número de cédula y la clave de ingreso son los últimos 5 dígitos del documento de identidad.

    Las fechas de esta temporada de evaluación son las siguientes:
    >> Fechas para que las coordinaciones suban las listas de aprendices e instructores:
    Fecha de Inicio {mail_data['startdate']} - Fecha Limite {mail_data['endCoordination']}
    >> Fecha Limite para que los instructores suban su foto:
    Fecha de Inicio {mail_data['endCoordination']} - Fecha Limite {mail_data['endInstPhoto']}
    >> La evaluación por parte de los aprendices se realizara:
    Fecha de Inicio {mail_data['endInstPhoto']} - Fecha Limite {mail_data['endEvaluation']}

    Agradecemos la pronta gestión de los listados requeridos.
    
    Si tiene algunas dudas o sugerencias por favor comunicarse con la subdirección de su centro educativo

    Atentamente

    Centro De Producción De Soluciones Inteligentes
    Centro de Gestión de Mercados, Logística y Tecnologías de la Información.
    '''


def instructor_email_template(mail_data):
    return f'''
    Señor(a) Instructor(a) {mail_data['NOMBRE']} {mail_data['APELLIDOS']}
    Regional: {mail_data['REGIONAL']}, Centro Educativo: {mail_data['CENTRO']}

    La plataforma para que los aprendices den apreciaciones sobre su estilo de enseñanza ha sido activada y le solicitamos muy amablemente subir una foto de su rostro reciente y de frente con la finalidad que los aprendices no tengan dudas sobre su identidad.

    El ingreso a la plataforma es "www.datasena.evalinstructor.com".
    El nombre de usuario es el número de cédula y la clave de ingreso son los últimos 5 dígitos del documento de identidad.

    Las fechas de esta temporada de evaluación son las siguientes:
    >> Fecha Limite para que los instructores suban su foto:
    Fecha de Inicio {mail_data['endCoordination']} - Fecha Limite {mail_data['endInstPhoto']}
    >> La evaluación por parte de los aprendices se realizara:
    Fecha de Inicio {mail_data['endInstPhoto']} - Fecha Limite {mail_data['endEvaluation']}

    Agradecemos la pronta gestión al requerimiento.
    
    Si tiene algunas dudas o sugerencias por favor comunicarse con la coordinación de su centro educativo

    Atentamente

    Centro De Producción De Soluciones Inteligentes
    Centro de Gestión de Mercados, Logística y Tecnologías de la Información.
    '''

