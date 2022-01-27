import time
from logging import Logger
from pbx_component_files_uploader.exceptions.errors import EmptyAuthField
from .token import Token

import requests


class Auth:
    AUTH_URL = 'https://auth.selcdn.ru/'

    def __init__(self, authData: dict, tokenCacheDir: str, requests: requests, logger: Logger):
        self.tokenCacheDir = tokenCacheDir
        if not tokenCacheDir:
            raise EmptyAuthField('token_cache_dir')
        self.check_auth_data(authData=authData)
        self.username = authData.get('username', '')
        self.password = authData.get('password', '')
        self.container = authData.get('container', '')

        self.requests = requests
        self.logger = logger
        self.token = Token(tokenCacheDir=tokenCacheDir, logger=logger).load()

    def check_auth_data(self, authData: dict) -> None:
        for k, v in authData.items():
            if not v:
                raise EmptyAuthField(k)

    def update_auth_token(self, new_token, storage_url, expires):
        self.token.secret = new_token
        self.token.storageUrl = storage_url
        self.token.expiresAt = int(time.time()) + int(expires)
        self.token.update()

    def authenticate(self):
        self.logger.debug('Need to authenticate with %s:%s',
                          self.username, self.password)
        resp = self.requests.get(self.AUTH_URL, headers={
            'X-Auth-User': self.username,
            'X-Auth-Key': self.password
        })
        if resp.status_code != 204:
            self.logger.debug(
                'Got an unexpected response from auth: %s', resp.content)
            raise Exception("Selectel: Unexpected status code: %s" %
                            resp.status_code)
        self.update_auth_token(
            resp.headers['X-Auth-Token'], resp.headers['X-Storage-Url'], resp.headers['X-Expire-Auth-Token'])

    def get_storage_data(self) -> dict:
        if self.token.is_expired():
            self.authenticate()

        return {
            'secret': self.token.secret,
            'storage_url': self.token.storageUrl,
            'container': self.container
        }
