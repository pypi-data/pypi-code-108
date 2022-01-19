"""
    lager.auth

    Authentication helpers
"""
import os
import base64
import json
import time
import datetime
import urllib.parse
import requests
from ..config import read_config_file, write_config_file

_DEFAULT_CLIENT_ID = 'N2NcC4UplFLlxiIPzDDa5K1PKbTrRVec'
_DEFAULT_AUDIENCE = 'https://app.lagerdata.com/gateway'
_DEFAULT_AUTH_URL = 'https://auth.lagerdata.com'

_JWK_PATH = '.well-known/jwks.json'

_EXPIRY_GRACE = datetime.timedelta(hours=1).seconds

def get_auth_url():
    return os.getenv('LAGER_AUTH_URL', _DEFAULT_AUTH_URL)

def get_client_id():
    return os.getenv('LAGER_CLIENT_ID', _DEFAULT_CLIENT_ID)

def get_audience():
    return os.getenv('LAGER_AUDIENCE', _DEFAULT_AUDIENCE)

def _get_jwks(jwk_url):
    resp = requests.get(jwk_url)
    resp.raise_for_status()
    return resp.json()

def _is_expired(token):
    try:
        _header, encoded_payload, _sig = token.split('.')
        padding = '===='  # Auth0 token does not include padding
        payload = json.loads(base64.b64decode(encoded_payload + padding))
        return payload['exp'] < time.time() + _EXPIRY_GRACE
    except ValueError:
        return True

def _refresh(refresh_token):
    data = {
        'grant_type': 'refresh_token',
        'client_id': get_client_id(),
        'refresh_token': refresh_token,
    }
    token_url = urllib.parse.urljoin(get_auth_url(), '/oauth/token')
    resp = requests.post(token_url, data=data)
    resp.raise_for_status()
    return resp.json()

AUTH_TOKEN_KEY = 'LAGER_AUTH_TOKEN'
REFRESH_TOKEN_KEY = 'LAGER_REFRESH_TOKEN'
TOKEN_TYPE_KEY = 'LAGER_TOKEN_TYPE'
SECRET_TOKEN_KEY = 'LAGER_SECRET_TOKEN'
TOKEN_ID_KEY = 'LAGER_TOKEN_ID'
TOKEN_SECRET_KEY = 'LAGER_TOKEN_SECRET'

def _load_auth_from_environ(env):
    if TOKEN_ID_KEY in env and TOKEN_SECRET_KEY in env:
        token = base64.b64encode(f'{env[TOKEN_ID_KEY]}:{env[TOKEN_SECRET_KEY]}'.encode()).decode()
        return dict(
            token=token,
            type='token',
        )
    if SECRET_TOKEN_KEY in env:
        return dict(
            token=env[SECRET_TOKEN_KEY],
            type='secret',
        )

    if AUTH_TOKEN_KEY in env and TOKEN_TYPE_KEY in env and (
            env[TOKEN_TYPE_KEY].lower() == 'secret' or REFRESH_TOKEN_KEY in env):
        return dict(
            token=env[AUTH_TOKEN_KEY],
            refresh=env.get(REFRESH_TOKEN_KEY),
            type=env[TOKEN_TYPE_KEY],
        )
    return None

def load_auth():
    """
        Load auth token from environment if available, otherwise config
    """
    auth = None
    update_config = False
    auth = _load_auth_from_environ(os.environ)
    if not auth:
        config = read_config_file()
        if 'AUTH' not in config or 'token' not in config['AUTH']:
            return None
        update_config = True
        auth = config['AUTH']

    if auth['type'].lower() == 'bearer' and _is_expired(auth['token']):
        fresh_token = _refresh(auth['refresh'])
        auth['token'] = fresh_token['access_token']
        auth['type'] = fresh_token['token_type']
        if update_config:
            write_config_file(config)

    return auth
