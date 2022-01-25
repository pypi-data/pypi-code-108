# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import errno
import http.client as httplib
import json
import os
import random
import socket
import ssl
import struct
import sys

from collections import OrderedDict
from io import BytesIO
from typing import (
    Any,
    AnyStr,
    Callable,
    cast,
    Dict,
    IO,
    Iterator,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from qumulo.lib import log
from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_BINARY = 'application/octet-stream'

DEFAULT_CHUNKED = False
DEFAULT_CHUNK_SIZE_BYTES = 1024

NEED_LOGIN_MESSAGE = 'Need to log in first to establish credentials.'

PRIV_PORT_BEG = 900
PRIV_PORT_END = 1024

LOCALHOSTS = frozenset(['localhost', 'ip6-localhost', '127.0.0.1', '::1'])

RequestFunction = TypeVar('RequestFunction', bound=Callable[..., 'RestResponse'])

PagingRequestFunction = TypeVar('PagingRequestFunction', bound=Callable[..., 'PagingIterator'])

VoidRequestFunction = TypeVar('VoidRequestFunction', bound=Callable[..., 'None'])

# Order of evaluation is important. If host is not local, don't check
# uid at all, which is not available on all platforms.
def user_is_local_root(host: str) -> bool:
    return host in LOCALHOSTS and os.geteuid() == 0


# Decorator for request methods that return RestResponse
def request(fn: RequestFunction) -> RequestFunction:
    setattr(fn, 'request', True)
    return fn


# Decorator for request methods that return PagingIterator
def paging_request(fn: PagingRequestFunction) -> PagingRequestFunction:
    setattr(fn, 'request', True)
    return fn


# Decorator for request methods that return nothing
def void_request(fn: VoidRequestFunction) -> VoidRequestFunction:
    setattr(fn, 'request', True)
    return fn


def pretty_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, indent=4)


def stream_writer(conn: IO[bytes], file_: IO[bytes]) -> None:
    chunk_size = 128 * 1024
    while True:
        data = conn.read(chunk_size)
        if len(data) == 0:
            return
        file_.write(data)


# We set various TCP socket options for HTTPS connections by overriding
# httplib.HTTPSConnection. When/if Qumulo Core supports http (vs. https) we need to do
# the same for httplib.HTTPConnection. The options set here are consistent with those
# set on socket in the product.
class HTTPSConnectionWithSocketOptions(httplib.HTTPSConnection):
    # Default TCP keepalive settings consistent with net/posix_socket.h
    DEFAULT_KEEPALIVE_IDLE_TIME = 60  # seconds before sending keepalive probes
    DEFAULT_KEEPALIVE_PROBE_COUNT = 3  # keepalive probes before giving up
    DEFAULT_KEEPALIVE_PROBE_INTERVAL = 10  # seconds between probes
    DEFAULT_TCP_USER_TIMEOUT = 90 * 1000  # ms timeout on unacked transmits

    def connect(self) -> None:
        httplib.HTTPSConnection.connect(self)

        # QFS-14181: httplib doesn't set TCP_NODELAY on sockets. Set it here to reduce
        # request latency.
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Enable TCP keepalive to ensure that dead connections are detected more
        # quickly. This fixes an issue in automation where a dropped connection can
        # cause REST calls to hang.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # Versions of Windows prior to Windows 10 1709 did not support TCP_KEEP*
        # options, so check for them before setting them.
        if (
            hasattr(socket, 'TCP_KEEPIDLE')
            and hasattr(socket, 'TCP_KEEPCNT')
            and hasattr(socket, 'TCP_KEEPINTVL')
        ):
            self.sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.DEFAULT_KEEPALIVE_IDLE_TIME
            )
            self.sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_KEEPCNT, self.DEFAULT_KEEPALIVE_PROBE_COUNT
            )
            self.sock.setsockopt(
                socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, self.DEFAULT_KEEPALIVE_PROBE_INTERVAL
            )
        elif hasattr(socket, 'SIO_KEEPALIVE_VALS'):
            # Windows uses this ioctl to set keepalive parameters
            self.sock.ioctl(
                getattr(socket, 'SIO_KEEPALIVE_VALS'),
                (
                    1,  # enable
                    self.DEFAULT_KEEPALIVE_IDLE_TIME * 1000,  # idle time in ms
                    self.DEFAULT_KEEPALIVE_PROBE_INTERVAL * 1000,  # interval in ms
                ),
            )

        # Set the TCP user timeout, if available. Versions of Python before 3.6 didn't
        # have this constant, so we have to check for it.
        if hasattr(socket, 'TCP_USER_TIMEOUT'):
            self.sock.setsockopt(
                socket.SOL_TCP, socket.TCP_USER_TIMEOUT, self.DEFAULT_TCP_USER_TIMEOUT
            )
        elif sys.platform.startswith('linux'):
            # For Python < 3.6 running on Linux, we'd still like to set the TCP user
            # timeout, so we'll just grab the value explicitly from
            # /usr/include/linux/tcp.h
            self.sock.setsockopt(socket.SOL_TCP, 18, self.DEFAULT_TCP_USER_TIMEOUT)


class Connection:
    def __init__(
        self,
        host: str,
        port: int,
        chunked: bool = DEFAULT_CHUNKED,
        chunk_size: int = DEFAULT_CHUNK_SIZE_BYTES,
        timeout: Optional[int] = None,
        reuse: Optional[bool] = None,
        user_agent: Optional[str] = None,
    ):
        self.scheme = 'https'
        self.host = host
        self.port = port
        self.chunked = chunked
        self.chunk_size = chunk_size
        self.conn: Optional[HTTPSConnectionWithSocketOptions] = None
        self.backdoor = user_is_local_root(host)
        self.timeout = timeout
        self.reuse_connection = not self.backdoor if reuse is None else reuse
        self.user_agent = user_agent

    def set_reuse_flag(self, reuse: bool) -> None:
        self.reuse_connection = reuse

    def must_close(self) -> bool:
        return not self.reuse_connection

    def _get_connection(self, port: Optional[int] = None) -> HTTPSConnectionWithSocketOptions:
        kwargs: Dict[str, Any] = {
            'context': ssl.SSLContext(ssl.PROTOCOL_TLSv1_2),
            'timeout': self.timeout,
        }
        if port is not None:
            kwargs['source_address'] = (self.host, port)

        return HTTPSConnectionWithSocketOptions(self.host, self.port, **kwargs)

    def connect_backdoor(self) -> HTTPSConnectionWithSocketOptions:
        ports = list(range(PRIV_PORT_BEG, PRIV_PORT_END))
        random.shuffle(ports)

        last_error = socket.error('Disable raising-bad-type')
        for port in ports:
            try:
                conn = self._get_connection(port)
                conn.connect()
                # Set SO_LINGER on backdoor sockets created for root-initiated
                # connections to localhost to force an immediate RST on close.
                # We have a very limited number of privileged ports available
                # to bind to and short-lived REST connections can otherwise
                # easily exhaust those with TIME_WAIT connections.
                conn.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
                return conn
            except OSError as e:
                last_error = e
        # If we tried all the ports, we'll bail out with the last error we got
        # which is likely a connection refused error meaning the server
        # is not up.  A little lame that we go through all the ports to
        # determine this, but it's quick.
        raise last_error

    def connect(self) -> HTTPSConnectionWithSocketOptions:
        if self.backdoor and self.conn and not self.reuse_connection:
            # Need to close the connection to get a new local priv port, the one
            # stuck in the conn is probably in TIME_WAIT.
            self.conn = None
        if self.conn is None:
            if self.backdoor:
                self.conn = self.connect_backdoor()
            else:
                self.conn = self._get_connection()

        return self.conn

    def close(self) -> None:
        """
        Close the underlying network connection.

        An explicit close() should not strictly be necessary, as refcount GC
        will also ensure the connection gets closed. This provides a stronger
        guarantee or tighter control if desired (e.g. it might be useful when a
        long lived instance has long idle periods).
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def reconnect(self) -> HTTPSConnectionWithSocketOptions:
        self.close()
        return self.connect()


class APIException(Exception):
    """
    Unusual errors when sending request or receiving response.
    """

    pass


class RequestError(Exception):
    """
    An error response to an invalid REST request. A combination of HTTP status code,
    HTTP status message and REST error response.
    """

    def __init__(
        self, status_code: int, status_message: str, json_error: Optional[Mapping[str, Any]] = None
    ):
        self.status_code = status_code
        self.status_message = str(status_message)

        json_error = {} if json_error is None else json_error

        module = json_error.get('module', 'qumulo.lib.request')
        self.module = str(module)

        error_class = json_error.get('error_class', 'unknown')
        self.error_class = str(error_class)

        if 'description' in json_error:
            self.description = json_error['description']
        elif status_code == 401:
            self.description = NEED_LOGIN_MESSAGE
        else:
            self.description = 'Dev error: No json error response.'

        self.stack = json_error.get('stack', [])
        self.user_visible = json_error.get('user_visible', False)

        inner = json_error.get('inner', None)
        self.inner: Optional[RequestError] = None
        if inner is not None:
            self.inner = RequestError(status_code, status_message, inner)

        formatted = '\n'.join(' ' * 4 + frame for frame in self.stack)
        formatted = formatted or '    (no backtrace)'
        message = 'Error {}: {}: {}\nBacktrace:\n{}'.format(
            str(self.status_code), str(self.error_class), str(self.description), str(formatted)
        )
        super().__init__(message)

    def pretty_str(self) -> str:
        """
        This formatting of the error is used by QQ to display the error nicely
        to a user.
        """
        return f'Error {self.status_code}: {self.error_class}: {self.description}'


#  ____                            _
# |  _ \ ___  __ _ _   _  ___  ___| |_
# | |_) / _ \/ _` | | | |/ _ \/ __| __|
# |  _ <  __/ (_| | |_| |  __/\__ \ |_
# |_| \_\___|\__, |\__,_|\___||___/\__|
#               |_|


class APIRequest:
    """REST API request class."""

    def __init__(
        self,
        conninfo: Connection,
        credentials: Optional[Credentials],
        method: str,
        uri: str,
        body: Union[Sequence[object], Mapping[str, object]] = None,
        body_file: Optional[IO[AnyStr]] = None,
        if_match: Optional[str] = None,
        request_content_type: str = CONTENT_TYPE_JSON,
        response_file: IO[bytes] = None,
        headers: Mapping[str, str] = None,
    ):
        self.conninfo = conninfo
        self.credentials = credentials
        self.method = method
        self.uri = uri
        self.chunked = conninfo.chunked
        self.chunk_size = conninfo.chunk_size
        self.response: Optional[httplib.HTTPResponse] = None
        self.response_etag: Optional[str] = None
        self._response_data: Optional[bytes] = None
        self.response_obj: Union[Dict[str, object], List[object], None] = None
        self.conn = self.conninfo.connect()
        self._headers: Dict[str, Any] = OrderedDict()
        self._headers.update(headers or {})
        if if_match is not None:
            self._headers['If-Match'] = if_match
        if self.conninfo.user_agent:
            self._headers['User-Agent'] = self.conninfo.user_agent

        # Request type defaults to JSON. If overridden, body_file is required.
        self.request_content_type = request_content_type
        if request_content_type != CONTENT_TYPE_JSON:
            assert body_file is not None, 'Binary request requires body_file'

        self.response_file = response_file

        self.body_file: Optional[Union[IO[str], IO[bytes]]] = None
        self.body_text = None
        self.body_length = 0
        if body_file is not None:
            self.body_file = body_file

            # Most http methods want to overwrite fully, so seek to 0.
            if not method == 'PATCH':
                try:
                    body_file.seek(0, 0)
                except OSError:
                    # file is a stream, and therefore can't be seeked.
                    pass

            if not self.chunked:
                current_pos = body_file.tell()
                body_file.seek(0, 2)
                self.body_length = body_file.tell() - current_pos
                body_file.seek(current_pos, 0)

        elif body is not None:
            self.body_text = body
            json_blob = json.dumps(body, ensure_ascii=True)
            self.body_file = BytesIO(json_blob.encode('utf-8'))
            # json_blob will only contain ascii characters so its length is the
            # same as its size in bytes.
            self.body_length = len(json_blob)

    def _needs_body(self) -> bool:
        return self.method in ('PUT', 'POST', 'PATCH')

    def send_request(self) -> None:
        self._headers['Content-Type'] = self.request_content_type
        if self.conninfo.must_close():
            self._headers['Connection'] = 'close'

        # cf request.c: our http server actually returns an error
        # if we send an empty body for, for example, GET. Various
        # tests will set "chunked" on a connection and request
        # inherits that. Avoid sending empty bodies.
        if self.chunked and self._needs_body():
            self._headers['Transfer-Encoding'] = 'chunked'
        else:
            self._headers['Content-Length'] = self.body_length

        if self.credentials:
            self._headers['Authorization'] = self.credentials.auth_header()

        log.debug(
            'REQUEST: {method} {scheme}://{host}:{port}{uri}'.format(
                method=self.method,
                scheme=self.conninfo.scheme,
                host=self.conninfo.host,
                port=self.conninfo.port,
                uri=self.uri,
            )
        )

        log.debug('REQUEST HEADERS:')
        for header in self._headers:
            log.debug(f'    {header}: {self._headers[header]}')

        if self.body_length > 0:
            log.debug('REQUEST BODY:')
            if self.request_content_type == CONTENT_TYPE_BINARY:
                log.debug(
                    '\tContent elided. File info: %s (%d bytes)'
                    % (self.body_file, self.body_length)
                )
            else:
                log.debug(self.body_text)
                assert self.body_file
                self.body_file.seek(0)

        # Wrap any random errors in a HttpException to make them more palatable.
        try:
            if self.conn.sock is None:
                self.conn.connect()
        except (httplib.HTTPException, OSError):
            # Already an HTTPException, so just raise it and socket errors are
            # cool too.
            raise
        except Exception as e:
            # Wrap it, but save the type, message, and stack.
            errno_attr = getattr(e, 'errno', None)
            message = os.strerror(errno_attr) if errno_attr is not None else str(e)
            wrap = httplib.HTTPException(f'{sys.exc_info()[0]}: {message}')
            raise wrap.with_traceback(sys.exc_info()[2])

        try:
            self.conn.putrequest(self.method, self.uri)

            for name, value in self._headers.items():
                self.conn.putheader(name, value)

            self.conn.endheaders()

            # Chunked transfer encoding. Details:
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.6.1
            # On our server side chunks are processed by chunked_xfer_istream.h
            if self.chunked and self._needs_body():
                if self.body_file is not None:
                    while True:
                        chunk = self.body_file.read(self.chunk_size)
                        chunk_bytes = chunk if isinstance(chunk, bytes) else chunk.encode()
                        chunk_size = len(chunk_bytes)
                        if chunk_size == 0:
                            break
                        msg = f'{chunk_size:x}\r\n'.encode()
                        msg += chunk_bytes
                        msg += b'\r\n'
                        self.conn.send(msg)

                self.conn.send(b'0\r\n\r\n')
            elif self.body_file is not None:
                self.conn.send(self.body_file)

        except OSError as e:
            # Allow EPIPE, server probably sent us a response before breaking
            if e.errno != errno.EPIPE:
                raise

    def get_response(self) -> None:
        try:
            self.response = self.conn.getresponse()
        except httplib.BadStatusLine:
            self.conn.close()
            raise
        self.response_etag = self.response.getheader('etag')

        log.debug('RESPONSE STATUS: %d' % self.response.status)
        # Redirect redirect to auth required for cli
        if self.response.status == 307:
            self.response.status = 401

        length = self.response.getheader('content-length')

        try:
            if self.response_file is None or not self._success():
                self._response_data = self.response.read()
            else:
                stream_writer(self.response, self.response_file)
        except:
            self.conn.close()
            raise

        # Close connection here if the server can't handle connection reuse
        if self.conninfo.must_close():
            self.conn.close()

        if not self._success():
            log.debug('Server replied: %d %s' % (self._status(), self._reason()))

        if self._response_data and length != '0':
            try:
                self.response_obj = json.loads(self._response_data.decode())
            except ValueError as e:
                if self._response_data:
                    raise APIException('Error loading data: %s' % str(e))
            else:
                log.debug('RESPONSE:')
                log.debug(self.response.msg)
                if self.response_obj is not None:
                    log.debug(self.response_obj)

        if not self._success():
            json_error = cast(Dict[str, object], self.response_obj)
            raise RequestError(self._status(), self._reason(), json_error)

    def _status(self) -> int:
        assert self.response
        return self.response.status

    def _success(self) -> bool:
        return self._status() >= 200 and self._status() < 300

    def _reason(self) -> str:
        assert self.response
        return self.response.reason


#  ____
# |  _ \ ___  ___ _ __   ___  _ __  ___  ___
# | |_) / _ \/ __| '_ \ / _ \| '_ \/ __|/ _ \
# |  _ <  __/\__ \ |_) | (_) | | | \__ \  __/
# |_| \_\___||___/ .__/ \___/|_| |_|___/\___|
#                |_|


class RestResponse(NamedTuple):
    data: Any
    etag: Optional[str]

    def __str__(self) -> str:
        return pretty_json(self.data)

    def lookup(self, key: str) -> object:
        if self.data is not None and key in self.data:
            return self.data[key]
        else:
            raise AttributeError(key)


def rest_request(
    conninfo: Connection,
    credentials: Optional[Credentials],
    method: str,
    uri: str,
    body: Union[Sequence[object], Mapping[str, object]] = None,
    body_file: Optional[IO[AnyStr]] = None,
    if_match: Optional[str] = None,
    request_content_type: str = CONTENT_TYPE_JSON,
    response_file: IO[bytes] = None,
    headers: Mapping[str, str] = None,
) -> RestResponse:
    rest = APIRequest(
        conninfo=conninfo,
        credentials=credentials,
        method=method,
        uri=uri,
        body=body,
        body_file=body_file,
        if_match=if_match,
        request_content_type=request_content_type,
        response_file=response_file,
        headers=headers,
    )
    rest.send_request()
    rest.get_response()
    return RestResponse(rest.response_obj, rest.response_etag)


#  ____             _
# |  _ \ __ _  __ _(_)_ __   __ _
# | |_) / _` |/ _` | | '_ \ / _` |
# |  __/ (_| | (_| | | | | | (_| |
# |_|   \__,_|\__, |_|_| |_|\__, |
#             |___/         |___/
#


class PagingIterator:
    def __init__(
        self,
        initial_url: str,
        fn: Callable[[UriBuilder], RestResponse],
        page_size: Optional[int] = None,
    ):
        self.initial_url = initial_url
        self.rest_request = fn
        self.page_size = page_size

        self.uri = UriBuilder(path=initial_url, rstrip_slash=False)
        if page_size is not None:
            self.uri.add_query_param('limit', page_size)

    def __iter__(self) -> Iterator[RestResponse]:
        return self

    def __next__(self) -> RestResponse:
        if self.uri == '' or self.uri == None:
            raise StopIteration
        result = self.rest_request(self.uri)
        self.uri = result.data['paging']['next']

        return result
