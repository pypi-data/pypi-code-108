"""
This module exposts two classes, Sender and Listener, which are used by the Broker class.
The idea to split the send operations and the listen operations comes from the fact that those operations cannot
share middlewares.
So instead of making a single class with a lot of complex functions, I prefered writing two distinct classes.
Still, the Broker class should be used by end users, and Sender or Listener should never be used directly.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, List, Optional, Protocol

from .dependencies import chain_middlewares
from .headers import HeaderTypes
from .middlewares.time import x_publish_time, x_request_time
from .protocol import PublishProtocol, RequestProtocol
from .requests import Request
from .responses import Response

if TYPE_CHECKING:  # pragma: no cover
    from .broker import Broker  # pragma: no cover


class SendRequestAPI(Protocol):
    """Request API exposed to end users"""

    async def __call__(
        self,
        subject: str,
        payload: Optional[Any] = None,
        headers: Optional[HeaderTypes] = None,
        timeout: float = 1.0,
        process_timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> Response[bytes]:
        ...  # pragma: no cover


class SendPublishAPI(Protocol):
    """Publish API exposed to end users"""

    async def __call__(
        self,
        subject: str,
        payload: Optional[Any] = None,
        reply: Optional[str] = None,
        headers: Optional[HeaderTypes] = None,
        **kwargs: Any,
    ) -> None:
        ...  # pragma: no cover


class Sender:
    """A class used to facilitate sending messages using middlewares"""

    def __init__(
        self,
        publish: PublishProtocol,
        request: RequestProtocol,
        middlewares: List[Callable[..., Awaitable[Optional[Response[Any]]]]] = [],
        broker: Optional[Broker] = None,
    ) -> None:
        """Create a new instance of sender.

        A sender can receive middlewares at init in the form of a list of coroutine functions.

        Those functions will be used to generate the `publish` and `request` methods.
        """
        # Store the broker
        self._broker = broker
        # Store the publish function implementing the publish protocol
        self._publish = publish
        # Store the coroutine function implementing the request protocol
        self._request = request
        # Store the middlewares
        self.middlewares: List[Callable[..., Awaitable[Optional[Response[Any]]]]] = [
            *middlewares,
            x_request_time,
            x_publish_time,
        ]
        # Generate the request method
        self.request = self._get_request_stack()
        # Generate the publish method
        self.publish = self._get_publish_stack()

    def _get_request_stack(self) -> SendRequestAPI:
        """Create a coroutine function which can be used to perform requests using middlewares."""
        request_pipe = chain_middlewares(self._request, self.middlewares)

        async def _request(
            subject: str,
            payload: Optional[Any] = None,
            headers: Optional[HeaderTypes] = None,
            timeout: float = 1.0,
            process_timeout: Optional[float] = None,
            **kwargs: Any,
        ) -> Response[bytes]:
            """Coroutine which performs the request"""
            # Build a request to send
            request = Request._from_request(
                subject,
                payload,
                headers=headers,
                timeout=timeout,
                process_timeout=process_timeout,
                **kwargs,
            )
            if self._broker:  # pragma: no cover
                # Inject the broker into the request scope
                request.scope["broker"] = self._broker
            # Get the response
            response: Response[bytes] = await request_pipe(request)
            # Return the response
            return response

        return _request

    def _get_publish_stack(self) -> SendPublishAPI:
        """Create a coroutine function which can be used to perform publish using middlewares."""
        publish_pipe = chain_middlewares(self._publish, self.middlewares)

        async def _publish(
            subject: str,
            payload: Optional[Any] = None,
            reply: Optional[str] = None,
            headers: Optional[HeaderTypes] = None,
            process_timeout: Optional[float] = None,
            **kwargs: Any,
        ) -> None:
            """Publish a message without expecting a response"""
            # Build the request
            request = Request._from_publish(
                subject,
                payload,
                reply=reply or "",
                headers=headers,
                process_timeout=process_timeout,
                **kwargs,
            )
            if self._broker:  # pragma: no cover
                request.scope["broker"] = self._broker
            # Publish the request
            await publish_pipe(request)

        return _publish
