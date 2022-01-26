import requests

from .authentication import getEmailPasswdAuthKey
from .config import Config

class FileDoesNotExist(Exception):
    pass


def handle_response(func):
    def wrapper(*args, **kwargs):
        resp = func(*args, **kwargs)
        if resp.status_code == 401 and Config.auth_retry < 1:
            getEmailPasswdAuthKey()
            Config.auth_retry = Config.auth_retry + 1
            resp = func(*args, **kwargs)
            
        if resp.status_code != 200:
            resp.raise_for_status()
        else:
            try:
                Config.auth_retry = 0
                jsn = resp.json()['data']
            except Exception as e:
                print('Could not json decode response : {0}!'.format(resp.text))
                raise
        return jsn

    return wrapper


@handle_response
def post2(method, data=None):
    queryUrl = f"{Config.WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360USER': Config.user['identityId'], "Application":"TIDY3D"}
    return requests.post(queryUrl, headers=headers, json=data)


@handle_response
def put2(method, data):
    queryUrl = f"{Config.WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360USER': Config.user['identityId'], "Application":"TIDY3D"}
    return requests.put(queryUrl, headers=headers, json=data)


@handle_response
def get2(method):
    queryUrl = f"{Config.WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360USER': Config.user['identityId'], "Application":"TIDY3D"}
    return requests.get(queryUrl, headers=headers)


@handle_response
def delete2(method):
    queryUrl = f"{Config.WEB_API_ENDPONT}/{method}"
    headers = {'Authorization': f"Bearer {Config.auth['accessToken']}", 'FLOW360USER': Config.user['identityId'], "Application":"TIDY3D"}
    return requests.delete(queryUrl, headers=headers)
