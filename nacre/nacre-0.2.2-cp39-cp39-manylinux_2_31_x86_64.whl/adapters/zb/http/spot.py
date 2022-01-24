import hashlib
import hmac
import time
from typing import Any, Dict

import nautilus_trader
from aiohttp import ClientConnectorError

from nacre.adapters.zb.http.client import ZbHttpClient
from nacre.adapters.zb.http.error import ZbOperationError


NAUTILUS_VERSION = nautilus_trader.__version__


def retry_if_connect_error(exception):
    return isinstance(exception, ClientConnectorError)


class ZbSpotHttpClient(ZbHttpClient):

    BASE_URL = "https://api.zb.company"  # market api
    # BASE_URL = "https://trade.zb.company"  # trade api

    async def sign_request(
        self,
        http_method: str,
        url_path: str,
        payload: Dict[str, Any] = None,
    ) -> Any:
        if payload is None:
            payload = {}
        payload["accesskey"] = self._key
        query_string = self._prepare_params(payload)
        payload["sign"] = hmac.new(
            bytes(self._hashed_secret, encoding="utf-8"), query_string.encode("utf-8"), hashlib.md5
        ).hexdigest()
        payload["reqTime"] = (int)(time.time() * 1000)

        return await self.send_request(http_method, url_path, payload)

    def _raise_if_operation_code_error(self, resp: Dict):
        code = resp.get("code")
        if code is None:
            return
        elif code == 1000:
            return
        else:
            raise ZbOperationError(status=code, message=str(resp))
