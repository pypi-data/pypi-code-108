import requests
from dnoticias_services.utils.request import get_headers


class BaseService:
    class Meta:
        abstract = True

    def __init__(self):
        self.api_url = ''
        self.api_key = ''
        self.timeout = ''

    def set_api_url(self, api_url: str, arguments: list = ()):
        self.api_url = api_url.format(*arguments) if arguments else api_url

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def post(self, params: dict, json: dict, api_key=None, timeout=None):
        if api_key:
            self.set_api_key(api_key)

        response = requests.post(
            self.api_url,
            headers=get_headers(self.api_key),
            params=params or None,
            json=json or None,
            timeout=timeout or None,
        )

        response.raise_for_status()
        return response

    def get(self, params: dict, api_key=None, timeout=None):
        if api_key:
            self.set_api_key(api_key)

        response = requests.get(
            self.api_url,
            headers=get_headers(self.api_key),
            params=params or None,
            timeout=timeout or None,
        )

        response.raise_for_status()
        return response
