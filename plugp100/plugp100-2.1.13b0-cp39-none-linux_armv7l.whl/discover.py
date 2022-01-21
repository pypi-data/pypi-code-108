import logging

import aiohttp
import jsons

from plugp100.core.encryption import Encryption
from plugp100.core.http_client import AsyncHttp
from plugp100.core.methods import HandshakeMethod
from plugp100.core.params import HandshakeParams

logger = logging.getLogger(__name__)


class TapoApiDiscover:

    @staticmethod
    async def is_tapo_device(address: str, session: aiohttp.ClientSession = None) -> bool:
        url = f"http://{address}/app"
        http = AsyncHttp(aiohttp.ClientSession() if session is None else session)
        key_pair = Encryption().generate_key_pair()

        handshake_method = HandshakeMethod(
            HandshakeParams(key_pair.get_public_key())
        )

        request_body = jsons.dump(handshake_method)

        try:
            response = await http.async_make_post(url, json=request_body)
            resp_dict = await response.json()

            if 'error_code' in resp_dict:
                if resp_dict['error_code'] != 0:
                    return False

            cookie = response.cookies.get('TP_SESSIONID').value
            key = resp_dict['result']['key']

            return cookie and cookie != "" and key and key != ""
        except Exception as e:
            logger.exception(e)
            return False
