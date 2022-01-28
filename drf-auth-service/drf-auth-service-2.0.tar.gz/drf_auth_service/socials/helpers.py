from urllib.error import HTTPError

from rest_framework.exceptions import ValidationError
from social_core.exceptions import MissingBackend, AuthTokenError
from social_django.utils import load_backend


def get_user_data_from_provider(strategy, provider, access_token, device_type):
    try:
        backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
    except MissingBackend:
        raise ValidationError({'provider': 'Please provide a valid provider'})
    try:
        user_data = backend.user_data(access_token, device_type=device_type)
    except HTTPError as error:
        raise ValidationError({'social_token': str(error)})
    except AuthTokenError as error:
        raise ValidationError({'social_token': str(error)})

    return user_data
