from hashlib import sha256
import hmac
import os
from typing import Type
import requests
from requests.auth import AuthBase
import time

from zaiclient import config

class ZaiHmacAuth(AuthBase):
    '''Z.ai client-side authentication'''

    def __init__(self, client_id: str=None, secret: str=None):
        if client_id is None:
            try:
                self.__client_id = os.environ[config.ZAI_CLIENT_ID_ENV]
            except KeyError as e:
                raise KeyError(f'Required environment varible is not set: {config.ZAI_CLIENT_ID_ENV}')
        else:
            if type(client_id) != str:
                raise TypeError('Client ID must be a string value.')
            self.__client_id = client_id
        if secret is None:
            try:
                self.__secret = os.environ[config.ZAI_CLIENT_SECRET_ENV]
            except KeyError as e:
                raise KeyError(f'Required environment varible is not set: {config.ZAI_CLIENT_SECRET_ENV}')
        else:
            if type(secret) != str:
                raise TypeError('Secret must be a string value.')
            self.__secret = secret

    def __call__(self, request: requests.Request) -> requests.Request:
        timestamp = str(int(time.time()))
        request.headers[config.ZAI_CLIENT_ID_HEADER] = self.__client_id
        request.headers[config.ZAI_UNIX_TIMESTAMP_HEADER] = timestamp
        request.headers[config.ZAI_AUTHORIZATION_HEADER] = f'Zai {self.__sign(request, timestamp)}'

        return request

    def __sign(self, request, timestamp):
        message = f'{self.__client_id}:{request.url}:{timestamp}'
        signature = hmac.new(
            str.encode(self.__secret, encoding='UTF-8'),
            str.encode(message, encoding='UTF-8'),
            sha256
        ).hexdigest()

        return signature
