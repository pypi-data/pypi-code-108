from typing import Any, Awaitable, Callable, Optional, Protocol

from .config import BrokerConfig
from .requests import Request
from .responses import Response


class SubscriptionProtocol(Protocol):
    """Subscription Protocol which must be implemented by all backends"""

    subject: str
    queue: str

    @property
    def id(self) -> int:
        ...  # pragma: no cover

    @property
    def pending_requests(self) -> int:
        """
        Number of delivered requests that are being buffered
        in the pending queue.
        """
        ...  # pragma: no cover

    @property
    def delivered(self) -> int:
        """Number of delivered requests to this subscription so far."""
        ...  # pragma: no cover

    async def unsubscribe(self, limit: int = 0) -> None:
        """Removes interest in a subject, remaining requests will be discarded."""
        ...  # pragma: no cover

    async def drain(self) -> None:
        """Removes interest in a subject, but will process remaining requests."""
        ...  # pragma: no cover


class SubscribeProtocol(Protocol):
    async def __call__(
        self,
        subject: str,
        cb: Callable[[Request], Awaitable[None]],
        queue: str = ...,
        max_msgs: Optional[int] = ...,
        pending_bytes_limit: int = ...,
        pending_requests_limit: int = ...,
        concurrent_requests_limit: int = ...,
    ) -> SubscriptionProtocol:
        """Subscribe signature which must be implemented by all backends"""

        ...  # pragma: no cover


class PublishProtocol(Protocol):
    async def __call__(
        self,
        request: Request,
    ) -> None:
        """Publish signature which must be implemented by all backends"""
        ...  # pragma: no cover


class RequestProtocol(Protocol):
    async def __call__(
        self,
        request: Request,
    ) -> Response[bytes]:
        """Request signature which must be implemented by all backends"""
        ...  # pragma: no cover


class BrokerProtocol(Protocol):
    """Protocol which must be implemented by all backends"""

    def __init__(self, config: BrokerConfig) -> None:
        ...  # pragma: no cover

    config: BrokerConfig

    subscribe: SubscribeProtocol
    publish: PublishProtocol
    request: RequestProtocol
    connect: Callable[..., Awaitable[None]]
    close: Callable[..., Awaitable[None]]
    drain: Callable[..., Awaitable[None]]
    flush: Callable[..., Awaitable[None]]

    @property
    def is_connected(self) -> bool:
        ...  # pragma: no cover

    @property
    def is_reconnecting(self) -> bool:
        ...  # pragma: no cover
