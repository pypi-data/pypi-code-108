from datetime import timedelta

from django.conf import settings as django_settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from drf_auth_service.common.enums import RegisterType, SocialTypes, LogsType
from drf_auth_service.common.helpers import generate_token, generate_code
from drf_auth_service.common.models import BaseModel


class Service(models.Model):
    name = models.CharField(max_length=30)
    secret_token = models.CharField(unique=True, max_length=200, default=generate_token)
    public_token = models.CharField(unique=True, max_length=200, default=generate_token)

    class Meta:
        db_table = '"services"'


class AbstractSSOUser(AbstractBaseUser):
    username = models.CharField(max_length=200, unique=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_users')
    register_type = models.CharField(max_length=100, choices=RegisterType.choices, default=RegisterType.EMAIL)
    USERNAME_FIELD = 'username'
    objects = UserManager()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = '"users"'
        unique_together = [['username', 'service']]
        abstract = True

    @property
    def is_confirmed(self):
        if self.activation_code.filter(key_type=ActivationCode.CodeTypes.CONFIRM_ACCOUNT).first() is None:  # noqa
            return True
        return False

    @property
    def is_blocked(self):
        try:
            if self.block:  # noqa
                return True
        except ObjectDoesNotExist:
            return False


class SSOUser(AbstractSSOUser):
    class Meta(AbstractSSOUser.Meta):
        swappable = 'AUTH_USER_MODEL'


class Scope(models.Model):
    description = models.TextField()
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=200)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        db_table = '"scopes"'


class Role(models.Model):
    scopes = models.ManyToManyField(Scope)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        db_table = '"roles"'


class UserBlock(BaseModel):
    ip = models.CharField(max_length=50, null=True)
    reason = models.CharField(max_length=254, null=True)
    user = models.OneToOneField(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='block')

    class Meta:
        db_table = '"user_blocks"'


class Social(BaseModel):
    label = models.CharField(max_length=100)
    identifier = models.CharField(max_length=100)
    social_type = models.CharField(max_length=20, choices=SocialTypes.choices)
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user_social_identifier')

    class Meta:
        unique_together = [['user', 'social_type']]
        db_table = '"socials"'


class Config(BaseModel):
    key = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    value = models.TextField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='configs')

    class Meta:
        db_table = '"configs"'
        unique_together = [['service', 'key']]


class ActivationCode(models.Model):
    class CodeTypes(models.TextChoices):
        RESET_PASSWORD = 'reset_password', _('Reset password')
        CONFIRM_ACCOUNT = 'confirm_account', _('Confirm account')

    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=64, db_index=True, unique=True)
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, related_name='activation_code', on_delete=models.CASCADE)
    key_type = models.CharField(max_length=30, choices=CodeTypes.choices, default=CodeTypes.RESET_PASSWORD)

    class Meta:
        db_table = '"activation_codes"'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_token()

        return super(ActivationCode, self).save(*args, **kwargs)

    @classmethod
    def clear_expired(cls, expiry_time, key_type=None):
        if key_type is None:
            cls.objects.filter(created_at__lte=expiry_time, key_type=cls.CodeTypes.RESET_PASSWORD).delete()

        elif key_type == cls.CodeTypes.CONFIRM_ACCOUNT:
            cls.objects.filter(created_at__lte=expiry_time, key_type=cls.CodeTypes.CONFIRM_ACCOUNT).delete()

    # TODO think about change
    @classmethod
    def make_user_active(cls, user):
        cls.objects.filter(user=user, key_type=cls.CodeTypes.CONFIRM_ACCOUNT).delete()

    @staticmethod
    def create_token(user, key_type, for_phone=False):
        from drf_auth_service.settings import settings
        if settings.DEBUG_MODE and user.register_type in [RegisterType.PHONE_NUMBER, RegisterType.PHONE_NUMBER_CODE]:
            token = ActivationCode(key=settings.DEBUG_KEY)
        else:
            password_reset_token_validation_time = 24
            now_minus_expiry_time = timezone.now() - timedelta(hours=password_reset_token_validation_time)
            ActivationCode.clear_expired(now_minus_expiry_time, key_type=key_type)
            key = generate_code() if for_phone else generate_token()
            token, _ = ActivationCode.objects.update_or_create(user=user, key_type=key_type, defaults={'key': key})
        return token


class UserLogs(models.Model):
    username = models.CharField(max_length=200)
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='logs')
    type_log = models.CharField(max_length=50, choices=LogsType.choices)
    service = models.ForeignKey(Service, related_name='service_logs', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"user_logs"'
