from typing import Any

import aiohttp
import requests


class AsyncHttp:

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.session.connector._force_close = True

    async def async_make_post(self, url, json: Any) -> aiohttp.ClientResponse:
        async with self.session.post(url, json=json) as response:
            return await self._force_read_release(response)

    async def async_make_post_cookie(self, url, json, cookie) -> aiohttp.ClientResponse:
        self.session.cookie_jar.clear()
        async with self.session.post(url, json=json, cookies=cookie) as response:
            return await self._force_read_release(response)

    async def _force_read_release(self, response):
        await response.read()
        await response.release()
        return response
