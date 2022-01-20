import gzip
from http.cookiejar import CookieJar
from typing import Any
from urllib.parse import urlencode
from urllib.request import (HTTPCookieProcessor, Request, build_opener,
                            install_opener, urlopen)

_defaultHeader = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}


# Cookie
_cookie = CookieJar()
_cookieProc = HTTPCookieProcessor(_cookie)
_opener = build_opener(_cookieProc)
install_opener(_opener)


def getHeaderByDefault(headers: dict[str, str] | None):
    result = dict(_defaultHeader)
    if headers:
        for key, value in headers.items():
            result[key] = value
    return result


def httpGet(url: str, headers: dict[str, str] | None = None, timeout: int = 30, retry: int = 3):
    method = 'GET'
    if headers:
        headers = getHeaderByDefault(headers)
    result: bytes = b""
    response = None
    currentTry = 0
    while currentTry < retry:
        currentTry += 1
        try:
            request = Request(url=url, headers=headers or {}, method=method)
            with urlopen(request, timeout=timeout) as response:
                result = response.read()
            break
        except Exception:
            pass
    if response is not None:
        contentEncoding = response.headers.get('Content-Encoding')
        if contentEncoding == 'gzip':
            result = gzip.decompress(result)
    return result, response


def httpPost(url: str, data: Any = None, headers: dict[str, str] = {}, timeout: int = 30, retry: int = 3):
    method = 'POST'
    headers = getHeaderByDefault(headers)
    postData = data
    if type(data) == dict:
        postData = urlencode(data).encode()
    result = None
    response = None
    currentTry = 0
    while currentTry < retry:
        currentTry += 1
        try:
            request = Request(url=url, data=postData, headers=headers, method=method)
            response = urlopen(request, timeout=timeout)
            result = response.read()
            response.close()
            break
        except Exception:
            pass
    return result, response
