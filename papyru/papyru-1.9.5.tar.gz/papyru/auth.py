import re
from base64 import b64decode
from http import HTTPStatus
from inspect import signature

from .context import PlainContext

ANY_USER = 0x0


def require_basic_auth(user_map, realm='auth'):
    def wrapper(view):
        if user_map is None:
            return view

        get_request = _make_request_argument_binder(view)

        def impl(*args, **kwargs):
            request = get_request(*args, **kwargs)

            request.auth_user = _authenticate(
                user_map, parse_authorization_headers(request))

            if request.auth_user is None:
                auth_request = 'Basic realm="%s", charset="UTF-8"' % realm

                return (PlainContext(content_type=None)
                        .response(body='',
                                  status=HTTPStatus.UNAUTHORIZED,
                                  headers={'WWW-Authenticate': auth_request}))

            return view(*args, **kwargs)
        return impl
    return wrapper


def _make_request_argument_binder(func):
    sig = signature(func)

    def binder(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)

        if 'request' in bound.arguments:
            return bound.arguments['request']
        else:
            return args[0]
    return binder


def _authenticate(user_map, credentials):
    if credentials is None:
        return None

    username, password = credentials

    if user_map == ANY_USER:
        return username

    if username not in user_map:
        return None

    if user_map[username] != password:
        return None

    return username


def parse_authorization_headers(request):
    if 'Authorization' not in request.headers:
        return None

    m = re.match(r'^Basic (.+)$', request.headers['Authorization'])
    if not m:
        return None

    try:
        encoded_credentials = b64decode(m.group(1)).decode('utf-8')
    except Exception:
        return None

    credentials = encoded_credentials.split(':')

    if len(credentials) != 2:
        return None

    return credentials
