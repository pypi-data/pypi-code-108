import builtins
from distutils.util import strtobool

from drf_auth_service.common.backends import BaseBackend
from drf_auth_service.common.enums import LogsType
from drf_auth_service.common.helpers import generate_code
from drf_auth_service.common.managers import EmailManager, PhoneManager
from drf_auth_service.models import Config, UserLogs
from drf_auth_service.settings import settings, User


class EmailBackend(BaseBackend):
    name = 'email'
    manager = EmailManager


class PhoneBackend(BaseBackend):
    name = 'phone_number'
    manager = PhoneManager


class PhoneCodeBackend(BaseBackend):
    name = 'phone_number_code'
    manager = PhoneManager

    def register(self):
        user, code = self.register_user()
        backend = self.manager(self.configs)
        backend.send(to_phone=user.username, message=f"Registration code: {code}")

        return dict(success=True, message="Register code was successfully sent")

    def register_user(self):
        user = User(username=self.request.data['username'], service=self.request.service,
                    register_type=self.request.data['register_type'])
        code = generate_code()
        user.set_password(str(code))
        user.save()
        UserLogs.objects.create(service=self.request.service, user=user,
                                username=user.username, type_log=LogsType.REGISTER)
        return user, code


class NicknameBackend(BaseBackend):
    name = 'nickname'

    def register(self):
        return self.get_jwt_response(self.register_user())

    def send_confirmation(self, user):
        raise NotImplementedError()


class RegisterManager:
    register_backend = None
    request = None
    configs = {}

    def __init__(self, register_type, request):
        self.request = request
        self.init_configs()
        self.set_backend(register_type)

    def register(self):
        return self.register_backend.register()

    def init_configs(self):
        for conf in Config.objects.filter(service=self.request.service):
            try:
                if conf.type == 'bool':
                    self.configs[conf.key] = strtobool(conf.value)
                else:
                    self.configs[conf.key] = getattr(builtins, conf.type)(conf.value)
            except AttributeError:
                self.configs[conf.key] = conf.value

    def set_backend(self, backend_name):
        for register_backend in settings.BACKENDS.REGISTER_BACKENDS:
            if getattr(register_backend, 'name') == backend_name:
                self.register_backend = register_backend(self.request, self.configs)
