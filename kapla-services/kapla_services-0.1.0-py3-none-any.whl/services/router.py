from __future__ import annotations

import asyncio
from functools import partial
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    overload,
)

from anyio import ExceptionGroup, create_task_group, move_on_after
from loguru import logger

from . import defaults
from .broker import Broker
from .errors import RouterNotStartedError, RouterStoppedError, TimeoutError
from .protocol import SubscriptionProtocol
from .requests import HeaderTypes, Request
from .responses import Response

T = TypeVar("T", bound=Callable[..., Any])


class SubscriptionSpec(TypedDict):
    subject: str
    cb: Callable[..., Awaitable[Any]]
    middlewares: List[Callable[..., Any]]
    queue: Optional[str]
    max_msgs: Optional[int]
    concurrent_requests_limit: int
    pending_bytes_limit: int
    pending_requests_limit: int
    error_handlers: Dict[
        Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
    ]


class ReplySubscriptionSpec(SubscriptionSpec):
    status_code: int
    details: Optional[str]
    drop_headers: Iterable[str]


class BaseBrokerRouter:
    """A class used to dispatch incoming messages to several subscriptions

    A router can define a queue group which will be applied to all subscriptions.

    A router needs to me mounted into an application in order to be started
    """

    def __init__(
        self,
        base_subject: Optional[str] = None,
        queue_group: Optional[str] = None,
        subscribe_middlewares: List[Callable[..., Awaitable[Any]]] = [],
        send_middlewares: List[Callable[..., Awaitable[Any]]] = [],
        default_error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Any]
        ] = {},
        default_concurrency: int = defaults.CONCURRENT_REQUESTS_LIMIT,
        default_pending_bytes_limit: int = defaults.PENDING_BYTES_LIMIT,
        default_pending_requests_limit: int = defaults.PENDING_REQUESTS_LIMIT,
        default_drop_headers: Iterable[str] = [],
        default_status_code: int = 200,
    ) -> None:
        """Create a new instance of router"""
        # Initialize private attributes
        self.__broker__: Broker = None  # type: ignore[assignment]
        self.__subscriptions__: Dict[int, SubscriptionProtocol] = {}
        self.__tasks__: Dict[str, asyncio.Task[Any]] = {}
        # Initialize public attributes
        self.subscriptions: List[SubscriptionSpec] = []
        self.reply_suscriptions: List[ReplySubscriptionSpec] = []
        self.tasks: Dict[str, Callable[[], Awaitable[None]]] = {}
        self.started = False
        self.stopped = False
        self.base_subject = base_subject or ""
        self.queue_group = queue_group
        self.default_concurrency = default_concurrency
        self.default_pending_bytes_limit = default_pending_bytes_limit
        self.default_pending_requests_limit = default_pending_requests_limit
        self.default_error_handlers = default_error_handlers
        self.default_drop_headers = default_drop_headers
        self.default_status_code = default_status_code
        self.send_middlewares = send_middlewares or []
        self.subscribe_middlewares = subscribe_middlewares or []

    @property
    def broker(self) -> Broker:
        """Get the Broker client the router is attached to"""
        if self.__broker__:
            return self.__broker__
        raise RouterNotStartedError(
            "Router has not been attached to an application yet"
        )

    @staticmethod
    def _get_subject(base_subject: Optional[str], subject: str) -> str:
        if not base_subject:
            return subject
        if base_subject[-1] == ".":
            base_subject = base_subject[:-1]
        if not subject:
            return base_subject
        if subject[0] == ".":
            subject = subject[1:]
        return ".".join([base_subject, subject])

    def _subscribe(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Any]],
        queue: Optional[str],
        max_msgs: Optional[int],
        concurrent_requests_limit: int,
        pending_requests_limit: int,
        pending_bytes_limit: int,
        error_handlers: Dict[Type[Exception], Callable[[Exception, Request], Any]] = {},
    ) -> None:
        # Define subscription spec
        subscription: SubscriptionSpec = dict(
            # Subject must be provided
            subject=self._get_subject(self.base_subject, subject),
            # Callback must be provided
            cb=cb,
            # Queue
            queue=queue if queue is not ... else self.queue_group,
            # Middlewares
            middlewares=middlewares
            if middlewares is not ...
            else self.subscribe_middlewares,
            # Unsubscribe after max msgs (0 disables the auto-unsubscribe)
            max_msgs=max_msgs or 0,
            # Concurrency
            concurrent_requests_limit=concurrent_requests_limit
            if concurrent_requests_limit is not ...
            else self.default_concurrency,
            # Pending bytes
            pending_bytes_limit=pending_bytes_limit
            if pending_bytes_limit is not ...
            else self.default_pending_bytes_limit,
            # Pending requests
            pending_requests_limit=pending_requests_limit
            if pending_requests_limit is not ...
            else self.default_pending_requests_limit,
            # Error handlers
            error_handlers={**self.default_error_handlers, **error_handlers},
        )
        # Append the subscription
        self.subscriptions.append(subscription)
        # Start subscription if router is already started
        if self.started:
            # We must create a coroutine first and then submit it
            # using asyncio.create_task because parent function is not async
            async def _start() -> None:
                sub = await self.broker.subscribe(**subscription)
                self.__subscriptions__[sub.id] = sub

            asyncio.create_task(_start())

    def _subscribe_and_reply(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Any]],
        queue: Optional[str],
        max_msgs: Optional[int],
        concurrent_requests_limit: int,
        pending_requests_limit: int,
        pending_bytes_limit: int,
        status_code: int,
        details: Optional[str],
        drop_headers: Iterable[str],
        error_handlers: Dict[Type[Exception], Callable[[Exception, Request], Any]],
    ) -> None:
        # Define subscription spec
        subscription: ReplySubscriptionSpec = dict(
            # Subject must be provided
            subject=self._get_subject(self.base_subject, subject),
            # Callback must be provided
            cb=cb,
            # Queue
            queue=queue if queue is not ... else self.queue_group,
            # Middlewares
            middlewares=middlewares
            if middlewares is not ...
            else self.subscribe_middlewares,
            # Unsubscribe after max msgs (0 disables the auto-unsubscribe)
            max_msgs=max_msgs or 0,
            # Concurrency
            concurrent_requests_limit=concurrent_requests_limit
            if concurrent_requests_limit is not ...
            else self.default_concurrency,
            # Pending bytes
            pending_bytes_limit=pending_bytes_limit
            if pending_bytes_limit is not ...
            else self.default_pending_bytes_limit,
            # Pending requests
            pending_requests_limit=pending_requests_limit
            if pending_requests_limit is not ...
            else self.default_pending_requests_limit,
            # Reply configuration
            status_code=status_code
            if status_code is not ...
            else self.default_status_code,
            drop_headers=drop_headers
            if drop_headers is not ...
            else self.default_drop_headers,
            details=details,
            # Error handlers
            error_handlers={**self.default_error_handlers, **error_handlers},
        )
        # Append the subscription
        self.reply_suscriptions.append(subscription)
        # Start subscription if router is already started
        if self.started:
            # We must create a coroutine first and then submit it
            # using asyncio.create_task because parent function is not async
            async def _start() -> None:
                sub = await self.broker.subscribe_and_reply(**subscription)
                self.__subscriptions__[sub.id] = sub

            asyncio.create_task(_start())

    def add_subscription(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Awaitable[Any]]] = ...,  # type: ignore[assignment]
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
        ] = {},
    ) -> None:
        """Declare a subscription to an NATS subject using a coroutine as callback.

        The subscrpition won't be started until Router.start() method is called.
        """
        if self.stopped:
            raise RouterStoppedError("Cannot add subscription on stopped router")
        self._subscribe(
            subject,
            cb,
            queue=queue,
            middlewares=middlewares,
            max_msgs=max_msgs,
            concurrent_requests_limit=concurrent_requests_limit,
            pending_bytes_limit=pending_bytes_limit,
            pending_requests_limit=pending_requests_limit,
            error_handlers={**self.default_error_handlers, **error_handlers},
        )

    def add_reply_subscription(
        self,
        subject: str,
        cb: Callable[..., Any],
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
    ) -> None:
        if self.stopped:
            raise RouterStoppedError("Cannot add subscription on stopped router")
        self._subscribe_and_reply(
            subject,
            cb,
            queue=queue,
            middlewares=middlewares,
            max_msgs=max_msgs,
            concurrent_requests_limit=concurrent_requests_limit,
            pending_bytes_limit=pending_bytes_limit,
            pending_requests_limit=pending_requests_limit,
            status_code=status_code,
            drop_headers=drop_headers,
            details=details,
            error_handlers={**self.default_error_handlers, **error_handlers},
        )

    def add_task(
        self,
        name: str,
        coro: Callable[[], Awaitable[None]],
    ) -> None:
        if self.stopped:
            raise RouterStoppedError("Cannot register task on stopped router")
        self.tasks[name] = coro
        if self.started:
            self.__tasks__[name] = asyncio.create_task(coro(), name=name)

    def run_in_executor(
        self,
        function: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> Awaitable[T]:
        func = partial(function, *args, **kwargs)
        return asyncio.get_running_loop().run_in_executor(None, func)

    async def drain(self, timeout: Optional[float] = 30) -> None:
        self.stopped = True

        async def cancel_task(task: asyncio.Task[Any]) -> None:
            try:
                # First cancel then wait
                task.cancel()
                # Do not use timeout here
                # This coroutine will be cancelled by the parent scope
                await asyncio.wait_for(task, None)
            finally:
                self.__tasks__.pop(task.get_name(), None)

        async def cancel_sub(sub: SubscriptionProtocol) -> None:
            try:
                # Do not use timeout here
                # This coroutine will be cancelled by the parent scope
                await asyncio.wait_for(sub.drain(), None)
            finally:
                self.__subscriptions__.pop(sub.id, None)

        with move_on_after(timeout) as scope:
            async with create_task_group() as tg:
                for task in self.__tasks__.values():
                    tg.start_soon(cancel_task, task)
                for sub in self.__subscriptions__.values():
                    tg.start_soon(cancel_sub, sub)

        if scope.cancel_called:
            raise TimeoutError(
                f"Failed to drain router before timeout (timeout={timeout})"
            )

    async def stop(self, timeout: Optional[float] = 10) -> None:
        """Stop all subscriptions. This is an alias to self.drain()."""
        await self.drain(timeout)

    async def start(self, broker: Broker) -> None:
        """Start all subscriptions"""
        # This method can be run once only
        if self.started:
            return

        # Define a coroutine to start subscriptions
        async def start_sub(spec: SubscriptionSpec, reply: bool = False) -> None:
            # Create the subscription
            if reply:
                logger.debug(f"Starting reply subscription with options: {spec}")
                sub = await broker.subscribe_and_reply(**spec)
            else:
                logger.debug(f"Starting subscription with options: {spec}")
                sub = await broker.subscribe(**spec)
            # Store the subscription
            self.__subscriptions__[sub.id] = sub

        # Use a try/except block to start the router
        try:
            # First kick off the tasks, it's really fast since we don't await
            for task_name, task in self.tasks.items():
                self.__tasks__[task_name] = asyncio.create_task(task())

            # Then kick off the subscriptions using a task group
            async with create_task_group() as tg:
                for spec in self.subscriptions:
                    tg.start_soon(start_sub, spec)
                for spec in self.reply_suscriptions:
                    tg.start_soon(start_sub, spec, True)
        # Make sure to unsubscribe and cancel all tasks in case of failure
        except (Exception, ExceptionGroup):
            # Cancel all tasks and subscriptions
            await self.drain()
            # Raise the error again
            raise

        # In case of success store the broker and set the started attribute
        self.__broker__ = broker
        self.started = True


CallbackT = TypeVar("CallbackT", bound=Callable[..., Awaitable[Any]])
TaskT = TypeVar("TaskT", bound=Callable[[], Awaitable[None]])


class BrokerRouter(BaseBrokerRouter):
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
        return await self.broker.publish(
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
        response: Response[Any] = await self.broker.request(
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
