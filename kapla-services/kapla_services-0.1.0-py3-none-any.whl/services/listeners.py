from __future__ import annotations

import asyncio
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
)

from .dependencies import get_subscribe_and_reply_cb, get_subscribe_cb
from .protocol import PublishProtocol, SubscribeProtocol, SubscriptionProtocol
from .requests import Request

if TYPE_CHECKING:  # pragma: no cover
    from .broker import Broker  # pragma: no cover


class Listener:

    semaphore: Optional[asyncio.Semaphore]

    def __init__(
        self,
        subscribe: SubscribeProtocol,
        publish: PublishProtocol,
        middlewares: List[Callable[..., Awaitable[Any]]] = [],
        default_concurrency: int = 1,
        default_pending_bytes_limit: int = 1024,
        default_pending_requests_limit: int = 0,
        default_drop_headers: Iterable[str] = [],
        default_status_code: int = 200,
        default_error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Any]
        ] = {},
        broker: Optional[Broker] = None,
    ) -> None:
        self._broker = broker
        self._subscribe = subscribe
        self._publish = publish
        self.middlewares = middlewares
        self.default_concurrency = default_concurrency
        self.default_pending_bytes_limit = default_pending_bytes_limit
        self.default_pending_requests_limit = default_pending_requests_limit
        self.default_drop_headers = default_drop_headers
        self.default_status_code = default_status_code
        self.default_error_handlers = default_error_handlers
        # Private attribute where subscriptions are stored
        self.__subscriptions__: Dict[int, SubscriptionProtocol] = {}

    async def subscribe(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Awaitable[Any]]] = [],
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        error_handlers: Dict[Type[Exception], Callable[[Exception, Request], Any]] = {},
        **kwargs: Any,
    ) -> SubscriptionProtocol:
        """Subscribe to a subject using a callback"""
        options = self.prepare_subscribe_cb(
            subject=subject,
            cb=cb,
            middlewares=middlewares,
            queue=queue,
            max_msgs=max_msgs,
            concurrent_requests_limit=concurrent_requests_limit,
            pending_bytes_limit=pending_bytes_limit,
            pending_requests_limit=pending_requests_limit,
            error_handlers=error_handlers,
            **kwargs,
        )

        return await self._subscribe(**options)

    async def subscribe_and_reply(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Awaitable[Any]]] = [],
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        status_code: int = 200,
        details: Optional[str] = None,
        drop_headers: Iterable[str] = [],
        error_handlers: Dict[Type[Exception], Callable[[Exception, Request], Any]] = {},
        **kwargs: Any,
    ) -> SubscriptionProtocol:
        """Subscribe to a subject using a callback"""
        options = self.prepare_subscribe_and_reply_cb(
            subject=subject,
            cb=cb,
            middlewares=middlewares,
            queue=queue,
            max_msgs=max_msgs,
            concurrent_requests_limit=concurrent_requests_limit,
            pending_bytes_limit=pending_bytes_limit,
            pending_requests_limit=pending_requests_limit,
            status_code=status_code,
            details=details,
            drop_headers=drop_headers,
            error_handlers=error_handlers,
            **kwargs,
        )

        return await self._subscribe(**options)

    def prepare_subscribe_cb(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Awaitable[Any]]] = [],
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        error_handlers: Dict[Type[Exception], Callable[[Exception, Request], Any]] = {},
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Subscribe to a subject using a callback"""
        error_handlers = {**self.default_error_handlers, **error_handlers}

        listener = get_subscribe_cb(
            cb,
            middlewares or self.middlewares,
            error_handlers=error_handlers,
            broker=self._broker,
        )

        options = self._get_subscribe_options(
            subject=subject,
            queue=queue,
            max_msgs=max_msgs,
            listener=listener,
            pending_bytes_limit=pending_bytes_limit,
            pending_requests_limit=pending_requests_limit,
            concurrent_requests_limit=concurrent_requests_limit,
            **kwargs,
        )

        return options

    def prepare_subscribe_and_reply_cb(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Awaitable[Any]]] = [],
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        status_code: int = 200,
        details: Optional[str] = None,
        drop_headers: Iterable[str] = [],
        error_handlers: Dict[Type[Exception], Callable[[Exception, Request], Any]] = {},
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Subscribe to a subject using a callback"""
        error_handlers = {**self.default_error_handlers, **error_handlers}

        listener = get_subscribe_and_reply_cb(
            self._publish,
            cb,
            middlewares=middlewares or self.middlewares,
            status_code=status_code,
            details=details,
            drop_headers=drop_headers,
            error_handlers=error_handlers,
            broker=self._broker,
        )

        options = self._get_subscribe_options(
            subject=subject,
            queue=queue,
            max_msgs=max_msgs,
            listener=listener,
            pending_bytes_limit=pending_bytes_limit,
            pending_requests_limit=pending_requests_limit,
            concurrent_requests_limit=concurrent_requests_limit,
            **kwargs,
        )

        return options

    def _get_subscribe_options(
        self,
        *,
        subject: str,
        listener: Callable[..., Awaitable[Any]],
        queue: Optional[str],
        max_msgs: Optional[int],
        concurrent_requests_limit: int,
        pending_bytes_limit: int,
        pending_requests_limit: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        options = dict(
            subject=subject,
            queue="" if queue is ... else queue or "",
            max_msgs=max_msgs if max_msgs else 0,
            cb=listener,
            pending_bytes_limit=self.default_pending_bytes_limit
            if pending_bytes_limit is ...
            else pending_bytes_limit,
            pending_requests_limit=self.default_pending_requests_limit
            if pending_requests_limit is ...
            else pending_requests_limit,
            concurrent_requests_limit=self.default_concurrency
            if concurrent_requests_limit is ...
            else concurrent_requests_limit,
            **kwargs,
        )

        return options
