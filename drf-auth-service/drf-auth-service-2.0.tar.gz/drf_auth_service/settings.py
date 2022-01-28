from datetime import timedelta

from django.apps import apps
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

from drf_auth_service.common.constants import SENDINBLUE_BACKEND_NAME, MAILCHIMP_BACKEND_NAME, TWILIO_BACKEND_NAME
from drf_auth_service.common.enums import RegisterType

auth_user = getattr(django_settings, 'AUTH_USER_MODEL', None) or 'drf_auth_service.SSOUser'
auth_module, user_model = auth_user.rsplit(".", 1)

User = apps.get_model(auth_module, user_model)
SSO_SETTINGS_NAMESPACE = "DRF_AUTH_SERVICE"

EMAIL_HOST = getattr(django_settings, 'EMAIL_HOST')
EMAIL_PORT = getattr(django_settings, 'EMAIL_PORT')
EMAIL_USERNAME = getattr(django_settings, 'EMAIL_HOST_USER')
EMAIL_PASSWORD = getattr(django_settings, 'EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = getattr(django_settings, 'EMAIL_USE_TLS')


class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            value = self[item]
            if isinstance(value, str):
                value = import_string(value)
            elif isinstance(value, (list, tuple)):
                value = [import_string(val) if isinstance(val, str) else val for val in value]
            self[item] = value
        except KeyError:
            value = super(ObjDict, self).__getattribute__(item)

        return value

    def __set_name__(self, owner, name):
        self.__name__ = 'dict'


default_sso_settings = {
    "CONFIRM_USERNAME": "email",
    "WORK_MODE": "standalone",
    "DEBUG_MODE": False,
    "DEBUG_KEY": "1111",
    "COOKIE_KEY": "sso_key",
    "DOMAIN_ADDRESS": None,
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "SENDINBLUE_RESET_PASS_TEMPLATE": None,
    "SENDINBLUE_CONFIRMATION_TEMPLATE": None,
    "SENDINBLUE_API_KEY": None,
    "MAILCHIMP_RESET_PASS_TEMPLATE": None,
    "MAILCHIMP_CONFIRMATION_TEMPLATE": None,
    "MAILCHIMP_USERNAME": None,
    "MAILCHIMP_SECRET_KEY": None,
    "SEND_CONFIRMATION": True,
    "RESET_PASSWORD_EXPIRE": 24,
    "RESET_PASSWORD_URL": '',
    "SEND_CONFIRMATION_URL": 'https://example.com/confirm-email/',
    "TWILIO_ACCOUNT_SID": "AC6b3fc1744aa63d35235a4fb01241e71a",
    "TWILIO_AUTH_TOKEN": "a3e0f68829427c69dbb94cb4e95ff638",
    "TWILIO_FROM_NUMBER": None,
    "SMS_CONFIRMATION_MESSAGE": "Confirmation code {{ code }}",
    "SMS_RESET_PASSWORD_MESSAGE": "Reset password code {{ code }}",
    "REGISTER_TYPES": list(dict(RegisterType.choices).keys()),
    "EMAIL_HOST": EMAIL_HOST,
    "EMAIL_PORT": EMAIL_PORT,
    "EMAIL_USERNAME": EMAIL_USERNAME,
    "EMAIL_PASSWORD": EMAIL_PASSWORD,
    "EMAIL_USE_TLS": EMAIL_USE_TLS,
    "HTML_RESET_PASSWORD_SUBJECT": "Reset password",
    "HTML_DEFAULT_FROM_EMAIL": EMAIL_USERNAME,
    "HTML_CONFIRMATION_SUBJECT": "Confirm account",
    "HTML_EMAIL_RESET_TEMPLATE": '',
    "HTML_EMAIL_CONFIRM_TEMPLATE": '',
    "SERIALIZERS": ObjDict({
        "USER_RETURN_SERIALIZER": "drf_auth_service.users.serializers.ReturnUserBaseSerializer",
        "USER_SERIALIZER": "drf_auth_service.users.serializers.UserBaseSerializer",
        "USER_IDENTIFIER": "drf_auth_service.users.serializers.UserIdentifierSerializer",
        "BLOCK_USER_SERIALIZER": "drf_auth_service.users.serializers.BlockUserSerializer",
        "USER_CONFIRM_SERIALIZER": "drf_auth_service.users.serializers.UserConfirmSerializer",
        "SOCIAL_RETURN_SERIALIZER": "drf_auth_service.socials.serializers.ReturnSocialSerializer",
        "SOCIAL_SERIALIZER": "drf_auth_service.socials.serializers.SocialSerializer",
        "SERVICE_SERIALIZER": "drf_auth_service.services.serializers.ServiceSerializer",
        "REGISTER_SERIALIZER": "drf_auth_service.authentication.serializers.RegisterSerializer",
        "REGISTER_RETURN_SERIALIZER": "drf_auth_service.authentication.serializers.ReturnRegisterSerializer",
        "SEND_RESET_PASSWORD_SERIALIZER": "drf_auth_service.authentication.serializers.SendResetPasswordSerializer",
        "RESET_PASSWORD_CONFIRMATION_SERIALIZER": "drf_auth_service.authentication.serializers.ResetPasswordConfirmSerializer",
        "RESET_PASSWORD_VERIFY_SERIALIZER": "drf_auth_service.authentication.serializers.ResetPasswordVerifySerializer",
        "RETURN_SUCCESS_SERIALIZER": "drf_auth_service.authentication.serializers.ReturnSuccessSerializer",
        "SET_PASSWORD_SERIALIZER": "drf_auth_service.users.serializers.UserSetPasswordSerializer",
        "LOGIN_SERIALIZER": "drf_auth_service.authentication.serializers.LoginSerializer",
    }),
    "VIEWS": ObjDict({
        "USER_VIEWS": "drf_auth_service.users.views.UserViewSet",
        "SERVICE_VIEWS": "drf_auth_service.services.views.ServiceViewSet",
        "AUTHENTICATION_VIEWS": "drf_auth_service.authentication.views.AuthenticationViewSet",
        "AUTHENTICATION_LOGIN_VIEWS": "drf_auth_service.authentication.views.LoginViewSet",
    }),
    "PERMISSIONS": ObjDict({
        "USER_PERMISSIONS": "drf_auth_service.users.permissions.USER_PERMISSIONS",
        "SERVICE_PERMISSIONS": "drf_auth_service.services.permissions.SERVICE_PERMISSIONS",
        "AUTHENTICATION_PERMISSIONS": "drf_auth_service.authentication.permissions.AUTHENTICATION_PERMISSIONS",
        "SERVICE_TOKEN_PERMISSION": "drf_auth_service.common.permissions.ServiceTokenPermission",
        "SECRET_SERVICE_TOKEN_PERMISSION": "drf_auth_service.common.permissions.SecretServiceTokenPermission",
    }),
    "BACKENDS": ObjDict({
        "SMS_BACKEND": "drf_auth_service.common.sms_backends.TwilioBackend",
        "EMAIL_BACKEND": "drf_auth_service.common.email_backends.HtmlTemplateBackend",
        "REGISTER_BACKENDS": [
            'drf_auth_service.common.register_backends.EmailBackend',
            'drf_auth_service.common.register_backends.PhoneBackend',
            'drf_auth_service.common.register_backends.PhoneCodeBackend',
            'drf_auth_service.common.register_backends.NicknameBackend',
        ]
    }),
    "ENUMS": ObjDict({
        "REGISTER_TYPES": "drf_auth_service.common.enums.RegisterType",
        "SOCIAL_TYPES": "drf_auth_service.common.enums.SocialTypes",
    })
}

MAILCHIMP_REQUIRED_CONFIGS = ["MAILCHIMP_SECRET_KEY", "MAILCHIMP_RESET_PASS_TEMPLATE",
                              "MAILCHIMP_CONFIRMATION_TEMPLATE"]

SENDINBLUE_REQUIRED_CONFIGS = ["SENDINBLUE_API_KEY", "SENDINBLUE_RESET_PASS_TEMPLATE",
                               "SENDINBLUE_CONFIRMATION_TEMPLATE"]

HTML_EMAIL_REQUIRED_CONFIGS = ["HTML_RESET_PASSWORD_SUBJECT", "HTML_CONFIRMATION_SUBJECT", "EMAIL_HOST", "EMAIL_PORT",
                               "EMAIL_USERNAME", "EMAIL_PASSWORD", "EMAIL_USE_TLS", "HTML_EMAIL_RESET_TEMPLATE",
                               "HTML_EMAIL_CONFIRM_TEMPLATE", "HTML_DEFAULT_FROM_EMAIL"]

TWILIO_REQUIRED_CONFIGS = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER"]

SETTINGS_TO_IMPORT_IN_DB = ["BACKENDS", "REGISTER_TYPES", "SEND_CONFIRMATION", "SMS_RESET_PASSWORD_MESSAGE",
                            "SMS_CONFIRMATION_MESSAGE", "DEBUG_MODE", "DEBUG_KEY", "CONFIRM_USERNAME"] \
                           + SENDINBLUE_REQUIRED_CONFIGS \
                           + MAILCHIMP_REQUIRED_CONFIGS + HTML_EMAIL_REQUIRED_CONFIGS + TWILIO_REQUIRED_CONFIGS

PHONE_NUMBER_BACKEND_CASE = []


class Settings:
    def __init__(self, default_sso_settings, explicit_overriden_settings: dict = None):  # noqa
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}  # noqa

        overriden_settings = (
                getattr(django_settings, SSO_SETTINGS_NAMESPACE, {}) or explicit_overriden_settings)  # noqa
        self._load_default_sso_settings()
        self._override_settings(overriden_settings)
        self._validate_configs()
        self._add_custom_schema_to_swagger()
        try:
            self._init_settings_to_db()
        except:  # noqa
            pass

    @staticmethod
    def _add_custom_schema_to_swagger():
        try:
            from drf_yasg import app_settings
            swagger_schema = getattr(getattr(django_settings, 'SWAGGER_SETTINGS', {}), 'DEFAULT_AUTO_SCHEMA_CLASS',
                                     None)
            if swagger_schema == app_settings.SWAGGER_DEFAULTS['DEFAULT_AUTO_SCHEMA_CLASS'] or swagger_schema is None:
                app_settings.SWAGGER_DEFAULTS[
                    'DEFAULT_AUTO_SCHEMA_CLASS'] = 'drf_auth_service.common.mixins.CustomAutoSchema'

            swagger_schema = getattr(getattr(django_settings, 'SWAGGER_SETTINGS', {}), 'SECURITY_DEFINITIONS',
                                     None)
            if swagger_schema == app_settings.SWAGGER_DEFAULTS['SECURITY_DEFINITIONS'] or swagger_schema is None:
                app_settings.SWAGGER_DEFAULTS['SECURITY_DEFINITIONS'] = {
                    'Bearer': {
                        'type': 'apiKey',
                        'name': 'Authorization',
                        'in': 'header'
                    },
                    'Service-Token': {
                        'type': 'apiKey',
                        'name': 'Service-Token',
                        'in': 'header'
                    },
                    'Secret-Token': {
                        'type': 'apiKey',
                        'name': 'Secret-Token',
                        'in': 'header'
                    }
                }
        except ModuleNotFoundError:
            pass

    def _load_default_sso_settings(self):
        for setting_name, setting_value in default_sso_settings.items():
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings: dict):
        for setting_name, setting_value in overriden_settings.items():
            value = setting_value
            if isinstance(setting_value, dict):
                value = getattr(self, setting_name, {})
                value.update(ObjDict(setting_value))
            setattr(self, setting_name, value)

    def _init_settings_to_db(self):
        from drf_auth_service.models import Service, Config

        if getattr(self, 'WORK_MODE') == 'standalone' and Service.objects.count() == 0:
            Service.objects.create(name='Default configs')

    def _validate_configs(self):

        if import_string(getattr(self, 'BACKENDS')['EMAIL_BACKEND']).name == SENDINBLUE_BACKEND_NAME:
            for required_conf in SENDINBLUE_REQUIRED_CONFIGS:
                if getattr(self, required_conf, '') == '':
                    raise ImproperlyConfigured(f"{required_conf} is required for {SENDINBLUE_BACKEND_NAME}")

        if import_string(getattr(self, 'BACKENDS')['EMAIL_BACKEND']).name == MAILCHIMP_BACKEND_NAME:
            for required_conf in MAILCHIMP_REQUIRED_CONFIGS:
                if getattr(self, required_conf, '') == '':
                    raise ImproperlyConfigured(f"{required_conf} is required for {MAILCHIMP_BACKEND_NAME}")

        if import_string(getattr(self, 'BACKENDS')['SMS_BACKEND']).name == TWILIO_BACKEND_NAME:
            for required_conf in TWILIO_REQUIRED_CONFIGS:
                if getattr(self, required_conf, '') == '':
                    raise ImproperlyConfigured(f"{required_conf} is required for {TWILIO_BACKEND_NAME}")


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_sso_settings, explicit_overriden_settings)


settings = LazySettings()


def reload_sso_settings(*args, **kwargs):
    global settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == SSO_SETTINGS_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)  # noqa


setting_changed.connect(reload_sso_settings)
