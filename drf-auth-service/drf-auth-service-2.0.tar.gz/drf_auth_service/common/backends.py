from django.db import transaction
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from drf_auth_service.common.enums import LogsType
from drf_auth_service.models import UserLogs, Service
from drf_auth_service.settings import User
from drf_auth_service.settings import settings


class BaseBackend:
    configs = {}
    manager = None
    name = None

    def __init__(self, request, configs):
        self.request = request
        self.configs = configs

    def register(self):
        with transaction.atomic():
            user = self.register_user()
            if self.configs.get('SEND_CONFIRMATION'):
                return self.send_confirmation(user)

        return self.get_jwt_response(user)

    def register_user(self):
        user = User(
            register_type=self.name,
            service=self.request.service,
            username=self.request.data['username']
        )

        user.set_password(self.request.data['password'])
        user.save()

        UserLogs.objects.create(
            user=user,
            username=user.username,
            type_log=LogsType.REGISTER,
            service=self.request.service
        )
        return user

    def send_confirmation(self, user):
        backend = self.manager(self.configs)
        backend.send_confirmation(user)
        return settings.SERIALIZERS.RETURN_SUCCESS_SERIALIZER(dict(message="Confirmation was sent successfully")).data

    @staticmethod
    def get_jwt_response(user):
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['user_id'] = user.id

        return dict(refresh=str(refresh), access=str(refresh.access_token))


class SSOAuthentication(JWTAuthentication):
    request = None

    def authenticate(self, request):
        self.request = request
        return super(SSOAuthentication, self).authenticate(request)

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.get(**{
                api_settings.USER_ID_FIELD: user_id,
                'service': Service.objects.filter(public_token=settings.PERMISSIONS.SERVICE_TOKEN_PERMISSION.get_token(self.request)).first()
            })
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        if user.is_blocked:
            raise AuthenticationFailed('User is blocked', code='user_blocked')

        if not user.is_confirmed:
            raise AuthenticationFailed('User is not confirmed', code='user_not_confirmed')

        return user
