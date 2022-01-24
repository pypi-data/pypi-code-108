import ssl
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Type, Union

from .broker import Broker
from .config import BROKER_PROTOCOL, BrokerConfig, get_server_and_protocol
from .errors import BackendNotFoundError
from .protocol import BrokerProtocol
from .requests import Request


def nats_factory() -> Type[BrokerProtocol]:
    try:
        from kapla.services.backends.nats import NATSBroker
    except ModuleNotFoundError:  # pragma: no cover
        raise RuntimeError(  # pragma: no cover
            "Package 'nats-py' must be installed in order to use NATSBroker. Please run 'python -m pip install nats-py'"
        )

    return NATSBroker


FACTORIES: Dict[BROKER_PROTOCOL, Callable[[], Type[BrokerProtocol]]] = {
    "nats": nats_factory,
}


def create_broker_from_config(
    config: BrokerConfig,
    subscribe_middlewares: List[Callable[..., Awaitable[Any]]] = [],
    send_middlewares: List[Callable[..., Awaitable[Any]]] = [],
    default_concurrency: int = 1,
    default_pending_bytes_limit: int = 1024,
    default_pending_requests_limit: int = 0,
    default_drop_headers: Iterable[str] = [],
    default_status_code: int = 200,
    default_error_handlers: Dict[
        Type[Exception], Callable[[Exception, Request], Any]
    ] = {},
) -> Broker:
    # Create backend
    try:
        backend = FACTORIES[config.protocol]()(config)
    except KeyError:
        raise BackendNotFoundError(
            f'No backend were found for protocol "{config.protocol}"'
        )
    # Create broker
    broker = Broker(
        backend,
        subscribe_middlewares=subscribe_middlewares,
        send_middlewares=send_middlewares,
        default_concurrency=default_concurrency,
        default_pending_bytes_limit=default_pending_bytes_limit,
        default_pending_requests_limit=default_pending_requests_limit,
        default_drop_headers=default_drop_headers,
        default_status_code=default_status_code,
        default_error_handlers=default_error_handlers,
    )
    # Return the broker
    return broker


def create_config(
    servers: Union[str, List[str], None] = None,
    *,
    name: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    protocol: Optional[BROKER_PROTOCOL] = None,
    tls: Optional[ssl.SSLContext] = None,
    tls_hostname: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    credentials: Optional[str] = None,
    disconnected_cb: Optional[Callable[[], Awaitable[None]]] = None,
    closed_cb: Optional[Callable[[], Awaitable[None]]] = None,
    reconnected_cb: Optional[Callable[[], Awaitable[None]]] = None,
    allow_reconnect: bool = True,
    connect_timeout: int = 2,
    reconnect_timeout: int = 2,
    drain_timeout: int = 30,
    max_reconnect_attempts: int = 60,
    ping_interval: int = 120,
    max_outstanding_pings: int = 120,
    flusher_queue_size: int = 1024,
    **kwargs: Any,
) -> BrokerConfig:
    _protocol, _servers = get_server_and_protocol(servers, host, port, protocol)

    return BrokerConfig(
        protocol=_protocol,
        servers=_servers,
        name=name,
        tls=tls,
        tls_hostname=tls_hostname,
        user=user,
        password=password,
        token=token,
        credentials=credentials,
        disconnected_cb=disconnected_cb,
        closed_cb=closed_cb,
        reconnected_cb=reconnected_cb,
        allow_reconnect=allow_reconnect,
        connect_timeout=connect_timeout,
        reconnect_timeout=reconnect_timeout,
        drain_timeout=drain_timeout,
        max_reconnect_attempts=max_reconnect_attempts,
        ping_interval=ping_interval,
        max_outstanding_pings=max_outstanding_pings,
        flusher_queue_size=flusher_queue_size,
        **kwargs,
    )


def create_broker(
    servers: Union[str, List[str], None] = None,
    *,
    name: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    protocol: Optional[BROKER_PROTOCOL] = None,
    tls: Optional[ssl.SSLContext] = None,
    tls_hostname: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    credentials: Optional[str] = None,
    disconnected_cb: Optional[Callable[[], Awaitable[None]]] = None,
    closed_cb: Optional[Callable[[], Awaitable[None]]] = None,
    reconnected_cb: Optional[Callable[[], Awaitable[None]]] = None,
    allow_reconnect: bool = True,
    connect_timeout: int = 2,
    reconnect_timeout: int = 2,
    drain_timeout: int = 30,
    max_reconnect_attempts: int = 60,
    ping_interval: int = 120,
    max_outstanding_pings: int = 120,
    flusher_queue_size: int = 1024,
    subscribe_middlewares: List[Callable[..., Awaitable[Any]]] = [],
    send_middlewares: List[Callable[..., Awaitable[Any]]] = [],
    default_concurrency: int = 1,
    default_pending_bytes_limit: int = 1024,
    default_pending_requests_limit: int = 0,
    default_drop_headers: Iterable[str] = [],
    default_status_code: int = 200,
    default_error_handlers: Dict[
        Type[Exception], Callable[[Exception, Request], Any]
    ] = {},
    **kwargs: Any,
) -> Broker:
    config = create_config(
        servers=servers,
        host=host,
        port=port,
        protocol=protocol,
        name=name,
        tls=tls,
        tls_hostname=tls_hostname,
        user=user,
        password=password,
        token=token,
        credentials=credentials,
        disconnected_cb=disconnected_cb,
        closed_cb=closed_cb,
        reconnected_cb=reconnected_cb,
        allow_reconnect=allow_reconnect,
        connect_timeout=connect_timeout,
        reconnect_timeout=reconnect_timeout,
        drain_timeout=drain_timeout,
        max_reconnect_attempts=max_reconnect_attempts,
        ping_interval=ping_interval,
        max_outstanding_pings=max_outstanding_pings,
        flusher_queue_size=flusher_queue_size,
        **kwargs,
    )
    # Create backend
    return create_broker_from_config(
        config,
        subscribe_middlewares=subscribe_middlewares,
        send_middlewares=send_middlewares,
        default_concurrency=default_concurrency,
        default_pending_bytes_limit=default_pending_bytes_limit,
        default_pending_requests_limit=default_pending_requests_limit,
        default_drop_headers=default_drop_headers,
        default_status_code=default_status_code,
        default_error_handlers=default_error_handlers,
    )
