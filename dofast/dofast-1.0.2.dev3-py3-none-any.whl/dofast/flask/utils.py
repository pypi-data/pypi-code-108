import codefast as cf
from flask import request

from dofast.security._hmac import certify_token

from .config import AUTH_KEY
import authc


def make_response(code: int, msg: str):
    return {'code': code, 'message': msg}


# AUTH off for URL shortener
_ALLOWED_PATHS = ['/s', '/uploladed', '/hanlp']


def authenticate_flask(app):
    app._tokenset = set()
    accs = authc.authc()
    whitelist_token = accs['qflask_whitelist_token']

    @app.before_request
    def _():
        try:
            _path = request.path
            if any(map(lambda x: _path.startswith(x), _ALLOWED_PATHS)):
                return

            token = request.args.get('token', '')
            if token in app._tokenset:
                return make_response(
                    401, 'Authentication failed: token already used.')

            if certify_token(AUTH_KEY, token):
                if token != whitelist_token:
                    app._tokenset.add(token)
                cf.info('Authentication SUCCESS.')
                return

            cf.error('Authentication failed' + str(request.data) +
                     str(request.json) + str(request.args))
            return make_response(401, 'Authentication failed.')
        except BaseException as e:
            cf.error('Authentication failed', str(e))
            return make_response(401, 'Authentication failed.')
