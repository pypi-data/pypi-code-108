from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from drf_auth_service.models import ActivationCode
from drf_auth_service.settings import settings


def validate_token_by_type(token, code_type, **additional_params):
    if not settings.DEBUG_MODE or code_type == ActivationCode.CodeTypes.RESET_PASSWORD:
        password_reset_token_validation_time = 24

        try:
            token = get_object_or_404(ActivationCode, key=token, key_type=code_type, **additional_params)
        except:
            raise ValidationError(['Invalid Token'])

        expiry_date = token.created_at + timedelta(hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            token.delete()
            raise ValidationError(['Token expired'])
    else:
        if token != settings.DEBUG_KEY: # noqa
            raise ValidationError(['Invalid Token'])
    return token
