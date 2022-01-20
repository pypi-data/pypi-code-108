# import asyncio
# from typing import Dict, Optional
#
import nautilus_trader

# from aiohttp import ClientResponse
# from nautilus_trader.common.clock import LiveClock
# from nautilus_trader.common.logging import Logger
# from nautilus_trader.network.http import HttpClient
# from retrying import retry
#
# from nacre.metrics.metrics import HTTP_ERROR_COUNTER
# from nacre.metrics.metrics import REQ_TIME
from nacre.adapters.binance.http.client import BinanceHttpClient


nautilus_trader.adapters.binance.http.client.BinanceHttpClient = BinanceHttpClient

# _request = HttpClient.request
#
# NAUTILUS_VERSION = nautilus_trader.__version__
#
#
# def retry_if_connect_error(exception):
#     return isinstance(exception, ConnectionError)
#
#
# def __init__(
#     self,
#     loop: asyncio.AbstractEventLoop,
#     clock: LiveClock,
#     logger: Logger,
#     key=None,
#     secret=None,
#     base_url=None,
#     timeout=None,
#     show_limit_usage=False,
#     proxy=None,
# ):
#     super(BinanceHttpClient, self).__init__(
#         loop=loop,
#         logger=logger,
#     )
#     self._clock = clock
#     self._key = key
#     self._secret = secret
#     self._base_url = base_url or self.BASE_URL
#     self._show_limit_usage = show_limit_usage
#     self._proxies = None
#     self._headers = {
#         "Content-Type": "application/json;charset=utf-8",
#         "User-Agent": "nautilus-trader/" + NAUTILUS_VERSION,
#         "X-MBX-APIKEY": key,
#     }
#
#     if timeout is not None:
#         self._headers["timeout"] = timeout
#
#     self._proxy = proxy
#
#     # TODO(cs): Implement limit usage
#
#
# @retry(retry_on_exception=retry_if_connect_error)
# async def request(
#     self,
#     method: str,
#     url: str,
#     headers: Optional[Dict[str, str]] = None,
#     json: Optional[Dict[str, str]] = None,
#     **kwargs,
# ) -> ClientResponse:
#     try:
#         with REQ_TIME.labels(method=method, endpoint=url).time():
#             if self._proxy:
#                 kwargs["proxy"] = self._proxy
#
#             with HTTP_ERROR_COUNTER.labels(method=method, endpoint=url).count_exceptions():
#                 return await _request(self, method, url, headers, json, **kwargs)
#     except ConnectionError as ex:
#         self._log.warning("ConnectionError retrying ...")
#         raise ex
#

# deprecated
# nautilus_trader.adapters.binance.http.client.BinanceHttpClient.request = request
# nautilus_trader.adapters.binance.http.client.BinanceHttpClient.__init__ = __init__
