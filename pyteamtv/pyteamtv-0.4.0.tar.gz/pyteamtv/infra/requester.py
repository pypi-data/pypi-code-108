import time

import requests
import logging


logger = logging.getLogger(__name__)


class Requester(object):
    def __init__(self, base_url, jwt_token, headers:dict = None):
        self._base_url = base_url
        self.jwt_token = jwt_token
        self.headers = dict(**headers) if headers else {}

    def request(self, method, url, input_=None):
        import pyteamtv

        start = time.time()
        headers = self.headers
        headers['Authorization'] = f'Bearer {self.jwt_token}'
        headers['User-Agent'] = f'pyteamtv {pyteamtv.__version__}'
        logger.debug(f"Sending {method} request to {url} - {self.headers}")
        response = requests.request(
            method,
            self._base_url + url,
            headers=headers,
            json=input_
        )
        took = time.time() - start
        logger.debug(f"Request took: {took * 1000:.2f}ms")
        if response.status_code != 200:
            raise Exception(str(response))

        return response.json()

    def with_extra_headers(self, headers:dict):
        new_headers = dict(**self.headers)
        new_headers.update(headers)
        return self.__class__(
            self._base_url,
            self.jwt_token,
            headers
        )


