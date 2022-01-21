import firebase_admin
from firebase_admin import db
from datetime import datetime
import pandas as pd
import json

def Monitoreo_Operativo(
    COD_AREA:str, COD_MODELO:str, TIPO_MODELO:str,
    METRICA_1:str, VALOR_METRICA_1:float, METRICA_2:str, VALOR_METRICA_2:float,
    FLG_DATA_DRIFT:int, FLG_RECALIBRACION:int, RESULTADO_PROCESO:int,
    TARGET:str, DESCRIPCION_TARGET:str
    ):
    """
    Funcion enfocada en crear un nuevo registro de monitoreo operativo para los modelos de Banco Davivienda.
    A continuacion se presentan los parametros necesarios para la correcta ejecucion del monitoreo.\n\n
    
    
    COD_AREA: Código del área a la que pertenece el modelo (ejm. DEPTO709698).\n 
    COD_MODELO: Código del modelo (ejm. DEPTO_706005_000).\n
    TIPO_MODELO: Tipo del modelo (ejm. REGRESION)\n
    METRICA_1: Nombre de la metrica objetivo 1 (ejm. ROC).\n
    VALOR_METRICA_1: Valor de la metrica objetivo 1 (ejm. 0.85)\n
    METRICA_2: Nombre de la metrica objetivo 2 (ejm. RMSE).\n
    VALOR_METRICA_2: Valor de la metrica objetivo 2 (ejm. 230.5)\n
    FLG_DATA_DRIFT: Flag que determina si se presento o no Data Drift en la actual prediccion. Acepta
    valores de 1 o 0.\n
    FLG_RECALIBRATION: Flag que determina si se recalibro el modelo en la actual prediccion. Acepta
    valores de 1 o 0.\n
    RESULTADO_PROCESO: Resultado de la actual prediccion. Acepta valores de 1 o 0.\n
    TARGET: Nombre de la variable objetivo del modelo.\n
    DESCRIPCION_TARGET: Describir la variable objetivo.
    """
    
    cred_object = firebase_admin.credentials.Certificate({
        "type": "service_account",
        "project_id": "monitoreo-gdm",
        "private_key_id": "6418c30962ac48ac61d32437802fb580ceaa2a02",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCx8vJcBdKwo+tH\n8HQI7s0r8QjztxNsykJPQf2ZzlXRYV9jJVLBWFv4hkatOSsBcWsOQPGGDsORHDtE\nj8dYOOhzVu5y2DK1OdBTLCyKRUWEbpxcYIBEBFnLCkMQTGhCzNc3k2etlkWBk8g1\n4RpHidZHWMCRq5UBvHB/BFCO6sDk99xzgSV1Y+XMgaOGefhrQKdCwrYNPeQJ1BE3\nGvJjyIEcU6dhyubsrvCjkzd1IOMK9/nVJzvHIYVh+ArTyxMBaqeK7C7L1R2gWaPt\nix1BLjSx5/pfLzT6KyzlrRcqGqk0Z2g6YZAiNn9soGAbjMd040JZ9ITvuhph8Ity\nNlnfKfixAgMBAAECggEAD7hME7gJ+EPKzaSew4lBA8A7z7fdFe+6MuE8A4HYT/Jf\nqFUMPftNyKMoDDZwJ6T61ZwEGhkkyqVpUPG4pQEF++Zykx+pPxw33Jka6C4daYkR\n9BEsU5Xkzsx9xytQzJHm80ho0MtlIYDKH4Reu3IgRVZAUL4NIEWi1H2vliiD2NYs\n2L5ws1JKAsNh3xKdG8dabZqhMn27AZoGx9xf34ccbEp4wajLRF6RBOYNbGkzXech\ndRSAdfn3H1ReNbLfwy7wbTLfMQ4bU/wzU8L1zvyuQjPbAxCyuNADw8vEzJK6LuVs\nEE9adyQMz7NGrS3z7EEw0mCNfA6D/xzJpOjFpU75pwKBgQDgBvhWA6Q62wIWvILT\n1ZsgVpTF6eNvjug+moDl07R6s+QxnHyz6H0GMgQSYFZsBahktkQ0ljiSSNmpFoSX\nqcQxRTVGrlZQTjsH9hxtr60n3ttsWy7PLbVMp1rtLKlIwIOCD5Hoil8zBs6FzFTG\n7BXVpDnOO3FZPxD7vb8M26iEhwKBgQDLWHgINWnqFZW4JYqfvIQRJl4k+SaFZqVS\nhGhcHYKYIfTivXoFxi/GseSl7xyWaTMLxTFFHopoPZlUAbiWiK3Xb2vDWefveaCH\nrBJ8/D8tMndl5C1rxINK7X0vFQKIduodDbgpqRuBvFQO3U65wRvofr/1qnIYjKyi\nC/R6wO4fBwKBgCMq9PELwUw79Sf8j80RSzjYXqJzBPEOTgcF2hY6FartcnUXS7wy\nUu4WC+2WkfqDKNwmgK6ApoDQTtrsXgQw8kuJwcNGuuYAYePuDqhpW5VWtrtb1Q1Q\n75UI8I0q5ag2EG7qYs1Oa4NnHiSC3wwbI5JWJXzqd/C6pb/fGY67LMkhAoGBAJNR\nrOSFjg5BRQ78Y8oGUcf6/AndV8Md8ngt5U2XM530O+5pR5YXV1WkW/q7mQJ/hLPq\nUR+6WJvcxNDPzmOA8jE6T+BfqmEcxOiGCX7zYPHltgrjnOSOonAOTrtlhUhInqQd\n5GaKVZtQTbXXL8nz1bxC19+rdK3EfO2Jq72jOODRAoGBAL/yymWiZt8jlWJ0K2J1\npLoggEVi5QmHEQWhgL8uvNG3b0L6LTxz5aedgcdHd8fFmdWZNU8aVLnE90zjojOL\n+3ofpe8jV9vYGjlf4CY7cIo0MfTvSMZcjP3AUvDuuvyJH0/pe32+FIKcIaBNkvV0\nkqrfMeL8/BKUkqfpKJ9GZD6c\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-jyyut@monitoreo-gdm.iam.gserviceaccount.com",
        "client_id": "113040927407929871362",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-jyyut%40monitoreo-gdm.iam.gserviceaccount.com"})
    
    databaseURL = "https://monitoreo-gdm-default-rtdb.firebaseio.com/"
    
    if not firebase_admin._apps:
        default_app = firebase_admin.initialize_app(cred_object, {
        'databaseURL':databaseURL
        })
    
    validaciones = [0, 1]
    cod_areas = __CodAreas__()
    cod_modelos = __CodModelos__()
    
    
    if COD_AREA not in cod_areas.keys():
        raise ValueError("El código del área no se encuentra registrado")
    
    if COD_MODELO not in cod_modelos.keys():
        raise ValueError("El código del modelo no se encuentra registrado")
    
    if FLG_DATA_DRIFT not in validaciones:
        raise ValueError("El valor de FLG_DATA_DRIFT no puede ser diferente a 0 y 1")
    
    if FLG_RECALIBRACION not in validaciones:
        raise ValueError("El valor de FLG_RECALIBRACION no puede ser diferente a 0 y 1")
    
    if RESULTADO_PROCESO not in validaciones:
        raise ValueError("El valor de RESULTADO_PROCESO no puede ser diferente a 0 y 1")
    
    dictionary = {
        'COD_AREA': {'valor': COD_AREA, 'tipo': str},
        'COD_MODELO': {'valor': COD_MODELO, 'tipo': str},
        'TIPO_MODELO': {'valor': TIPO_MODELO, 'tipo': str},
        'METRICA_1': {'valor': METRICA_1, 'tipo': str},
        'VALOR_METRICA_1': {'valor': VALOR_METRICA_1, 'tipo': float},
        'METRICA_2': {'valor': METRICA_2, 'tipo': str},
        'VALOR_METRICA_2': {'valor': VALOR_METRICA_2, 'tipo': float},
        'FLG_DATA_DRIFT': {'valor': FLG_DATA_DRIFT, 'tipo': int},
        'FLG_RECALIBRACION': {'valor': FLG_RECALIBRACION, 'tipo': int},
        'RESULTADO_PROCESO': {'valor': RESULTADO_PROCESO, 'tipo': int},
        'VARIABLE_OBJETIVO': {'valor': TARGET, 'tipo': str},
        'DESCRIPCION': {'valor': DESCRIPCION_TARGET, 'tipo': str}
    }
    __Validacion__(dictionary=dictionary)
    
    FECHA = datetime.today().strftime('%Y%m%d')
    HORA = datetime.today().strftime('%H%M%S')
    
    data = {
        'HORA': HORA,
        'TIPO_MODELO': TIPO_MODELO,
        'METRICA_1': METRICA_1,
        'VALOR_METRICA_1': VALOR_METRICA_1,
        'METRICA_2': METRICA_2,
        'VALOR_METRICA_2': VALOR_METRICA_2,
        'FLG_DATA_DRIFT': FLG_DATA_DRIFT,
        'FLG_RECALIBRACION': FLG_RECALIBRACION,
        'RESULTADO_PROCESO': RESULTADO_PROCESO,
        'VARIABLE_OBJETIVO': TARGET,
        'DESCRIPCION_OBJETIVO': DESCRIPCION_TARGET
    }

    ruta = '/monitoreo' + '/' + COD_AREA + '/' + COD_MODELO + '/' + FECHA + '/' + 'M_OPERATIVO' + '/' 
    ref = db.reference(ruta)
    ref.set( data )
    return



def Monitoreo_Variables(
    COD_AREA:str, COD_MODELO:str, VERSION_MODELO:str, DATAFRAME, V_FECHA:str, V_PREDICT:str, V_REAL:str,
    FECHAS:list
):
    """
    Funcion enfocada en crear un nuevo registro de monitoreo de variables para los modelos de Banco Davivienda.
    A continuacion se presentan los parametros necesarios para la correcta ejecucion del monitoreo.\n\n
    
    
    COD_AREA: Código del área a la que pertenece el modelo (ejm. DEPTO709698).\n 
    COD_MODELO: Código del modelo (ejm. DEPTO_706005_000).\n
    DATAFRAME: DataFrame que contiene toda la información tanto de variables como de fechas y estimaciones.\n
    V_FECHA: Nombre de la columna que contiene la fecha de y_real.\n
    V_PREDICT: Nombre de la columna que contiene las predicciones para el periodo analizado.\n
    V_REAL: Nombre de la columna que contiene las predicciones reales asociadas al vector V_FECHA.\n
    FECHAS: Lista que contiene los periodos para los cuales se realizará el registro de valores reales.
    Es decir, esta lista contiene el valor único del vector V_FECHA. El formato de los valores contenidos
    en la lista mencionada debe ser YYYYMMDD.
    """
    
    cred_object = firebase_admin.credentials.Certificate({
        "type": "service_account",
        "project_id": "monitoreo-gdm",
        "private_key_id": "6418c30962ac48ac61d32437802fb580ceaa2a02",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCx8vJcBdKwo+tH\n8HQI7s0r8QjztxNsykJPQf2ZzlXRYV9jJVLBWFv4hkatOSsBcWsOQPGGDsORHDtE\nj8dYOOhzVu5y2DK1OdBTLCyKRUWEbpxcYIBEBFnLCkMQTGhCzNc3k2etlkWBk8g1\n4RpHidZHWMCRq5UBvHB/BFCO6sDk99xzgSV1Y+XMgaOGefhrQKdCwrYNPeQJ1BE3\nGvJjyIEcU6dhyubsrvCjkzd1IOMK9/nVJzvHIYVh+ArTyxMBaqeK7C7L1R2gWaPt\nix1BLjSx5/pfLzT6KyzlrRcqGqk0Z2g6YZAiNn9soGAbjMd040JZ9ITvuhph8Ity\nNlnfKfixAgMBAAECggEAD7hME7gJ+EPKzaSew4lBA8A7z7fdFe+6MuE8A4HYT/Jf\nqFUMPftNyKMoDDZwJ6T61ZwEGhkkyqVpUPG4pQEF++Zykx+pPxw33Jka6C4daYkR\n9BEsU5Xkzsx9xytQzJHm80ho0MtlIYDKH4Reu3IgRVZAUL4NIEWi1H2vliiD2NYs\n2L5ws1JKAsNh3xKdG8dabZqhMn27AZoGx9xf34ccbEp4wajLRF6RBOYNbGkzXech\ndRSAdfn3H1ReNbLfwy7wbTLfMQ4bU/wzU8L1zvyuQjPbAxCyuNADw8vEzJK6LuVs\nEE9adyQMz7NGrS3z7EEw0mCNfA6D/xzJpOjFpU75pwKBgQDgBvhWA6Q62wIWvILT\n1ZsgVpTF6eNvjug+moDl07R6s+QxnHyz6H0GMgQSYFZsBahktkQ0ljiSSNmpFoSX\nqcQxRTVGrlZQTjsH9hxtr60n3ttsWy7PLbVMp1rtLKlIwIOCD5Hoil8zBs6FzFTG\n7BXVpDnOO3FZPxD7vb8M26iEhwKBgQDLWHgINWnqFZW4JYqfvIQRJl4k+SaFZqVS\nhGhcHYKYIfTivXoFxi/GseSl7xyWaTMLxTFFHopoPZlUAbiWiK3Xb2vDWefveaCH\nrBJ8/D8tMndl5C1rxINK7X0vFQKIduodDbgpqRuBvFQO3U65wRvofr/1qnIYjKyi\nC/R6wO4fBwKBgCMq9PELwUw79Sf8j80RSzjYXqJzBPEOTgcF2hY6FartcnUXS7wy\nUu4WC+2WkfqDKNwmgK6ApoDQTtrsXgQw8kuJwcNGuuYAYePuDqhpW5VWtrtb1Q1Q\n75UI8I0q5ag2EG7qYs1Oa4NnHiSC3wwbI5JWJXzqd/C6pb/fGY67LMkhAoGBAJNR\nrOSFjg5BRQ78Y8oGUcf6/AndV8Md8ngt5U2XM530O+5pR5YXV1WkW/q7mQJ/hLPq\nUR+6WJvcxNDPzmOA8jE6T+BfqmEcxOiGCX7zYPHltgrjnOSOonAOTrtlhUhInqQd\n5GaKVZtQTbXXL8nz1bxC19+rdK3EfO2Jq72jOODRAoGBAL/yymWiZt8jlWJ0K2J1\npLoggEVi5QmHEQWhgL8uvNG3b0L6LTxz5aedgcdHd8fFmdWZNU8aVLnE90zjojOL\n+3ofpe8jV9vYGjlf4CY7cIo0MfTvSMZcjP3AUvDuuvyJH0/pe32+FIKcIaBNkvV0\nkqrfMeL8/BKUkqfpKJ9GZD6c\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-jyyut@monitoreo-gdm.iam.gserviceaccount.com",
        "client_id": "113040927407929871362",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-jyyut%40monitoreo-gdm.iam.gserviceaccount.com"})
    
    databaseURL = "https://monitoreo-gdm-default-rtdb.firebaseio.com/"
    
    if not firebase_admin._apps:
        default_app = firebase_admin.initialize_app(cred_object, {
        'databaseURL':databaseURL
        })
    

    cod_areas = __CodAreas__()
    cod_modelos = __CodModelos__()
    
    if COD_AREA not in cod_areas.keys():
        raise ValueError("El código del área no se encuentra registrado")
    
    if COD_MODELO not in cod_modelos.keys():
        raise ValueError("El código del modelo no se encuentra registrado")
    
    dictionary = {
        'COD_AREA': {'valor': COD_AREA, 'tipo': str},
        'COD_MODELO': {'valor': COD_MODELO, 'tipo': str},
        'VERSION_MODELO': {'valor': VERSION_MODELO, 'tipo': str},
        'DATAFRAME': {'valor': DATAFRAME, 'tipo': pd.core.frame.DataFrame},
        'VFECHA': {'valor': V_FECHA, 'tipo': str},
        'VPREDICT': {'valor': V_PREDICT, 'tipo': str},
        'VREAL': {'valor': V_REAL, 'tipo': str},
        'FECHAS': {'valor': FECHAS, 'tipo': list},
        'CONTENIDO FECHAS': {'valor': FECHAS[0], 'tipo': int}
    }
    __Validacion__(dictionary=dictionary)
    
    FECHA = datetime.today().strftime('%Y%m%d')
    HORA = datetime.today().strftime('%H%M%S')



    json_variables = DATAFRAME.to_json()    
    data = {
        'HORA': HORA,
        'FECHA': json.dumps(FECHAS),
        'VARIABLES': json_variables,
        'Y_ESTIMADA': V_PREDICT,
        'Y_REAL': V_REAL,
        'VECTOR_FECHAS': V_FECHA,
        'VERSION_MODELO': VERSION_MODELO
    }

    ruta = '/monitoreo' + '/' + COD_AREA + '/' + COD_MODELO + '/' + FECHA + '/' + 'M_VARIABLES' + '/' 
    ref = db.reference(ruta)
    ref.set( data )
    return




def CodigosAreas():
    """
    Retorna el nombre y los codigos de las areas registradas en la base de datos.
    """
    cod_areas = __CodAreas__()
    for key, values in cod_areas.items():
        print(f"{values}: {key}")
    return


def __CodModelos__():
    cred_object = firebase_admin.credentials.Certificate({
        "type": "service_account",
        "project_id": "monitoreo-gdm",
        "private_key_id": "6418c30962ac48ac61d32437802fb580ceaa2a02",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCx8vJcBdKwo+tH\n8HQI7s0r8QjztxNsykJPQf2ZzlXRYV9jJVLBWFv4hkatOSsBcWsOQPGGDsORHDtE\nj8dYOOhzVu5y2DK1OdBTLCyKRUWEbpxcYIBEBFnLCkMQTGhCzNc3k2etlkWBk8g1\n4RpHidZHWMCRq5UBvHB/BFCO6sDk99xzgSV1Y+XMgaOGefhrQKdCwrYNPeQJ1BE3\nGvJjyIEcU6dhyubsrvCjkzd1IOMK9/nVJzvHIYVh+ArTyxMBaqeK7C7L1R2gWaPt\nix1BLjSx5/pfLzT6KyzlrRcqGqk0Z2g6YZAiNn9soGAbjMd040JZ9ITvuhph8Ity\nNlnfKfixAgMBAAECggEAD7hME7gJ+EPKzaSew4lBA8A7z7fdFe+6MuE8A4HYT/Jf\nqFUMPftNyKMoDDZwJ6T61ZwEGhkkyqVpUPG4pQEF++Zykx+pPxw33Jka6C4daYkR\n9BEsU5Xkzsx9xytQzJHm80ho0MtlIYDKH4Reu3IgRVZAUL4NIEWi1H2vliiD2NYs\n2L5ws1JKAsNh3xKdG8dabZqhMn27AZoGx9xf34ccbEp4wajLRF6RBOYNbGkzXech\ndRSAdfn3H1ReNbLfwy7wbTLfMQ4bU/wzU8L1zvyuQjPbAxCyuNADw8vEzJK6LuVs\nEE9adyQMz7NGrS3z7EEw0mCNfA6D/xzJpOjFpU75pwKBgQDgBvhWA6Q62wIWvILT\n1ZsgVpTF6eNvjug+moDl07R6s+QxnHyz6H0GMgQSYFZsBahktkQ0ljiSSNmpFoSX\nqcQxRTVGrlZQTjsH9hxtr60n3ttsWy7PLbVMp1rtLKlIwIOCD5Hoil8zBs6FzFTG\n7BXVpDnOO3FZPxD7vb8M26iEhwKBgQDLWHgINWnqFZW4JYqfvIQRJl4k+SaFZqVS\nhGhcHYKYIfTivXoFxi/GseSl7xyWaTMLxTFFHopoPZlUAbiWiK3Xb2vDWefveaCH\nrBJ8/D8tMndl5C1rxINK7X0vFQKIduodDbgpqRuBvFQO3U65wRvofr/1qnIYjKyi\nC/R6wO4fBwKBgCMq9PELwUw79Sf8j80RSzjYXqJzBPEOTgcF2hY6FartcnUXS7wy\nUu4WC+2WkfqDKNwmgK6ApoDQTtrsXgQw8kuJwcNGuuYAYePuDqhpW5VWtrtb1Q1Q\n75UI8I0q5ag2EG7qYs1Oa4NnHiSC3wwbI5JWJXzqd/C6pb/fGY67LMkhAoGBAJNR\nrOSFjg5BRQ78Y8oGUcf6/AndV8Md8ngt5U2XM530O+5pR5YXV1WkW/q7mQJ/hLPq\nUR+6WJvcxNDPzmOA8jE6T+BfqmEcxOiGCX7zYPHltgrjnOSOonAOTrtlhUhInqQd\n5GaKVZtQTbXXL8nz1bxC19+rdK3EfO2Jq72jOODRAoGBAL/yymWiZt8jlWJ0K2J1\npLoggEVi5QmHEQWhgL8uvNG3b0L6LTxz5aedgcdHd8fFmdWZNU8aVLnE90zjojOL\n+3ofpe8jV9vYGjlf4CY7cIo0MfTvSMZcjP3AUvDuuvyJH0/pe32+FIKcIaBNkvV0\nkqrfMeL8/BKUkqfpKJ9GZD6c\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-jyyut@monitoreo-gdm.iam.gserviceaccount.com",
        "client_id": "113040927407929871362",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-jyyut%40monitoreo-gdm.iam.gserviceaccount.com"})
    
    databaseURL = "https://monitoreo-gdm-default-rtdb.firebaseio.com/"
    
    if not firebase_admin._apps:
        default_app = firebase_admin.initialize_app(cred_object, {
        'databaseURL':databaseURL
        })
    
    modelos = db.reference('/cod_modelos').get()
    return modelos


def __CodAreas__():
    cred_object = firebase_admin.credentials.Certificate({
        "type": "service_account",
        "project_id": "monitoreo-gdm",
        "private_key_id": "6418c30962ac48ac61d32437802fb580ceaa2a02",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCx8vJcBdKwo+tH\n8HQI7s0r8QjztxNsykJPQf2ZzlXRYV9jJVLBWFv4hkatOSsBcWsOQPGGDsORHDtE\nj8dYOOhzVu5y2DK1OdBTLCyKRUWEbpxcYIBEBFnLCkMQTGhCzNc3k2etlkWBk8g1\n4RpHidZHWMCRq5UBvHB/BFCO6sDk99xzgSV1Y+XMgaOGefhrQKdCwrYNPeQJ1BE3\nGvJjyIEcU6dhyubsrvCjkzd1IOMK9/nVJzvHIYVh+ArTyxMBaqeK7C7L1R2gWaPt\nix1BLjSx5/pfLzT6KyzlrRcqGqk0Z2g6YZAiNn9soGAbjMd040JZ9ITvuhph8Ity\nNlnfKfixAgMBAAECggEAD7hME7gJ+EPKzaSew4lBA8A7z7fdFe+6MuE8A4HYT/Jf\nqFUMPftNyKMoDDZwJ6T61ZwEGhkkyqVpUPG4pQEF++Zykx+pPxw33Jka6C4daYkR\n9BEsU5Xkzsx9xytQzJHm80ho0MtlIYDKH4Reu3IgRVZAUL4NIEWi1H2vliiD2NYs\n2L5ws1JKAsNh3xKdG8dabZqhMn27AZoGx9xf34ccbEp4wajLRF6RBOYNbGkzXech\ndRSAdfn3H1ReNbLfwy7wbTLfMQ4bU/wzU8L1zvyuQjPbAxCyuNADw8vEzJK6LuVs\nEE9adyQMz7NGrS3z7EEw0mCNfA6D/xzJpOjFpU75pwKBgQDgBvhWA6Q62wIWvILT\n1ZsgVpTF6eNvjug+moDl07R6s+QxnHyz6H0GMgQSYFZsBahktkQ0ljiSSNmpFoSX\nqcQxRTVGrlZQTjsH9hxtr60n3ttsWy7PLbVMp1rtLKlIwIOCD5Hoil8zBs6FzFTG\n7BXVpDnOO3FZPxD7vb8M26iEhwKBgQDLWHgINWnqFZW4JYqfvIQRJl4k+SaFZqVS\nhGhcHYKYIfTivXoFxi/GseSl7xyWaTMLxTFFHopoPZlUAbiWiK3Xb2vDWefveaCH\nrBJ8/D8tMndl5C1rxINK7X0vFQKIduodDbgpqRuBvFQO3U65wRvofr/1qnIYjKyi\nC/R6wO4fBwKBgCMq9PELwUw79Sf8j80RSzjYXqJzBPEOTgcF2hY6FartcnUXS7wy\nUu4WC+2WkfqDKNwmgK6ApoDQTtrsXgQw8kuJwcNGuuYAYePuDqhpW5VWtrtb1Q1Q\n75UI8I0q5ag2EG7qYs1Oa4NnHiSC3wwbI5JWJXzqd/C6pb/fGY67LMkhAoGBAJNR\nrOSFjg5BRQ78Y8oGUcf6/AndV8Md8ngt5U2XM530O+5pR5YXV1WkW/q7mQJ/hLPq\nUR+6WJvcxNDPzmOA8jE6T+BfqmEcxOiGCX7zYPHltgrjnOSOonAOTrtlhUhInqQd\n5GaKVZtQTbXXL8nz1bxC19+rdK3EfO2Jq72jOODRAoGBAL/yymWiZt8jlWJ0K2J1\npLoggEVi5QmHEQWhgL8uvNG3b0L6LTxz5aedgcdHd8fFmdWZNU8aVLnE90zjojOL\n+3ofpe8jV9vYGjlf4CY7cIo0MfTvSMZcjP3AUvDuuvyJH0/pe32+FIKcIaBNkvV0\nkqrfMeL8/BKUkqfpKJ9GZD6c\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-jyyut@monitoreo-gdm.iam.gserviceaccount.com",
        "client_id": "113040927407929871362",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-jyyut%40monitoreo-gdm.iam.gserviceaccount.com"})
    
    databaseURL = "https://monitoreo-gdm-default-rtdb.firebaseio.com/"
    
    if not firebase_admin._apps:
        default_app = firebase_admin.initialize_app(cred_object, {
        'databaseURL':databaseURL
        })
    
    areas = db.reference('/cod_areas').get()
    return areas


def __Validacion__(dictionary:dict):
    for key in dictionary:
        valor = dictionary[key]['valor']
        tipo = dictionary[key]['tipo']
        if type(valor) != tipo:
            raise ValueError(f"Tipo inapropiado {key}. Valor {type(valor)} se esperada {tipo}")

