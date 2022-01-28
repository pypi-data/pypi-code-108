import phonenumbers
from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from drf_auth_service.common.enums import RegisterType, LogsType
from drf_auth_service.models import ActivationCode, UserLogs
from drf_auth_service.settings import User
from drf_auth_service.settings import settings
from drf_auth_service.validators import validate_token_by_type


class RegisterSerializer(serializers.Serializer):  # noqa
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    register_type = serializers.ChoiceField(choices=settings.ENUMS.REGISTER_TYPES.choices, required=True)

    def validate(self, attrs):
        error_message = ValidationError({"username": f"Value '{attrs['username']}' is invalid phone number"})

        if User.objects.filter(username=attrs['username'], service=self.context['request'].service).exists():
            raise ValidationError({'username': f"User '{attrs['username']}' already exists"})

        if attrs['register_type'] == RegisterType.EMAIL:
            email_validator = EmailValidator({"username": f"Value '{attrs['username']}' is invalid email address"})
            email_validator(attrs['username'])

        elif attrs['register_type'] == RegisterType.PHONE_NUMBER or \
                attrs['register_type'] == RegisterType.PHONE_NUMBER_CODE:

            try:
                phone = phonenumbers.parse(f"+{attrs['username']}", None)
            except:
                raise error_message

            if not phonenumbers.is_valid_number(phone):
                raise error_message
        return attrs


class ReturnAccessTokenSerializer(serializers.Serializer):  # noqa
    access_token = serializers.CharField(label='Jwt token for authentication')


class ReturnJWTTokensSerializer(ReturnAccessTokenSerializer):  # noqa
    refresh_token = serializers.CharField(label='Refresh token for access token')


class ReturnRegisterSerializer(ReturnAccessTokenSerializer):  # noqa
    refresh_token = serializers.CharField(label='Jwt token for refresh access token')


class ReturnSuccessSerializer(serializers.Serializer):  # noqa
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(label='Here will be displayed message of success or fail')


class SendResetPasswordSerializer(serializers.Serializer):  # noqa
    username = serializers.CharField(required=True)

    def validate(self, attrs):
        attrs['user'] = User.objects.filter(username=attrs['username']).first()
        if attrs['user'] is None:
            raise ValidationError({'username': 'Invalid username'})

        return attrs


class ResetPasswordVerifySerializer(serializers.Serializer):  # noqa
    token = serializers.CharField(label="Reset password token from url", required=True, allow_null=False,
                                  allow_blank=False)

    def validate(self, data):
        """
        Check if passwords matched and if token is valid.
        """
        data['token'] = validate_token_by_type(data['token'], ActivationCode.CodeTypes.RESET_PASSWORD)
        return data


class ResetPasswordConfirmSerializer(ResetPasswordVerifySerializer):  # noqa
    password = serializers.CharField(label="Password", required=True, allow_null=False, allow_blank=False)
    confirm_password = serializers.CharField(label="Confirm password", required=True,
                                             allow_null=False, allow_blank=False)

    def validate(self, data):
        data = super().validate(data)
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords does not match")
        return data


class LoginSerializer(TokenObtainPairSerializer):  # noqa
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['user_id'] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if getattr(self.context['request'], 'service', None):
            UserLogs.objects.create(service=self.context['request'].service, user=self.user,
                                    username=self.user.username, type_log=LogsType.LOGIN_BY_CREDENTIALS)
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):  # noqa
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        user = User.objects.filter(
            pk=refresh.payload.get("user_id"),
            service=self.context['request'].service
        ).first()

        refresh['username'] = user.username

        if not user:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        if user.is_blocked:
            raise AuthenticationFailed('User is blocked', code='user_blocked')

        if not user.is_confirmed:
            raise AuthenticationFailed('User is not confirmed', code='user_not_confirmed')

        UserLogs.objects.create(
            service=self.context['request'].service,
            user=user,
            username=user,
            type_log=LogsType.LOGIN_BY_CREDENTIALS
        )

        data = {'access': str(refresh.access_token)}

        return data


class TokenByCookieSerializer(TokenRefreshSerializer):
    service_token = serializers.CharField(required=False)

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        user = User.objects.filter(pk=refresh.payload.get("user_id")).first()
        if not user:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        UserLogs.objects.create(
            service=user.service,
            user=user,
            username=user,
            type_log=LogsType.REFRESH_TOKEN
        )

        return super().validate(attrs)
