import json
import urllib

import requests
from common_structure_microservices.exception import GenericMicroserviceError


def _http_method_mapper(method):
    mapper = {
        'get': 'get',
        'post': 'create',
        'patch': 'retrive',
        'put': 'update',
        'delete': 'delete',
    }
    return mapper.get(method)


def _status_ok(request, raise_exception):
    request_json = json.loads(request.content)
    if not request_json['status'] and raise_exception:
        raise GenericMicroserviceError(status=request.status_code, detail=request_json['errors'])
    return request


class RemoteModel:
    def __init__(self, request, url):
        self.request = request
        self.url = url

    def _headers(self, override_headers=None):
        base_headers = {'content-type': 'application/json; charset=utf-8'}
        override_headers = override_headers or {}
        return {**self.request.headers, **base_headers, **override_headers}

    def _cookies(self, override_cookies=None):
        override_cookies = override_cookies or {}
        return {**self.request.COOKIES, **override_cookies}

    def get(self, entity_id=None, url_path=None, raise_exception=True):
        url_default_path = f'{self.url}{entity_id}/' if entity_id is not None else f'{self.url}'
        url_path = url_default_path if (url_path is None) else f'{self.url}{url_path}'
        return _status_ok(requests.get(url_path, headers=self._headers(), cookies=self._cookies()), raise_exception)

    def create(self, entity_data, url_path=None, raise_exception=True):
        url_path = f'{self.url}' if (url_path is None) else f'{self.url}{url_path}'
        return _status_ok(
            requests.post(url_path, data=json.dumps(entity_data), headers=self._headers(), cookies=self._cookies()),
            raise_exception)

    def update(self, entity_data, entity_id=None, url_path=None, raise_exception=True):
        url_path = f'{self.url}{entity_id}/' if (url_path is None) else f'{self.url}{url_path}'
        return _status_ok(
            requests.put(url_path, data=json.dumps(entity_data), headers=self._headers(), cookies=self._cookies()),
            raise_exception)

    def retrive(self, entity_data, entity_id=None, url_path=None, raise_exception=True):
        url_path = f'{self.url}{entity_id}/' if (url_path is None) else f'{self.url}{url_path}'
        return _status_ok(
            requests.patch(url_path, data=json.dumps(entity_data), headers=self._headers(), cookies=self._cookies()),
            raise_exception)

    def delete(self, entity_id=None, url_path=None, raise_exception=True):
        url_path = f'{self.url}{entity_id}/' if (url_path is None) else f'{self.url}{url_path}'
        return _status_ok(requests.delete(url_path, headers=self._headers(), cookies=self._cookies()), raise_exception)

    def filter(self, raise_exception=True, url_path='', **params):
        params = f'?{urllib.parse.urlencode(params)}'
        return _status_ok(
            requests.get(f'{self.url}{url_path}{params}', headers=self._headers(), cookies=self._cookies()),
            raise_exception)

    def custom(self, url_path='', method=None, data=None, raise_exception=True, **kwargs):
        method = 'get' if (method is None) else method.lower()
        url_path = f'{url_path}/' if (url_path[-1] != '/') else url_path
        for key, value in kwargs.items():
            if f'<{key}>' in url_path:
                url_path = url_path.replace(f'<{key}>', value)

        kwargs = {
            'url_path': url_path
        }
        func = getattr(self, _http_method_mapper(method), self.get)
        if data is not None and method != 'get':
            kwargs.update({'entity_data': data})
        return func(raise_exception=raise_exception, **kwargs)
