from tornado.simple_httpclient import SimpleAsyncHTTPClient
from tornado.httpclient import HTTPClientError
import json

PYPY_URL = 'https://pypi.org/pypi/tinybird-cli/json'


class CheckPypi:
    client = SimpleAsyncHTTPClient()

    async def get_latest_version(self):
        try:
            response = await self.client.fetch(PYPY_URL)
            result = json.loads(response.body)
            return result['info']['version']
        except HTTPClientError as e:
            response = e.response
        except Exception as e:
            print(f'Error getting package info: {e}')
