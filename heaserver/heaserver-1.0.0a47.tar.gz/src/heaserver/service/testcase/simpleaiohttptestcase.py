from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web
from json import loads
from typing import Union


class SimpleAioHTTPTestCase(AioHTTPTestCase):

    async def get_application(self) -> web.Application:
        return web.Application()

    def _assert_json_string_equals(self, expected: Union[str, bytes, bytearray], actual: Union[str, bytes, bytearray]) -> None:
        self.assertEqual(loads(expected), loads(actual))
