import builtins

from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from drf_auth_service.common.email_backends import BaseEmailBackend
from drf_auth_service.common.enums import RegisterType
from drf_auth_service.common.sms_backends import BasePhoneBackend
from drf_auth_service.models import Config


class BaseManager:
    backend = None
    backend_type = None
    base_backend = None

    def __init__(self, configs, request=None):
        if configs is None and request:
            configs = self.get_configs(request)
        elif configs is None:
            raise Warning('Can not be both configs and request None')
        try:
            self.backend = import_string(configs[self.backend_type])(configs, request)
            if not isinstance(self.backend, self.base_backend):
                raise ImproperlyConfigured(
                    f"{configs[self.backend_type]} is not instance of BaseEmailBackend"
                )
        except ImportError:
            raise ImproperlyConfigured(
                'Invalid path for backend'
            )

    def send_confirmation(self, user):
        self.backend.send_confirmation(user)

    def send_reset_password(self, user):
        self.backend.send_reset_password(user)

    @staticmethod
    def get_configs(request):
        configs = {}
        for conf in Config.objects.filter(service=request.service):
            configs[conf.key] = getattr(builtins, conf.type)(conf.value) if not conf.type == 'NoneType' else None
        return configs

    @staticmethod
    def load_manager(user, configs, request=None):

        if RegisterType.EMAIL in user.register_type:
            return EmailManager(configs, request)
        else:
            return PhoneManager(configs, request)


class PhoneManager(BaseManager):
    backend = None
    backend_type = 'SMS_BACKEND'
    base_backend = BasePhoneBackend

    def send(self, to_phone, message, from_phone=None):
        self.backend.send(to_phone, message, from_phone)


class EmailManager(BaseManager):
    backend = None
    backend_type = 'EMAIL_BACKEND'
    base_backend = BaseEmailBackend

    def send(self, email_to, **context):
        self.backend.send(email=email_to, **context)
