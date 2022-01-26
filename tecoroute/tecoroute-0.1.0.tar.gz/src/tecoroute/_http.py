from io import BytesIO
from itertools import chain
from socket import socket
from typing import Dict, NoReturn, Optional, Union
from urllib.parse import urlparse, urlunparse

from tornado.http1connection import HTTP1Connection
from tornado.httpclient import HTTPRequest, HTTPResponse
from tornado.httputil import (
    HTTPHeaders,
    HTTPMessageDelegate,
    RequestStartLine,
    ResponseStartLine,
)
from tornado.iostream import IOStream, StreamClosedError

from ._misc import dist


class _HttpMessage(HTTPMessageDelegate):  # type: ignore
    def __init__(self) -> None:
        self._buffer = BytesIO()
        self._headers: Optional[HTTPHeaders] = None
        self._start_line: Optional[Union[RequestStartLine, ResponseStartLine]] = None

    def headers_received(
        self,
        start_line: Union[RequestStartLine, ResponseStartLine],
        headers: HTTPHeaders,
    ) -> None:
        self._start_line = start_line
        self._headers = headers

    def data_received(self, chunk: bytes) -> None:
        self._buffer.write(chunk)

    def finish(self) -> None:
        pass

    def on_connection_close(self) -> NoReturn:
        raise StreamClosedError(Exception("HTTP is closed"))

    @property
    def start_line(self) -> Union[RequestStartLine, ResponseStartLine]:
        if not self._start_line:
            raise RuntimeError
        return self._start_line

    @property
    def headers(self) -> HTTPHeaders:
        if not self._headers:
            raise RuntimeError
        return self._headers

    @property
    def buffer(self) -> BytesIO:
        return self._buffer


class HttpClient:
    """TODO."""

    def __init__(self, host: str, port: int) -> None:
        """:class:`HttpClient` constructor."""
        self._sock = socket()
        self._sock.connect((host, port))
        self._stream = IOStream(self._sock)
        self._connection = HTTP1Connection(self._stream, True)

    async def send_request(
        self, request: HTTPRequest, headers_raw: Optional[Dict[str, str]]
    ) -> None:
        """TODO."""
        url_tuple = urlparse(request.url)
        url_from_path = urlunparse(("",) * 2 + url_tuple[2:]) or "/"
        request.headers.setdefault("Host", "NT_Host")
        if request.body is not None:
            request.headers.setdefault("Content-Length", str(len(request.body)))
        request.headers.setdefault(
            "User-Agent",
            f"{dist.metadata['Name']}/{dist.version} (+{dist.metadata['Home-page']})",
        )

        # Tornado's method write_headers doesn't support case sensitive headers,
        # so start line and headers must be formated here and written directly to stream
        raw = f"{request.method} {url_from_path} HTTP/1.1\r\n"
        for key, value in chain(
            request.headers.get_all(),
            (headers_raw if headers_raw is not None else {}).items(),
        ):
            raw += f"{key}: {value}\r\n"
        raw += "\r\n"
        await self._connection.stream.write(raw.encode("ascii"))

        if request.body is not None:
            self._connection.write(request.body)
        self._connection.finish()

    async def receive_response(
        self, request: Optional[HTTPRequest] = None
    ) -> HTTPResponse:
        """TODO."""
        http_message = _HttpMessage()
        await self._connection.read_response(http_message)
        assert isinstance(http_message.start_line, ResponseStartLine)
        return HTTPResponse(
            request or HTTPRequest(""),
            http_message.start_line.code,
            headers=http_message.headers,
            buffer=http_message.buffer,
            reason=http_message.start_line.reason,
        )

    async def request(
        self, request: HTTPRequest, headers_raw: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """TODO."""
        await self.send_request(request, headers_raw=headers_raw)
        return await self.receive_response(request=request)

    def close(self) -> None:
        """TODO."""
        self._connection.detach()
        self._stream.close()
        self._sock.close()
