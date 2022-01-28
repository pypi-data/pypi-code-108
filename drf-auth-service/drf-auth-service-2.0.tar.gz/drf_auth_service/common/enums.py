from django.db import models
from django.utils.translation import ugettext as _


class RegisterType(models.TextChoices):
    EMAIL = 'email', _('Email')
    PHONE_NUMBER = 'phone_number', _('Phone number')
    PHONE_NUMBER_CODE = 'phone_number_code', _('Phone number code')
    NICKNAME = 'nickname', _('Nickname')


class SocialTypes(models.TextChoices):
    Facebook = 'facebook', _('Facebook')
    Google = 'google-oauth2', _('Google')
    Apple = 'apple-id', _('Apple')


class LogsType(models.TextChoices):
    LOGIN_BY_CREDENTIALS = "login_by_credentials",
    REFRESH_TOKEN = "refresh_token",
    LOGOUT = "logout",
    REGISTER = "register",
    TOKEN_SENT = 'token_sent',
    TOKEN_CONFIRMED = 'token_confirmed',
