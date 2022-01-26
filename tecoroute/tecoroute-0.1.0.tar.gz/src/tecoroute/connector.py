"""TecoRoute EPSNET connector.

Connector creates meaningful log messages down to the :const:`logging.DEBUG` level.

Please do not open more than one connector per second. If there are many requests for
the TecoRoute service at one time, it may stuck for all customers.

Example of :class:`Connector` operation:

.. code-block:: python

    from asyncio import gather, run
    from logging import INFO, basicConfig

    from tecoroute.connector import Connector

    basicConfig(level=INFO)


    async def handle_communication(connector):
        await connector.send(epsnet_request)
        epsnet_response = await connector.receive()
        connector.close()


    async def main():
        connector = Connector(username='BroukPytlik', password='ferda1', plc='AB_1234')
        await gather(connector.run(), handle_communication(connector))


    run(main())

Example of :class:`UdpConnector` operation:

.. code-block:: python

    from asyncio import run
    from logging import INFO, basicConfig

    from tecoroute.connector import UdpConnector

    basicConfig(level=INFO)


    async def main():
        connector = UdpConnector(username='BroukPytlik', password='ferda1',
                                 plc='AB_1234')
        await connector.run()


    run(main())
"""
from asyncio import (
    BaseTransport,
    CancelledError,
    DatagramProtocol,
    DatagramTransport,
    Future,
    Lock,
    Queue,
    Task,
    TimeoutError,
    create_task,
    gather,
    get_event_loop,
    wait,
    wait_for,
)
from hashlib import sha1
from random import randint
from time import time
from typing import Any, Callable, NoReturn, Optional, Tuple

from tornado.httpclient import HTTPRequest
from tornado.iostream import StreamClosedError

from ._http import HttpClient
from ._misc import (
    APPLICATION,
    HOST,
    LATENCY_COUNT,
    LATENCY_THRESHOLD,
    PORT_CONNECTOR,
    TECOROUTE_HOST,
    TECOROUTE_PORT,
    logger,
)

__all__ = [
    "BaseConnector",
    "Connector",
    "UdpConnector",
    "ConnectorError",
    "ConnectorUserError",
    "ConnectorPlcError",
    "ConnectorConnectionError",
    "ConnectorLatencyError",
]


class BaseConnector:
    """Base connector class. Not intended for direct use, use inherited classes.

    :param username: TecoRoute username.
    :param password: TecoRoute password.
    :param plc: PLC to connect.
    :param application: TecoRoute application name.
    :param tecoroute_host: TecoRoute service host.
    :param tecoroute_port: TecoRoute service port.
    :param latency_threshold: Maximum latency in seconds.
    :param latency_count: Maximum number of latency errors.
    :param name: Connector name.
    """

    def __init__(
        self,
        username: str,
        password: str,
        plc: str,
        application: str = APPLICATION,
        tecoroute_host: str = TECOROUTE_HOST,
        tecoroute_port: int = TECOROUTE_PORT,
        latency_threshold: float = LATENCY_THRESHOLD,
        latency_count: int = LATENCY_COUNT,
        name: str = "",
    ) -> None:
        self._username = username
        self._password = password
        self._plc = plc
        self._application = application
        self._tecoroute_host = tecoroute_host
        self._tecoroute_port = tecoroute_port
        self._latency_threshold = latency_threshold
        self._latency_count = latency_count
        self._name = name

        self._init_args = locals()
        self._http: Optional[HttpClient] = None
        self._http_time: Optional[float] = None
        self._http_time_start: Optional[float] = None
        self._http_latency: int = 0
        self._send_buffer: Queue[bytes] = Queue()
        self._lock_run = Lock()
        self._task_run: Optional[Task[None]] = None
        self._subtasks_cancel = False  # https://bugs.python.org/issue42130 workaround

        self._logger = logger.getChild(
            "connector" + (f"-{self._name}" if self._name else "")
        )

        self._logger.debug(f"Initialized {repr(self)}")

    def __del__(self) -> None:
        self.close()

    def __repr__(self) -> str:
        class_ = type(self).__name__
        params = (f"{k}={repr(v)}" for k, v in self._init_args.items() if k != "self")
        info = " ".join(params)
        return f"<{class_} {info}>"

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """Connector name."""
        return self._name

    @property
    def http_time(self) -> Optional[float]:
        """Last response time from TecoRoute service (latency) in seconds."""
        if self._http_time is None:
            return None
        return round(self._http_time, 3)

    def _encode(self, data: bytes) -> bytes:
        encoded = bytes((data[0],))
        for byte in data[1:]:
            encoded += bytes(((~byte & 0xFF) + encoded[-1] & 0xFF,))
        return encoded

    def _decode(self, data: bytes) -> bytes:
        decoded = bytes((data[0],))
        for i in range(1, len(data)):
            decoded += bytes((~(data[i] - data[i - 1]) & 0xFF,))
        return decoded

    def _secret(self, string: str) -> str:
        return self._encode(bytes((randint(0, 255),)) + string.encode()).hex().upper()

    async def _send(self, data: bytes) -> None:
        await self._send_buffer.put(data)

    def _send_nowait(self, data: bytes) -> None:
        self._send_buffer.put_nowait(data)

    def _received(self, data: bytes) -> None:
        raise NotImplementedError

    async def _sending(self) -> NoReturn:
        assert self._http
        while True:
            try:
                data = await wait_for(self._send_buffer.get(), 10)
                if self._subtasks_cancel:
                    raise CancelledError
            except TimeoutError:
                data = bytes()
                self._http_time = None
            await self._http.send_request(
                HTTPRequest("/DATA.BIN", body=self._encode(data) if data else data),
                headers_raw={"u-tcm": "U-TCM"},
            )
            self._http_time_start = time()
            self._logger.debug(f"Sent {len(data)} bytes to TecoRoute")

    async def _receiving(self) -> NoReturn:
        assert self._http
        while True:
            res = await self._http.receive_response()
            if self._http_time_start:
                self._http_time = time() - self._http_time_start
            self._received(self._decode(res.body))
            time_log = self.http_time if self.http_time is not None else "-"
            self._logger.debug(
                f"Received {len(res.body)} bytes from TecoRoute (time: {time_log})"
            )
            if self._http_time_start and self._http_time is not None:
                if self._http_time >= self._latency_threshold:
                    self._http_latency += 1
                    if self._http_latency >= self._latency_count:
                        latency_error = ConnectorLatencyError()
                        self._logger.warning(latency_error)
                        raise latency_error
                else:
                    self._http_latency = 0
                self._http_time_start = None

    async def _run(self) -> None:
        subtasks: Optional[Tuple[Task[NoReturn], Task[NoReturn]]] = None
        try:
            self._logger.info("Started")

            # Open HTTP connection to TecoRoute
            self._http = HttpClient(self._tecoroute_host, self._tecoroute_port)
            self._logger.debug("Connection to TecoRoute established")

            # Getting salt from TecoRoute
            res = await self._http.request(
                HTTPRequest("/INDEX.XML"),
                headers_raw={
                    "x-aplic": f"{self._application} tecoroute",
                    "s-tcm": "1",
                    "n-user": self._secret(self._username),
                },
            )
            res_text = res.body.decode()
            self._logger.debug("Acquired salt from TecoRoute")

            # Authenticate application and user to TecoRoute
            password_hash = (
                sha1((res_text[:8] + self._password).encode()).hexdigest().upper()
                + "\r\n"
            )
            res = await self._http.request(
                HTTPRequest("/IAM.TXT", method="PUT", body=password_hash)
            )
            res_text = res.body.decode()
            if "_" in res_text:
                user_error = ConnectorUserError(
                    self._username, self._password, self._application, res_text.rstrip()
                )
                raise user_error
            self._logger.debug("User authenticated to TecoRoute")

            # Authenticate PLC to TecoRoute
            plc_secret = self._secret(self._plc) + "\r\n"
            res = await self._http.request(
                HTTPRequest("/PLC.TXT", method="PUT", body=plc_secret)
            )
            res_text = res.body.decode()
            if res_text != plc_secret:
                plc_error = ConnectorPlcError(self._plc, res_text.rstrip())
                raise plc_error
            self._logger.debug("PLC authenticated to TecoRoute")

            # Run communication to both directions asynchronously
            subtasks = (create_task(self._sending()), create_task(self._receiving()))
            self._logger.info("Communication channel is running")
            await gather(*subtasks)
        except StreamClosedError:
            connection_error = ConnectorConnectionError()
            self._logger.warning(connection_error)
            raise connection_error from None
        except ConnectorError as e:
            self._logger.warning(e)
            raise
        except Exception as e:
            self._logger.error(e)
            raise
        finally:
            if subtasks:
                self._subtasks_cancel = True
                for task in subtasks:
                    task.cancel()
                await wait(subtasks)
                self._subtasks_cancel = False
            if self._http:
                self._http.close()
                self._http = None
            self._http_time = None
            self._http_time_start = None
            self._http_latency = 0
            self._logger.info("Closed")

    async def run(self) -> None:
        """Run connector."""
        async with self._lock_run:
            if self._task_run:
                self._task_run.cancel()
                await wait((self._task_run,))
            self._task_run = create_task(self._run())
        try:
            await self._task_run
        finally:
            self._task_run = None

    @property
    def is_running(self) -> bool:
        """Return True if connector is running."""
        return bool(
            self._lock_run.locked() or self._task_run and not self._task_run.done()
        )

    def close(self) -> None:
        """Close the connector."""
        self._task_run and self._task_run.cancel()


class Connector(BaseConnector):
    """Connector that can be used to communicate with the PLC directly in code.

    The class in derived from :class:`BaseConnector`, shares all parent’s attributes and
    methods.

    All constructor's arguments are passed to :class:`BaseConnector`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._receive_buffer: Queue[bytes] = Queue()

    def _received(self, data: bytes) -> None:
        self._receive_buffer.put_nowait(data)

    def _check_running(self) -> None:
        if not self.is_running:
            raise RuntimeError("Connector is not open")

    async def receive(self) -> bytes:
        """Receive EPSNET message from the PLC.

        Coroutine awaits until the message is received. Raises :class:`RuntimeError` if
        the connector is not open.
        """
        self._check_running()
        return await self._receive_buffer.get()

    async def send(self, message: bytes) -> None:
        """Send EPSNET message to the PLC.

        :class:`RuntimeError` if connector is not open.
        """
        self._check_running()
        await self._send(message)


class _UdpConnectorProtocol(DatagramProtocol):
    def __init__(self, send_nowait_cb: Callable[[bytes], None]) -> None:
        self._send_nowait_cb = send_nowait_cb
        self._transport: Optional[DatagramTransport] = None
        self._address: Optional[Tuple[str, int]] = None
        self._wait_closed: Future[None] = Future()

    def connection_made(self, transport: BaseTransport) -> None:
        self._transport = transport  # type: ignore

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self._wait_closed.set_result(None)

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        self._send_nowait_cb(data)
        self._address = addr

    def datagram_send(self, data: bytes) -> None:
        if self._transport and self._address:
            self._transport.sendto(data, self._address)

    async def wait_closed(self) -> None:
        await self._wait_closed

    def close(self) -> None:
        if self._transport:
            try:
                self._transport.close()
            except RuntimeError:
                pass


class UdpConnector(BaseConnector):
    """Connector that opens the UDP port for EPSNET communication with the PLC.

    The connector on the UDP port accepts only one client, more precisely the connector
    responds to the address of the last request.

    The class in derived from :class:`BaseConnector`, shares all parent’s attributes and
    methods.

    :param host: Host to listen on.
    :param port: Port to listen on.

    All other constructor's arguments are passed to :class:`BaseConnector`.
    """

    def __init__(
        self, host: str = HOST, port: int = PORT_CONNECTOR, *args: Any, **kwargs: Any
    ) -> None:
        self._host = host
        self._port = port
        super().__init__(*args, **kwargs)
        self._udp: Optional[_UdpConnectorProtocol] = None

    def _received(self, data: bytes) -> None:
        assert self._udp
        self._udp.datagram_send(data)

    async def run(self) -> None:
        """:meta private:"""  # noqa: D400
        loop = get_event_loop()
        _, self._udp = await loop.create_datagram_endpoint(  # type: ignore
            lambda: _UdpConnectorProtocol(self._send_nowait),
            local_addr=(self._host, self._port),
        )
        assert self._udp
        try:
            await super().run()
        finally:
            self._udp.close()
            await self._udp.wait_closed()
            self._udp = None

    @property
    def is_running(self) -> bool:
        """:meta private:"""  # noqa: D400
        return bool(super().is_running or self._udp)


class ConnectorError(Exception):
    """ConnectorError()

    The base class for connector exceptions. Inherited from Exception.
    """  # noqa: D400

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConnectorUserError(ConnectorError):
    """ConnectorUserError()

    Unsuccessful authentication of the user to the
    TecoRoute service.
    """  # noqa: D400

    def __init__(
        self, username: str, password: str, application: str, error_code: str
    ) -> None:
        self._error_code = error_code
        super().__init__(
            (
                f"Can not authenticate user {repr(username)} with password "
                f"{repr(password)} to application {repr(application)}, error code "
                f"{self._error_code}"
            )
        )

    @property
    def error_code(self) -> str:
        """Error code from TecoRoute service."""
        return self._error_code


class ConnectorPlcError(ConnectorError):
    """ConnectorPlcError()

    Unsuccessful connection to the PLC.
    """  # noqa: D400

    def __init__(self, plc: str, error_code: str) -> None:
        self._error_code = error_code
        super().__init__(
            (f"Can not open PLC {repr(plc)}, error code {self._error_code}")
        )

    @property
    def error_code(self) -> str:
        """Error code from TecoRoute service."""
        return self._error_code


class ConnectorConnectionError(ConnectorError):
    """Connection error with the TecoRoute service."""

    def __init__(self) -> None:
        super().__init__("Connection with TecoRoute is closed")


class ConnectorLatencyError(ConnectorError):
    """High latency of the TecoRoute service."""

    def __init__(self) -> None:
        super().__init__(
            "Connection latency is too high, probably due to limitations of TecoRoute"
        )
