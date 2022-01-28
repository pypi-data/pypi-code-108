import binascii
import os
import random
from urllib.parse import urlparse


def generate_token(min_length=30, max_length=40):
    length = random.randint(min_length, max_length)

    return binascii.hexlify(
        os.urandom(max_length)
    ).decode()[0:length]


def generate_code(length=6):
    range_start = 10 ** (length - 1)
    range_end = (10 ** length) - 1
    return random.randint(range_start, range_end)


def set_cookies(response):
    from drf_auth_service.settings import settings

    response.set_cookie(
        settings.COOKIE_KEY,
        response.data['refresh'],
        max_age=settings.REFRESH_TOKEN_LIFETIME.total_seconds(),
        domain=urlparse(settings.DOMAIN_ADDRESS).netloc if settings.DOMAIN_ADDRESS else None,
        httponly=True,
        secure=True
    )
    response.cookies[settings.COOKIE_KEY]['samesite'] = 'None'

    return response
