from pathlib import Path
from typing import Any, Final
from urllib.parse import urlencode

import aiohttp

from beni.async_func import set_async_limit, wrapper_async_limit
from beni.internal import makeHttpHeaders

LIMIT_TAG_HTTP: Final = 'http'

set_async_limit(LIMIT_TAG_HTTP, 10)


@wrapper_async_limit(LIMIT_TAG_HTTP)
async def async_http_get(
    url: str,
    *,
    headers: dict[str, Any] | None = None,
    timeout: int = 10,
    retry: int = 1
):
    while True:
        retry -= 1
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=makeHttpHeaders(headers), timeout=timeout) as response:
                    result = await response.read()
                    return result, response
        except:
            if retry <= 0:
                raise


@wrapper_async_limit(LIMIT_TAG_HTTP)
async def async_http_post(
    url: str,
    *,
    data: bytes | dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    timeout: int = 10,
    retry: int = 1
):
    while True:
        retry -= 1
        try:
            postData = data
            if type(data) is dict:
                postData = urlencode(data).encode()
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=postData, headers=makeHttpHeaders(headers), timeout=timeout) as response:
                    result = await response.read()
                    return result, response
        except:
            if retry <= 0:
                raise


async def async_http_download(url: str, file: Path, timeout: int = 300):
    result, response = await async_http_get(url, timeout=timeout)
    assert len(result) == response.content_length
    import beni.async_file as async_file
    await async_file.async_writefile_bytes(file, result)
