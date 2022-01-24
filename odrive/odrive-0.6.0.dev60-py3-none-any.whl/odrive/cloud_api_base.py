import datetime
import json

import odrive.crypto as crypto
from odrive.crypto import b64encode

API_BASE_ADDR = 'https://api.odriverobotics.com'

class APIBase():
    def __init__(self, session, api_base_addr: str = API_BASE_ADDR, key = None):
        self._session = session
        self._api_base_addr = api_base_addr
        self._key = None if key is None else crypto.load_private_key(key)

    async def call(self, method: str, endpoint: str, inputs=None):
        url = self._api_base_addr + endpoint
        content = json.dumps(inputs or {}).encode('utf-8')
        headers = {
            'content-type': 'application/json; charset=utf-8'
        }

        if not self._key is None:
            url_bytes = endpoint.encode('utf-8')
            timestamp_bytes = int(datetime.datetime.now().timestamp()).to_bytes(8, 'little', signed=False)
            message = url_bytes + b':' + timestamp_bytes + b':' + content
            signature = crypto.sign(self._key, message)
            headers['Authorization'] = 'hmacauth ' + ':'.join([
                b64encode(crypto.get_public_bytes(self._key.public_key())),
                b64encode(timestamp_bytes),
                b64encode(signature)
            ])

        async with self._session.request(method, url, headers=headers, data=content, ) as response:
            if response.status != 200:
                try:
                    ex_data = await response.json()
                except:
                    ex_raw = await response.read()
                    raise Exception(f"Server failed with {response.status} ({response.reason}): {ex_raw}")
                else:
                    tb = ''.join(ex_data['traceback'])
                    raise Exception(f"Server failed with {response.status} ({response.reason}): {ex_data['message']} in \n{tb}")

            return await response.json()

    async def download(self, url: str):
        async with self._session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Server failed with {response.status} ({response.reason})")
            return await response.read()
