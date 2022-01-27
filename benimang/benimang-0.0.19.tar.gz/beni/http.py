import gzip
from http.client import HTTPResponse
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlencode
from urllib.request import (HTTPCookieProcessor, Request, build_opener,
                            install_opener, urlopen)

from beni import writefile_bytes
from beni.internal import makeHttpHeaders


def http_get(
    url: str,
    *,
    headers: dict[str, Any] | None = None,
    timeout: int = 10,
    retry: int = 1,
):
    while True:
        retry -= 1
        try:
            method = 'GET'
            request = Request(url=url, headers=makeHttpHeaders(headers), method=method)
            response: HTTPResponse
            with urlopen(request, timeout=timeout) as response:
                result = response.read()
                if response.headers.get('Content-Encoding') == 'gzip':
                    result = gzip.decompress(result)
                return result, response
        except:
            if retry <= 0:
                raise


def http_post(
    url: str,
    *,
    data: bytes | dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    timeout: int = 10,
    retry: int = 1,
):
    while True:
        retry -= 1
        try:
            method = 'POST'
            postData = data
            if type(data) is dict:
                postData = urlencode(data).encode()
            request = Request(url=url, data=cast(bytes, postData), headers=makeHttpHeaders(headers), method=method)
            response: HTTPResponse
            with urlopen(request, timeout=timeout) as response:
                result = response.read()
                contentEncoding = response.headers.get('Content-Encoding')
                if contentEncoding == 'gzip':
                    result = gzip.decompress(result)
                return result, response
        except:
            if retry <= 0:
                raise


def http_download(url: str, file: Path, timeout: int = 300):
    result, response = http_get(url, timeout=timeout)
    assert len(result) == response.length
    writefile_bytes(file, result)


# Cookie
_cookie = CookieJar()
_cookieProc = HTTPCookieProcessor(_cookie)
_opener = build_opener(_cookieProc)
install_opener(_opener)
