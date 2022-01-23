from http import HTTPStatus
import requests
from requests import HTTPError
import os

from zaiclient.auth import ZaiHmacAuth
from zaiclient import config
from zaiclient import http

class ZaiClient(object):

    def __init__(self, client_id: str=None, secret: str=None):

        if type(client_id) != str:
            raise TypeError('Client ID must be a string value.')
        if type(secret) != str:
            raise TypeError('Secret must be a string value.')
        if type(config.API_ENDPOINT) != str:
            raise TypeError('API endpoint must be a string object.')
        if not config.API_ENDPOINT.startswith('https://'):
            raise Exception('Must connect with SSL/TLS protocol.')
        if type(config.TIMEOUT) != int:
            raise TypeError('Timeout must be an integer value.')
        if config.TIMEOUT <= 0 or config.TIMEOUT > 300:
            raise ValueError('Timeout must be greater than 0 and less than or equal to 300 seconds.')

        if client_id is None:
            try:
                self.__client_id = os.environ[config.ZAI_CLIENT_ID_ENV]
            except KeyError as e:
                raise KeyError(f'Required environment varible is not set: {config.ZAI_CLIENT_ID_ENV}')
        else:
            if type(client_id) != str:
                raise TypeError('Client ID must be a string value.')
            self.__client_id = client_id

        self.__auth = ZaiHmacAuth(client_id, secret)
        self.__endpoint = config.API_ENDPOINT
        self.__timeout = config.TIMEOUT

    def _send_request(self, method: str, url: str, payload) -> requests.Response:
        try:
            response = requests.request(
                method=method,
                url=url,
                params=None,
                data=None,
                json=payload,
                headers={},
                cookies=None,
                files=None,
                auth=self.__auth,
                timeout=self.__timeout,
                verify=True
            )
        except HTTPError as http_err:
            print(f'An HTTP error has occurred: {http_err}')
        except Exception as err:
            print(f'An exception has occurred: {err}')

        status_code = response.status_code
        headers = response.headers
        body = response.json()

        if status_code == HTTPStatus.OK and headers['Content-Type'] == 'application/json':
            return body
        else:
            return None
    
    def get_recommendation(self, user_id: str=None, user_history: list=None) -> list:
        body = self._send_request(http.GET, f'{self.__endpoint}/{self.__client_id}', {})
        
        return body
