from django.conf import settings
from drf_yasg.generators import OpenAPISchemaGenerator


class Enums:
    ACTIVO = 'Activo'
    INACTIVO = 'Inactivo'
    LIST_STATUS = [ACTIVO, INACTIVO]
    CREATE = 'Crear'
    UPDATE = 'Actualizar'
    DELETE = 'Eliminar'
    PENDING = 'Pendiente'
    AUTHORIZED = 'Autorizada'
    LIST_AUTHORIZE_ROLE = [PENDING, AUTHORIZED]
    COMMUNITY = 'Comunidad'
    STANDARD = 'Estándar'
    LIST_TYPE_INVITE_ROLE = [COMMUNITY, STANDARD]
    TYPE_CONTRACT = 'Tipo de contrato'
    DOCUMENT = 'Documento'
    LIST_TYPE_CATEGORIES = [COMMUNITY, TYPE_CONTRACT, DOCUMENT]
    CONTENT_IMAGE = 'image/png'
    CONTENT_VIDEO = 'video/mp4'
    CONTENT_FILE = 'application/pdf'
    TYPE_FILE = ['png', 'gif', 'jpg', 'jpeg', 'mp4', 'pdf']
    EMAIL = 'Correo'
    CHAT = 'Chat'
    SHARE_OPTIONS = [EMAIL, CHAT]
    CONFIRMED = 'CONFIRMADO'
    FORCE_CHANGE_PASSWORD = 'FORZAR_CAMBIO_CONTRASEÑA'
    LIST_ACCOUNT_CONFIRMATION = [CONFIRMED, FORCE_CHANGE_PASSWORD]
    GOOGLE_PROVIDER = 'Google'
    REGULAR_PROVIDER = 'Regular'
    LIST_PROVIDERS = [GOOGLE_PROVIDER, REGULAR_PROVIDER]


class Constants:
    FORMAT_DATE_TIME = '%d-%m-%Y %H:%M:%S'
    FORMAT_DATE_TIME_12 = '%d-%m-%Y %I:%M %p'
    FORMAT_DATE = '%d-%m-%Y'
    FORMAT_DATE_OLD = '%Y-%m-%d'
    FORMAT_TIME = '%H:%M:%S'
    FORMAT_TIME_24 = ('%H:%M:%S',)
    FORMAT_DATE_TIME_TIMEZONE = '%d-%m-%YT%H:%M:%S.%fZ'
    FORMAT_DATE_TIME_TIMEZONE_EN = '%Y-%m-%dT%H:%M:%S.%fZ'
    EXPIRED = 'EXPIRADO'
    INVALID = 'INVALIDO'
    REFRESH_TOKEN = 'REFRESH_TOKEN'
    ACCESS_TOKEN = 'ACCESS_TOKEN'
    PHOTO_DEFAULT = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
    FRONTEND_CONTEXT = 'joinus'
    WINDOWS = 'win'
    LINUX = 'linux'
    MACOS = 'mac'
    DEVELOP = 'dev'
    DEPLOY = 'dep'
    LOCAL = 'loc'


class FrontendUrl:
    URL_BASE_COMMUNITY = '/usuarios/comunidad/'


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):

    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        base_path = getattr(settings, 'CUSTOM_SWAGGER', {})
        schema.basePath = base_path['BASE_PATH']
        return schema
