from rest_framework.exceptions import APIException


class GenericMicroserviceError(APIException):

    def __init__(self, detail, status):
        self.status_code = status
        super(GenericMicroserviceError, self).__init__(detail)

    status_code = 500
    default_detail = 'Error inesperado'
    default_code = 'generic_microservice_error'


class SendEmailError(APIException):
    status_code = 500
    default_detail = 'Ocurrió un error al enviar el correo.'
    default_code = 'send_email_error'


class FileIsNotValidError(APIException):
    status_code = 400
    default_detail = 'No has ingresado un archivo valido'
    default_code = 'file_not_valid_error'
