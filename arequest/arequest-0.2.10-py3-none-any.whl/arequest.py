#!/usr/bin/python3
from urllib.parse import urlsplit, urlencode
import asyncio
import zlib
import gzip
import chardet
import ssl
import json as sjson
import h11

__all__ = ["get", "post", "head", "put", "delete", "options", "patch", "Session", "ConnectionError", "TimeoutError"]

__version__ = "v0.2.10"

async def get(url, **kwargs):

    return await Session().get(url, **kwargs)

async def post(url, **kwargs):

    return await Session().post(url, **kwargs)

async def head(url, **kwargs):

    return await Session().head(url, **kwargs)

async def put(url, **kwargs):

    return await Session().put(url, **kwargs)

async def delete(url, **kwargs):

    return await Session().delete(url, **kwargs)

async def options(url, **kwargs):

    return await Session().options(url, **kwargs)

async def patch(url, **kwargs):

    return await Session().patch(url, **kwargs)


class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key.title(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.title())

    def __delitem__(self, key):
        super().__delitem__(key.title())

    def copy(self):
        return CaseInsensitiveDict(**self._data)


class Response:
    def __init__(self):
        self.status_code = None
        self.headers = None
        self.content = None
        self.url = None
        self.encoding = None
        self.cookies = dict()
        self.rawHeader = b""

    def __repr__(self):
        return f"<Response [{self.status_code}]>"

    @property
    def text(self):
        return self.content.decode(self.encoding, "replace") if self.content else ""

    def json(self):
        if n:=self.text:
            return sjson.loads(n)

    def _setHeaders(self, headers):
        self.headers = CaseInsensitiveDict()
        for key, value in headers:
            if (keyStr:=key.decode().title()) == "Set-Cookie":
                c = value.decode().split(";", 1)[0].strip().split("=")
                if len(c) == 2:
                    self.cookies[c[0]] = c[1].strip("\"")

            self.headers[keyStr] = value.decode()


class Session:
    def  __init__(self):
        self.netloc = ""
        self.writer = None
        self.keepAlive = False

    async def __aenter__(self):
        self.keepAlive = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None

    def __del__(self):
        if self.writer:
            self.writer.close()

    async def get(self, url, **kwargs):

        return await self.request("get", url, **kwargs)

    async def post(self, url, **kwargs):

        return await self.request("post", url,  **kwargs)

    async def head(self, url, **kwargs):

        return await self.request("head", url, **kwargs)

    async def put(self, url, **kwargs):

        return await self.request("put", url, **kwargs)

    async def delete(self, url, **kwargs):

        return await self.request("delete", url, **kwargs)

    async def options(self, url, **kwargs):

        return await self.request("options", url, **kwargs)

    async def patch(self, url, **kwargs):

        return await self.request("patch", url, **kwargs)

    def timeoutCallback(self, task):
        if not (task.done() or task.cancelled()):
            task.cancel()

    async def request(self, method, url, retries=0, timeout=60, allow_redirects=False, **kwargs):
        retries = int(retries)
        if retries < 0: raise ValueError("retries must be positive integer")
        error = None

        loop = asyncio.get_running_loop()

        for i in range(retries + 1):
            try:
                if timeout is None:
                    return await self._request(method, url, **kwargs)
                else:
                    e = loop.call_later(timeout, self.timeoutCallback, asyncio.current_task())
                    resp = await self._request(method, url, **kwargs)
                    e.cancel()
                    return resp
            except asyncio.CancelledError:
                error = TimeoutError("Connection timeout.")
                await self.close()
            except Exception as e:
                error = e
                await self.close()

        if error:
            raise error from None

    async def _request(self, method, url, params=None, data=None, headers=None,
                     cookies=None, verify=True, json=None, file=None, sslHostname=None,
                     contentType=None, getRawHeader=False):

        if method.lower() not in ("get", "post", "head", "put", "delete", "options", "patch"):
            raise ValueError(f"Unsupported method '{method}'")

        url = urlsplit(url)
        if self.keepAlive:
            if self.netloc:
                if self.netloc != url.netloc:
                    if self.writer:
                        await self.close()
                    self.netloc = url.netloc
            else:
                self.netloc = url.netloc
        method = method.upper()

        _headers = dict()
        _headers["Host"] = url.netloc
        _headers["User-Agent"] = f"arequest"
        _headers["Accept-Encoding"] = "gzip, deflate"
        _headers["Accept-Language"] = "*"
        _headers["Accept"] = "*/*"
        _headers["Connection"] = "keep-alive" if self.keepAlive else "close"

        if params:
            if isinstance(params, dict):
                query = urlencode(params)
            else:
                raise TypeError("params must be dict.")

            if url.query:
                query = f"?{url.query}&{params}"
            else:
                query = f"?{params}"
        else:
            query = f"?{url.query}" if url.query else None

        if headers:
            if isinstance(headers, dict):
                for i in headers:
                     _headers[str(i).title()] = headers[i]
            else:
                raise TypeError("headers argument must be dict.")

        if cookies:
            if isinstance(cookies, dict):
                cookies = urlencode(cookies)
            elif not isinstance(cookies, str):
                raise TypeError("cookies argument must be dict or str.")

            _headers["Cookie"] = cookies

        if data:
            if isinstance(data, dict):
                data = urlencode(data)
            elif not isinstance(data, str):
                raise TypeError("data argument must be dict or str.")

            _headers["Content-Length"] = str(len(data))
            _headers["Content-Type"] = "application/x-www-form-urlencoded"

        if json:
            if isinstance(json, dict):
                data = sjson.dumps(json, default=str)
                _headers["Content-Length"] = str(len(data))
                _headers["Content-Type"] = "application/json"
            else:
                raise TypeError("json argument must be dict.")

        if file:
            pass

        if contentType:
            if isinstance(contentType, str):
                 _headers["Content-Type"] = contentType
            else:
                raise TypeError("contentType argument must be str.")


        headers = []
        for key, value in _headers.items(): 
            headers.append((key, value))

        headers.sort()
        conn = h11.Connection(our_role=h11.CLIENT)
        sendData = conn.send(h11.Request(method=method, target=f"{url.path or '/'}{query or ''}", headers=headers))

        if self.keepAlive and self.writer:
            writer = self.writer
            reader = self.reader
        else:
            if url.scheme == "https":
                if not verify:
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
                reader, writer = await asyncio.open_connection(
                    url.hostname, url.port or 443, ssl=verify or context, server_hostname=sslHostname or url.hostname)
            elif url.scheme == "http":
                reader, writer = await asyncio.open_connection(
                    url.hostname, url.port or 80)
            else:
                raise ValueError("Unknown scheme '{url.scheme}'")

        writer.write(sendData)
        if data:
            writer.write(conn.send(h11.Data(data=data.encode())))
        writer.write(conn.send(h11.EndOfMessage()))


        r = Response()
        content = []
        while True:
            try:
                event = conn.next_event()
            except h11.ProtocolError:
                raise ConnectionError("Connection close.")
            if event is h11.NEED_DATA:
                tmpData = await reader.read(2048)
                if getRawHeader:
                    r.rawHeader += tmpData
                    if tmpData.find(b"\r\n\r\n") != -1:
                        r.rawHeader = r.rawHeader.split(b"\r\n\r\n", 1)[0].decode()
                        getRawHeader = False

                conn.receive_data(tmpData)
            elif isinstance(event, h11.Response):
                r._setHeaders(event.headers)
                r.status_code = event.status_code
            elif isinstance(event, h11.Data):
                content.append(event.data)
            elif isinstance(event, h11.ConnectionClosed):
                raise ConnectionError("h11 ConnectionClosed event.")
            elif type(event) is h11.EndOfMessage:
                break

        content = b"".join(content)
        if self.keepAlive and r.headers.get("Connection") and r.headers["Connection"].lower() == "keep-alive":
            conn.start_next_cycle()
            self.reader = reader
            self.writer = writer
        else:
            if self.writer:
                await self.close()
            else:
                writer.close()
                await writer.wait_closed()

        r.url = url.geturl()

        if not content:
            return r

        if (t := r.headers.get("Content-Encoding")):
            if t == "gzip":
                content = gzip.decompress(content)

            elif t == "deflate":
                content = zlib.decompress(content)

            else:
                raise TypeError(f"Unsupported Content-Encoding '{t}'")

        if r.headers.get("Content-Type") and r.headers["Content-Type"].find("charset") != -1:
            r.encoding = r.headers["Content-Type"].split("charset=")[1]
        else:
            r.encoding = chardet.detect(content)["encoding"]

        r.content = content
        return r


class ConnectionError(Exception):
    pass


class TimeoutError(Exception):
    pass


async def main():
    r = await get("https://httpbin.org/get")
    print(r.headers)
    print(r.status_code)
    print(r.encoding)
    print(r.text)


if __name__ == '__main__':
    asyncio.run(main())




