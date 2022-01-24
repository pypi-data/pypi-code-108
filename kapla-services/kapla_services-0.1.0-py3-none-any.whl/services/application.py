from __future__ import annotations

import asyncio
import ssl
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

from loguru import logger

from kapla.services.testing.client import TestClient

from .config import BROKER_PROTOCOL, BrokerConfig
from .factory import create_broker, create_broker_from_config
from .requests import HeaderTypes, Request, State
from .responses import Response
from .router import BrokerRouter

T = TypeVar("T", bound=Any)
CallbackT = TypeVar("CallbackT", bound=Callable[..., Awaitable[Any]])
TaskT = TypeVar("TaskT", bound=Callable[[], Awaitable[None]])


class BaseBrokerApp:
    def __init__(
        self,
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
    ) -> None:
        """Create a new application instance"""
        # Create a broker
        self.broker = create_broker(
            servers=servers,
            name=name,
            host=host,
            port=port,
            protocol=protocol,
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
            subscribe_middlewares=subscribe_middlewares,
            send_middlewares=send_middlewares,
            default_concurrency=default_concurrency,
            default_pending_bytes_limit=default_pending_bytes_limit,
            default_pending_requests_limit=default_pending_requests_limit,
            default_drop_headers=default_drop_headers,
            default_status_code=default_status_code,
            default_error_handlers=default_error_handlers,
            **kwargs,
        )
        # Create a list of routers
        self.routers: List[BrokerRouter] = []
        # Create a default router
        self._default_router = BrokerRouter(
            subscribe_middlewares=subscribe_middlewares,
            send_middlewares=send_middlewares,
            default_concurrency=default_concurrency,
            default_pending_bytes_limit=default_pending_bytes_limit,
            default_pending_requests_limit=default_pending_requests_limit,
            default_drop_headers=default_drop_headers,
            default_status_code=default_status_code,
            default_error_handlers=default_error_handlers,
        )
        # Include the default router
        self.include_router(self._default_router)
        # Create a state
        self.state = State()
        # Create a test client only when optimization is disabled
        if __debug__:  # pragma: no cover
            self.test_client = TestClient(self)

    async def start(self, **kwargs: Any) -> None:
        """Start the application

        All configuration can be provided as keyword arguments.

        See arguments supported by nats.aio.client.Client class.
        """
        if not self.broker.is_connected:
            await self.broker.connect(**kwargs)
        await asyncio.gather(*(router.start(self.broker) for router in self.routers))

    async def stop(self) -> None:
        """Stop the application"""
        await asyncio.gather(*(router.stop() for router in self.routers))
        if self.broker.is_connected or self.broker.is_reconnecting:
            await self.broker.drain()

    @property
    def add_subscription(self):  # type: ignore[no-untyped-def]
        return self._default_router.add_subscription

    @property
    def add_reply_subscription(self):  # type: ignore[no-untyped-def]
        return self._default_router.add_reply_subscription

    @property
    def add_task(self):  # type: ignore[no-untyped-def]
        return self._default_router.add_task

    def include_router(self, router: BrokerRouter) -> None:
        """Add a router to the application"""
        if router not in self.routers:
            self.routers.append(router)

    def include_app(self, app: BrokerApp) -> None:
        """Include all subscriptions from another application"""
        for router in app.routers:
            self.include_router(router)

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        """Start the application in the foreground. This will block the main thread."""
        try:
            logger.info("Creating a new event loop")
            loop = asyncio.get_event_loop_policy().new_event_loop()
            logger.info("Starting application")
            loop.run_until_complete(self.start(*args, **kwargs))
            try:
                logger.info("Application ready")
                loop.run_forever()
            finally:
                logger.info("Shutting down application")
                loop.run_until_complete(self.stop())
                loop.close()
                logger.info("Exiting...")
        except KeyboardInterrupt:
            return


class BrokerApp(BaseBrokerApp):
    async def publish(
        self,
        subject: str,
        payload: Optional[Any] = None,
        reply: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        process_timeout: Optional[float] = None,
    ) -> None:
        """Publish a message without expecting a response.

        Payload can be of any type and will be converted to "bytes" type if necessary.
        """
        return await self._default_router.publish(
            subject=subject,
            payload=payload,
            reply=reply,
            headers=headers,
            timeout=timeout,
            process_timeout=process_timeout,
        )

    @overload
    async def request(
        self,
        subject: str,
        payload: Optional[Any] = None,
        *,
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        validator: Type[T],
    ) -> Response[T]:
        ...  # pragma: no cover

    @overload
    async def request(
        self,
        subject: str,
        payload: Optional[Any] = None,
        *,
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        validator: None = None,
    ) -> Response[bytes]:
        ...  # pragma: no cover

    async def request(
        self,
        subject: str,
        payload: Optional[Any] = None,
        *,
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        validator: Optional[Type[Any]] = None,
    ) -> Response[Any]:
        """Publish a message and expect a response. Optionally a validator can be used to validate received data.

        When a validator is used, request data will be of "validator" type.
        When no validator is used (I.E, validator is None), request data will be of "bytes" type.
        """
        response: Response[Any] = await self._default_router.request(
            subject=subject,
            payload=payload,
            headers=headers,
            timeout=timeout,
            process_timeout=process_timeout,
            validator=validator,
        )
        return response

    def subscribe(
        self,
        subject: str,
        middlewares: List[Callable[..., Awaitable[Any]]] = ...,  # type: ignore[assignment]
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
        ] = {},
    ) -> Callable[[CallbackT], CallbackT]:
        """Decorate a function to be used as an NATS subscription callback."""

        def decorator(cb: CallbackT) -> CallbackT:
            # Create subscription
            self.add_subscription(
                subject,
                cb,
                queue=queue,
                max_msgs=max_msgs,
                middlewares=middlewares,
                concurrent_requests_limit=concurrent_requests_limit,
                pending_bytes_limit=pending_bytes_limit,
                pending_requests_limit=pending_requests_limit,
                error_handlers=error_handlers,
            )
            # Return original function
            return cb

        return decorator

    def subscribe_and_reply(
        self,
        subject: str,
        middlewares: List[Callable[..., Any]] = [],
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        status_code: int = ...,  # type: ignore[assignment]
        drop_headers: Iterable[str] = ...,  # type: ignore[assignment]
        details: Optional[str] = None,
        error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
        ] = {},
    ) -> Callable[[CallbackT], CallbackT]:
        """Decorate a function to be used as an NATS subscription callback."""

        def decorator(cb: CallbackT) -> CallbackT:
            # Create subscription
            self.add_reply_subscription(
                subject,
                cb,
                queue=queue,
                max_msgs=max_msgs,
                middlewares=middlewares,
                concurrent_requests_limit=concurrent_requests_limit,
                pending_bytes_limit=pending_bytes_limit,
                pending_requests_limit=pending_requests_limit,
                status_code=status_code,
                drop_headers=drop_headers,
                details=details,
                error_handlers=error_handlers,
            )
            # Return original function
            return cb

        return decorator

    def task(
        self,
        name: str,
    ) -> Callable[[TaskT], TaskT]:
        """Decorate a function to be used as an NATS subscription callback."""

        def decorator(coro: TaskT) -> TaskT:
            # Create subscription
            self.add_task(name=name, coro=coro)
            # Return original function
            return coro

        return decorator

    def run_in_executor(
        self,
        function: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> Awaitable[T]:
        return self._default_router.run_in_executor(function, *args, **kwargs)

    def update_config(
        self,
        *,
        config: BrokerConfig = ...,  # type: ignore[assignment]
        subscribe_middlewares: List[Callable[..., Awaitable[Any]]] = ...,  # type: ignore[assignment]
        send_middlewares: List[Callable[..., Awaitable[Any]]] = ...,  # type: ignore[assignment]
        default_concurrency: int = ...,  # type: ignore[assignment]
        default_pending_bytes_limit: int = ...,  # type: ignore[assignment]
        default_pending_requests_limit: int = ...,  # type: ignore[assignment]
        default_drop_headers: Iterable[str] = ...,  # type: ignore[assignment]
        default_status_code: int = ...,  # type: ignore[assignment]
        default_error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Any]
        ] = ...,  # type: ignore[assignment]
        **kwargs: Any,
    ) -> None:
        if self.broker.is_connected:
            raise RuntimeError("Cannot update config while broker is connected")

        def get_option(key: str, value: Any) -> Any:
            return value if value is not ... else getattr(self.broker, key)

        if config is not ...:
            new_config = self.broker.backend.config.copy(
                update=config.dict(exclude_unset=True), deep=True
            )
        else:
            new_config = self.broker.backend.config.copy()
        if kwargs:
            new_config = new_config.copy(
                update={
                    key: value
                    for key, value in kwargs.items()
                    if value not in (..., [...], {...}, (...))
                },
                deep=True,
            )
            logger.debug(f"Updated configuration: {new_config}")

        self.broker = create_broker_from_config(
            config=new_config,
            subscribe_middlewares=get_option(
                "subscribe_middlewares", subscribe_middlewares
            ),
            send_middlewares=get_option("send_middlewares", send_middlewares),
            default_concurrency=get_option("default_concurrency", default_concurrency),
            default_pending_bytes_limit=get_option(
                "default_pending_bytes_limit", default_pending_bytes_limit
            ),
            default_pending_requests_limit=get_option(
                "default_pending_requests_limit", default_pending_requests_limit
            ),
            default_drop_headers=get_option(
                "default_drop_headers", default_drop_headers
            ),
            default_status_code=get_option("default_status_code", default_status_code),
            default_error_handlers=get_option(
                "default_error_handlers", default_error_handlers
            ),
        )


__all__ = ["BrokerApp"]
