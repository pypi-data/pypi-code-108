"""
A backend-agnostic broker implementation.

This module provides the class `Broker` which implements the following methods:

  - connect: Connect the broker backend
  - disconnect: Disconnect the broker backend
  - close: Close the broker backend connection. This methods discards pending messages.
  - drain: Drain the broker backend connection. This methods stops all interests in all subscriptions, then wait for pending messages to be processed, and finally close the connection.
  - flush: Empty the publish pending buffer.
  - publish: Publish a message
  - request: Publish a message and expect a response
  - subscribe: Subscribe to incoming messages
  - subscribe_and_reply: Subscribe to incoming messages and reply to senders

It also provides the `__aenter__` and `__aexit__` methods in order to act as an asynchronous context manager.

NOTES:
  - In order to be efficient, publish does not always lead to a network operation, and published data might be sent to
    a pending buffer instead of TCP socket directly. If one wants to make sure that a calls to `publish` always leads
    to sending a message on the network, call the `flush` method right after.

  - Closing the connection discards all pending messages. In most cases, the `drain` method should be preferred to ensure that
    all pending messages are processed before closing a connection
"""
from __future__ import annotations

import asyncio
from types import TracebackType
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
    overload,
)

from anyio import move_on_after
from pydantic import ValidationError

from .errors import ConnectionClosedError, TimeoutError
from .io import dumps
from .listeners import Listener
from .protocol import BrokerProtocol, SubscriptionProtocol
from .requests import HeaderTypes, Request
from .responses import Response
from .senders import Sender
from .validation import validate

T = TypeVar("T")


class Broker:
    """A class for Message Brokers implementing Publish/Subscribe and Request/Reply patterns."""

    def __init__(
        self,
        backend: BrokerProtocol,
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
    ) -> None:
        """Create a new instance of Broker.

        A backend instance must be provided as first argument.
        """
        # Store the packend as a public property. The API design is still fresh, we might need to access the
        # backend for uses cases we did not consider yet.
        self.backend = backend
        # Store the middleware stack
        self.subscribe_middlewares = subscribe_middlewares
        self.send_middlewares = send_middlewares
        # Store attributes
        self.default_concurrency = default_concurrency
        self.default_pending_bytes_limit = default_pending_bytes_limit
        self.default_pending_requests_limit = default_pending_requests_limit
        self.default_drop_headers = default_drop_headers
        self.default_status_code = default_status_code
        self.default_error_handlers = default_error_handlers
        # Let's create a sender
        self.sender = Sender(
            publish=self.backend.publish,
            request=self.backend.request,
            middlewares=self.send_middlewares,
            broker=self,
        )
        # Let's create a listener. Listener is separated from Sender because they do not share the same middleware stack.
        # But they do share the same NATS client.
        # Note that a Listener requires a `publish` function to be given as second positional argument.
        # This function is required in order to let subscription callbacks reply to senders.
        # Also note that the publish method from the backend instance is used instead of the sender instance.
        # It means that messages published by the Listener won't visit the `send` middleware stack, I.E, messages published
        # as responsed within callbacks won't visit the middleware stack.
        self.listener = Listener(
            subscribe=self.backend.subscribe,
            publish=self.backend.publish,
            middlewares=self.subscribe_middlewares,
            default_concurrency=self.default_concurrency,
            default_pending_bytes_limit=self.default_pending_bytes_limit,
            default_pending_requests_limit=self.default_pending_requests_limit,
            default_drop_headers=self.default_drop_headers,
            default_status_code=self.default_status_code,
            default_error_handlers=self.default_error_handlers,
            broker=self,
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
        **kwargs: Any,
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
        **kwargs: Any,
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
        **kwargs: Any,
    ) -> Response[Any]:
        """Publish a message and expect a response. Optionally a validator can be used to validate received data.

        When a validator is used, request data will be of "validator" type.
        When no validator is used (I.E, validator is None), request data will be of "bytes" type.
        """
        did_timeout = False
        # Use a timeout for the whole request
        with move_on_after(timeout) as scope:
            try:
                response = await self.sender.request(
                    subject,
                    payload,
                    headers=headers,
                    timeout=timeout,
                    process_timeout=process_timeout,
                    **kwargs,
                )
            except asyncio.TimeoutError:
                # Too hard to reproduce using tests...
                did_timeout = True  # pragma: no cover

        # If timeout was reached
        if scope.cancel_called or did_timeout:
            # Generate an error message
            msg = f"Subscription did not reply before {timeout:.3f}s"
            # Return a Failure
            return Response(
                success=False,
                exception=TimeoutError(msg),
                code=504,
                error="RequestTimeoutError",
                details=msg,
            )

        # If success is True and validator is defined, then parse/validate the response data
        if response.success and validator:
            try:
                return response.copy(
                    update={"data": validate(validator, response.data)}
                )

            except ValidationError as err:
                return Response(
                    success=False,
                    exception=err,
                    code=417,
                    error="ValidationError",
                    details=dumps(err.errors()),
                    # Still send data which failed validation
                    data=response.data,
                )

        return response

    async def publish(
        self,
        subject: str,
        payload: Optional[Any] = None,
        reply: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        process_timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Publish a message without expecting a response.

        Payload can be of any type and will be converted to "bytes" type if necessary.
        """
        # Use a timeout even for publish, pending buffer might be full
        with move_on_after(timeout) as scope:
            # Publish using the sender
            # Do not propagate timeout to backends
            await self.sender.publish(
                subject,
                payload,
                reply,
                headers,
                process_timeout=process_timeout,
                **kwargs,
            )
        # Raise an error if publish did not happen
        if scope.cancel_called:
            raise TimeoutError(f"Publish did not complete before {timeout:.3f}s")

    async def subscribe(
        self,
        subject: str,
        cb: Callable[..., Awaitable[Any]],
        middlewares: List[Callable[..., Any]] = [],
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
        ] = {},
        **kwargs: Any,
    ) -> SubscriptionProtocol:
        """Subscribe to a subject using given callback.

        The callback arguments and return type must be annotated. Arguments type can be:
            * `Request`: The request instance will be injected as argument value
            * `Subject`: The request subject will be injected as argument value
            * `Reply`: The request reply subject will be injected as argument value
            * `Headers`: The requests headers will be injected as argument value
            * Any other type, in this case request data will be validated into argument type and injected as argument value

        If argument default value is `Header(key)` where key is a string, then argument value will be either `None` if header is not
        found in the request headers, or the validated header value (validation is performed according to header type).

        Consider the following callback as an example:

            >>> async def cb(request: Request, subject: Subject, reply: Reply, headers: Headers, user: str = Header("x-user-name")) -> None:
            >>>     ...

        """
        return await self.listener.subscribe(
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

    async def subscribe_and_reply(
        self,
        subject: str,
        cb: Callable[..., Any],
        middlewares: List[Callable[..., Any]] = [],
        queue: Optional[str] = ...,  # type: ignore[assignment]
        max_msgs: Optional[int] = None,
        concurrent_requests_limit: int = ...,  # type: ignore[assignment]
        pending_bytes_limit: int = ...,  # type: ignore[assignment]
        pending_requests_limit: int = ...,  # type: ignore[assignment]
        status_code: int = 200,
        details: Optional[str] = None,
        drop_headers: Iterable[str] = [],
        error_handlers: Dict[
            Type[Exception], Callable[[Exception, Request], Awaitable[Any]]
        ] = {},
    ) -> SubscriptionProtocol:
        """Subscribe to a subject using given callback. The callback return value is used to return a response to the sender."""
        return await self.listener.subscribe_and_reply(
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
        )

    async def connect(self, **kwargs: Any) -> None:
        """Open connection to the broker backend"""
        await self.backend.connect(**kwargs)

    async def close(self, **kwargs: Any) -> None:
        """Close connection to the broker backend.

        Closing a connection causes pending messages to be lost.
        """
        await self.backend.close(**kwargs)

    async def drain(self, **kwargs: Any) -> None:
        """Drain connection to the broker backend.

        Draining is similar to closing connection, but will wait
        for pending messages to be processed.
        """
        # Give a chance to asyncio to switch context
        await asyncio.sleep(0)
        await self.backend.drain(**kwargs)

    async def flush(self, **kwargs: Any) -> None:
        """Flush publish pending buffer.

        In order to be efficient, publish does not always lead to a network operation,
        and published data might be sent to a pending buffer instead of TCP socket directly.

        This method (flush) can be used in order to empty the pending buffer.
        """
        await self.backend.flush(**kwargs)

    async def __aenter__(self) -> Broker:
        """Open connection to the backend when entering the context manager."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Drain connection when exiting context manager. This way messages will be processed."""
        try:
            await self.drain()
        except ConnectionClosedError:
            pass

    @property
    def is_connected(self) -> bool:
        """Return True if broker backend is connected else False"""
        return self.backend.is_connected

    @property
    def is_reconnecting(self) -> bool:
        """Return True if broker backend is connected else False"""
        return self.backend.is_reconnecting


__all__ = ["Broker"]
