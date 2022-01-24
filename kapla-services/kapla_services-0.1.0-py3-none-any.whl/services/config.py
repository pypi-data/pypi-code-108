import ssl
from typing import Awaitable, Callable, List, Literal, Optional, Tuple, Union
from urllib.parse import urlparse

from pydantic import BaseModel

from . import defaults

BROKER_PROTOCOL = Literal["nats", "mqtt", "memory", "redis"]


class BrokerConfig(BaseModel):
    # Broker protocol
    protocol: BROKER_PROTOCOL
    # Server location
    servers: List[str]
    # Broker name
    name: Optional[str] = None
    # TLS Context
    tls: Optional[ssl.SSLContext] = None
    tls_hostname: Optional[str] = None
    # Authentication
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    credentials: Optional[str] = None
    # Various callbacks
    disconnected_cb: Optional[Callable[[], Awaitable[None]]] = None
    closed_cb: Optional[Callable[[], Awaitable[None]]] = None
    reconnected_cb: Optional[Callable[[], Awaitable[None]]] = None
    # Reconnect strategy
    ping_interval: int = defaults.PING_INTERVAL
    max_outstanding_pings: int = defaults.MAX_OUTSTANDING_PINGS
    allow_reconnect: bool = defaults.ALLOW_RECONNECT
    max_reconnect_attempts: int = defaults.MAX_RECONNECT_ATTEMPS
    # Timeouts
    connect_timeout: int = defaults.CONNECT_TIMEOUT
    reconnect_timeout: int = defaults.RECONNECT_TIMEOUT
    drain_timeout: int = defaults.DRAIN_TIMEOUT
    # Flusher queue configuration
    flusher_queue_size: int = defaults.FLUSHER_QUEUE_SIZE

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"


def get_server_and_protocol(
    servers: Union[str, List[str], None] = None,
    /,
    host: Optional[str] = None,
    port: Optional[int] = None,
    protocol: Optional[BROKER_PROTOCOL] = None,
) -> Tuple[BROKER_PROTOCOL, List[str]]:
    _protocol: BROKER_PROTOCOL = ...  # type: ignore[assignment]
    _servers: List[str] = []

    # Build a server URL when none was provided
    if servers is None:
        # Use localhost by default
        if host is None:
            host = defaults.HOST
        # Use "nats" protocol by default
        if protocol is None:
            # Use "nats" protocol by default
            _protocol = defaults.PROTOCOL  # type: ignore[assignment]
        else:
            _protocol = protocol
        # Use default port according to protocol
        if port is None:
            port = defaults.PORTS[_protocol]
        # Create server URL
        server = f"{_protocol}://{host}:{port}"
        # Store the list of servers
        servers = [server]
        # Convert single server to a list of servers
    elif isinstance(servers, str):
        servers = [servers]

    # Iterate on each server
    for server in servers:
        # Parse server URL
        server_url = urlparse(server)
        # Check if protocol indicates TLS (using a '+' character)
        if "+" in server_url.scheme:
            # Fetch protocol
            server_protocol, server_transport = server_url.scheme.split("+")
            # Remove protocol from server URL
            server = server_url.geturl().replace(server_url.scheme, server_transport)
        else:
            server_protocol = server_url.scheme
        # On first server only
        if _protocol is ...:
            _protocol = server_protocol  # type: ignore[assignment]
        # Make sure all servers have the same protocol
        elif _protocol != server_protocol:
            raise ValueError("All servers must connect using the same protocol")
        else:
            _protocol = server_url.scheme  # type: ignore[assignment]
        # Append server URL to list of servers
        _servers.append(server)
    # Return protocol and servers
    return _protocol, _servers
