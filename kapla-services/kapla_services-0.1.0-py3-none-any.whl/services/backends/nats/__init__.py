import asyncio
from typing import Any, Awaitable, Callable, Optional, final

import nats.errors
from loguru import logger
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.aio.subscription import Subscription

from kapla.services.concurrency import TaskPool
from kapla.services.config import BrokerConfig
from kapla.services.errors import (
    ConnectionClosedError,
    ConnectionDrainingError,
    ConnectionNotStartedError,
    InvalidCallbackError,
    InvalidSubjectError,
    MaxPayloadError,
    NoServerError,
    SubscriptionNotStartedError,
    TimeoutError,
)
from kapla.services.protocol import BrokerProtocol, SubscriptionProtocol
from kapla.services.requests import Request, Subject
from kapla.services.responses import Response


def get_nats_cb(
    pool: TaskPool,
    cb: Callable[[Request], Awaitable[None]],
) -> Callable[[Msg], Awaitable[asyncio.Task[None]]]:
    """Wrap provided callback so that it can handle NATS messages.

    NATS executes each message sequentially. In order to introduce concurrency, a TaskPool instance
    is used to submit callback as an asyncio task.
    Concurrency limit is configured at the task pool level.
    """

    async def _cb(msg: Msg) -> asyncio.Task[None]:

        request = Request._from_subscribe(
            subject=msg.subject,
            reply=msg.reply,
            payload=msg.data,
            headers=msg.headers,
        )
        return await pool.create_task(cb(request))

    return _cb


class NATSBroker(BrokerProtocol):
    def __init__(self, config: BrokerConfig) -> None:
        """Create a new instance of NATSBroker"""
        self.config = config
        self._nats = NATS()

    @property
    def is_connected(self) -> bool:
        """Return True when client is connected to NATS server"""
        # mypy considers NATS as untyped...
        return self._nats.is_connected  # type: ignore[no-any-return]

    @property
    def is_reconnecting(self) -> bool:
        """Return True when client is reconnecting to NATS server"""
        # mypy considers NATS as untyped...
        return self._nats.is_reconnecting  # type: ignore[no-any-return]

    async def _reply_on_slow_consumer(
        self, exception: nats.errors.SlowConsumerError
    ) -> None:
        """Reply on request that are aborted due to SlowConsumerError"""
        # Generate a response
        response = Response[None](
            success=False,
            code=503,
            error="SlowConsumerError",
            details=f"Pending queue is full",
            request_origin=exception.subject,
        )
        # Transform the response into a request
        request = response.to_request("reply", subject=exception.reply)
        # Publish the request
        await self.publish(request)

    async def default_error_cb(self, error: Exception) -> None:
        """NATS is kinda messy when it comes to error handling.

        Errors are raised within a coroutine running as an asyncio.Task,
        so they cannot be catched directly.

        Those errors can be raised from different places though:
          - When calling `nats.connect()`, a `while True:` loop is used to performed the connection.
            In this loop, some exceptions are catched and used as argument to execute the error_callback.

        The following exceptions can be received by the error callback:

        * OSError: raised during a call to `connect()` or `_attempt_reconnect` method

        * nats.errors.Error: raised during a call to `connect()` `_attempt_reconnect` method

        * asyncio.TimeoutError: raised during a call to `connect()` `_attempt_reconnect` method

        * Any exception raised by `asyncio.StreamWriter.wait_closed()` during a call to `_close()` method

        * Any exception raised by `asyncio.StreamWriter.wait_closed()` during a call to `_attempt_reconnect()` method

        * DrainTimeout: raised during a call to `drain()` method (WARNING: A class is received and not an instance, this is bothersome)

        * Any exception raised by `asyncio.open_connection()` during a call to `_select_next_server()` method (this method itself is used in `connect()` and `attempt_reconnect()`)

        * Any exception raised while trying to parse headers during a call to `_process_msg()` method

        * Any exception raised while processing a message

        * SlowConsumerError raised during a call to `_process_msg()` method

        * OSError raised during a call to `_flusher()` method

        * StaleConnectionError raised during a call to `_read_loop()` method

        Honestly, I don't know how we can handle everything neatly...
        """
        # Reply on SlowConsumerError
        if isinstance(error, nats.errors.SlowConsumerError):
            sub: Subscription = error.sub
            logger.error(
                f"Slow consumer on {type(sub).__name__}: {sub._id} (subject={error.subject}). Reply expected on subject {error.reply}"
            )
            # Respond to the requester
            await self._reply_on_slow_consumer(error)
        # FIXME: We should learn how to handle everything else I guess 😕
        else:
            # At the moment raise error and inspect traceback
            try:
                raise error
            except Exception:
                logger.exception("An NATS Error was not handled")

    async def connect(self, **kwargs: Any) -> None:
        # Get options from config
        default_options = self.config.dict(
            exclude={"protocol", "reconnect_timeout", "credentials"}
        )
        # Rename some options
        default_options["reconnect_time_wait"] = self.config.reconnect_timeout
        default_options["user_credentials"] = self.config.credentials
        default_options["error_cb"] = self.default_error_cb
        options = {**default_options, **kwargs}
        logger.debug(f"Connecting to NATS using options: {options}")
        try:
            await self._nats.connect(**options)
        except nats.errors.NoServersError:
            raise NoServerError("No server available for connection")

    async def close(self) -> None:
        """Close connection to NATS server"""
        try:
            await self._nats.close()
        except (AttributeError, AssertionError):
            raise ConnectionNotStartedError(
                "Broker is not started yet. Use the .connect() coroutine method start the broker."
            )

    async def drain(self) -> None:
        """Drain connection to a NATS server

        drain will put a connection into a drain state. All subscriptions will
        immediately be put into a drain state. Upon completion, the publishers
        will be drained and can not publish any additional messages. Upon draining
        of the publishers, the connection will be closed.
        """
        try:
            await self._nats.drain()
        except (AttributeError, AssertionError):
            raise ConnectionNotStartedError(
                "Broker is not started yet. Use the .connect() coroutine method start the broker."
            )
        except nats.errors.ConnectionClosedError as err:
            raise ConnectionClosedError(*err.args)

    async def publish(self, request: Request) -> None:
        kwargs = {
            "subject": str(request.subject),
            "payload": request.data,
            "reply": request.reply,
            "headers": dict(request.headers),
        }
        try:
            await self._nats.publish(**kwargs)
        except (AttributeError, AssertionError):
            raise ConnectionNotStartedError(
                "Broker is not started yet. Use the .connect() coroutine method start the broker."
            )
        except nats.errors.BadSubjectError:
            raise InvalidSubjectError("Subject cannot be empty")
        except nats.errors.MaxPayloadError as err:
            raise MaxPayloadError(*err.args)
        except nats.errors.TimeoutError as err:
            raise TimeoutError(*err.args)
        except nats.errors.ConnectionClosedError as err:
            raise ConnectionClosedError(*err.args)
        except nats.errors.ConnectionDrainingError as err:
            raise ConnectionDrainingError(*err.args)

    async def flush(self, timeout: float = 10) -> None:
        try:
            await self._nats.flush(timeout)
        except (AttributeError, AssertionError):
            raise ConnectionNotStartedError(
                "Broker is not started yet. Use the .connect() coroutine method start the broker."
            )
        except nats.errors.TimeoutError as err:
            raise TimeoutError(*err.args)
        except nats.errors.ConnectionClosedError as err:
            raise ConnectionClosedError(*err.args)
        except nats.errors.ConnectionDrainingError as err:
            raise ConnectionDrainingError(*err.args)

    async def request(self, request: Request) -> Response[bytes]:
        kwargs = {
            "subject": str(request.subject),
            "payload": request.data,
            "timeout": request.request_timeout,
            "headers": dict(request.headers),
        }
        try:
            msg = await self._nats.request(**kwargs)
        except (AttributeError, AssertionError):
            raise ConnectionNotStartedError(
                "Broker is not connected yet. Use the .connect() coroutine method start the broker."
            )
        except nats.errors.BadSubjectError as err:
            raise InvalidSubjectError(*err.args)
        except nats.errors.MaxPayloadError as err:
            raise MaxPayloadError(*err.args)
        except nats.errors.NoRespondersError as err:
            return Response(
                success=False,
                code=404,
                error="NoResponderError",
                details=f"No responder on subject {request.subject}",
                exception=err,
            )
        except nats.errors.TimeoutError as err:
            raise TimeoutError(*err.args)
        except nats.errors.ConnectionClosedError as err:
            raise ConnectionClosedError(*err.args)
        except nats.errors.ConnectionDrainingError as err:
            raise ConnectionDrainingError(*err.args)
        headers = msg.headers
        # FIXME: Now that we consider success and code everywhere, we should never process requests without those informations
        # If we talk only between quara services, then it's fine
        # But if we talk with third party services, we need to be able to parse a Response too
        if "success" not in headers:
            headers["success"] = True
        if "code" not in headers:
            headers["code"] = 200
        return Response(**msg.headers, data=msg.data)

    async def subscribe(
        self,
        subject: str,
        cb: Callable[[Request], Awaitable[None]],
        queue: str = "",
        max_msgs: Optional[int] = 0,
        pending_bytes_limit: int = 1024,
        pending_requests_limit: int = 1,
        concurrent_requests_limit: int = 1,
    ) -> SubscriptionProtocol:
        sub = NATSSubscription(
            self._nats,
            subject,
            cb,
            queue,
            max_msgs=max_msgs or 0,
            pending_bytes_limit=pending_bytes_limit,
            pending_requests_limit=pending_requests_limit,
            concurrent_requests_limit=concurrent_requests_limit,
        )
        # Start the subscrpition
        await sub.start()
        # Return the subscription
        return sub


class NATSSubscription(SubscriptionProtocol):
    def __init__(
        self,
        nats: NATS,
        subject: str,
        cb: Callable[..., Awaitable[None]],
        queue: Optional[str] = "",
        max_msgs: Optional[int] = 0,
        pending_bytes_limit: int = 1024,
        pending_requests_limit: int = 1,
        concurrent_requests_limit: int = 1,
        **kwargs: Any,
    ) -> None:
        # Display warning if kwargs are used. This is meant to preserve compatibility between backends
        # while warning for potential error (use of a non existing option for a specific backend)
        for key in kwargs:
            logger.warning(
                f"Warning: Ignoring option {key} not supported by {self.__class__.__name__}"
            )
        # the NATS client which will be used to perform subscription
        self._nats = nats
        # the subscription subject
        self.subject = Subject(subject)
        # The subscription queue is always a string (use empty string if None is provided)
        self.queue = queue or ""
        # Maxixum number of messages to receive before unsubscribing (0 means unlimited messages, use 0 if None is provided)
        self.max_msgs = max_msgs or 0
        # Maximum number of requests to be processed concurrently (this is different from number of pending requests)
        self.concurrent_requests_limit = concurrent_requests_limit
        # Maximum number of bytes to
        self.pending_bytes_limit = pending_bytes_limit
        # Messages received through NATS are pushed into a pending buffer
        # An asyncio task continuously fetch messages from the pending buffer and execute the user callback
        # pending_request_limit can be used to configure how many requests can be stored in pending buffer
        # Once limit is reached, received messages are not processed and immediately raise a SlowConsumer.
        # NATS does not support 0 pending request
        # Instead, using 0 will lead to an infite pending limit
        # Moreover -1 is not a supported value by NATS
        # In order to be consistent with asyncio and anyio
        # -1 is used for infinite pending requests, it will be transforemd into 0 for NATS
        # 0 is used for the smallest pending request limit, it will be transformed into 0 for NATS
        # Anything else is forwarded untouched to NATS
        self.pending_requests_limit = (
            0
            if pending_requests_limit == -1
            else (pending_requests_limit if pending_requests_limit != 0 else 1)
        )
        # Create a task pool
        self._task_pool = TaskPool(self.concurrent_requests_limit)
        # Store the callback
        self._cb = cb

    @property
    def id(self) -> int:
        """Id of the subscription. Can be used to stored subscriptions into mappings"""
        if not hasattr(self, "_nats_subscription"):
            raise SubscriptionNotStartedError("Subscription is not started yet")
        # mypy considers NATS as untyped...
        return self._nats_subscription._id  # type: ignore[no-any-return]

    @property
    def pending_requests(self) -> int:
        """Number of pending requests in the subscription"""
        if not hasattr(self, "_nats_subscription"):
            raise SubscriptionNotStartedError("Subscription is not started yet")
        # mypy considers NATS as untyped...
        return self._nats_subscription.pending_msgs  # type: ignore[no-any-return]

    @property
    def pending_bytes(self) -> int:
        """Number of pending bytes in the subscription"""
        if not hasattr(self, "_nats_subscription"):
            raise SubscriptionNotStartedError("Subscription is not started yet")
        return self._nats_subscription._pending_size  # type: ignore[no-any-return]

    async def start(self) -> None:
        """Start the subscription"""
        options = {
            "subject": self.subject,
            "queue": self.queue,
            "cb": get_nats_cb(self._task_pool, self._cb),
            "max_msgs": self.max_msgs,
            "pending_bytes_limit": self.pending_bytes_limit,
            "pending_msgs_limit": self.pending_requests_limit,
        }
        try:
            self._nats_subscription = await self._nats.subscribe(**options)
        except (AttributeError, AssertionError):
            raise ConnectionNotStartedError(
                "Broker is not started yet. Use the .connect() coroutine method start the broker."
            )
        except nats.errors.BadSubjectError as err:
            raise InvalidSubjectError(*err.args)
        except nats.errors.ConnectionClosedError as err:
            raise ConnectionClosedError(*err.args)
        except nats.errors.ConnectionDrainingError as err:
            raise ConnectionDrainingError(*err.args)
        except nats.errors.Error as err:
            raise InvalidCallbackError(*err.args)

    async def unsubscribe(
        self, limit: int = 0, cancel_timout: Optional[float] = None
    ) -> None:
        """Close the subscription. Cancel all pending messages and tasks"""
        if not hasattr(self, "_nats_subscription"):
            raise SubscriptionNotStartedError("Subscription is not started yet")
        try:
            await self._nats_subscription.unsubscribe(limit)
        except (
            nats.errors.ConnectionClosedError,
            nats.errors.BadSubscriptionError,
        ) as err:
            raise ConnectionClosedError(*err.args)
        except nats.errors.ConnectionDrainingError as err:
            raise ConnectionDrainingError(*err.args)
        finally:
            if limit <= 0:
                # FIXME: How do we configure this timeout ?
                await self._task_pool.drain(0, cancel_timeout=cancel_timout)

    async def drain(
        self, drain_timeout: float, cancel_timeout: Optional[float] = None
    ) -> None:
        """Stop interestn and process pending messages before closing subscription"""
        if not hasattr(self, "_nats_subscription"):
            raise SubscriptionNotStartedError("Subscription is not started yet")
        try:
            await self._nats_subscription.drain()
        except (
            nats.errors.ConnectionClosedError,
            nats.errors.BadSubscriptionError,
        ) as err:
            raise ConnectionClosedError(*err.args)
        finally:
            await self._task_pool.drain(drain_timeout, cancel_timeout)
