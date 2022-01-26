import asyncio
import sys
from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, TypeVar

from aiohttp import (
    ClientSession,
    ClientWebSocketResponse,
    WSMessage,
    WSMsgType,
    WSServerHandshakeError,
)

from .context import COILED_OP_CONTEXT, create_trace_data
from .errors import ServerError

MessageReturnT = TypeVar("MessageReturnT")


async def _exhaust_async_iterator(stream):
    async for _ in stream:
        pass


class WebsocketConnectorBase(Generic[MessageReturnT], ABC):
    def __init__(
        self,
        endpoint: str,
        session: ClientSession,
    ):
        self.endpoint = endpoint
        self.session = session
        self._error_messages: List[MessageReturnT] = []
        self.ws: ClientWebSocketResponse

    async def connect(self):
        self.ws = await self.session.ws_connect(self.endpoint)

    async def send_json(self, data: Dict):
        await self.ws.send_json({**data, **create_trace_data()})

    @abstractmethod
    async def on_message(self, message_data: Dict) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def check_error_message(self, message_data: Dict) -> Optional[MessageReturnT]:
        raise NotImplementedError()

    def error_messages(self) -> List[MessageReturnT]:
        return self._error_messages

    @abstractmethod
    async def on_error(self, message: WSMessage):
        # TODO comment about why this is different from error_messages, etc.
        raise NotImplementedError()

    @abstractmethod
    async def on_close(self, message: WSMessage):
        raise NotImplementedError()

    async def close(self, *, code: int = 1000, message: bytes = b""):
        await self.ws.close(code=code, message=message)

    def __aiter__(self):
        return self

    async def __anext__(self):
        message = await self.ws.receive()
        if message.type == WSMsgType.TEXT:
            data = message.json()
            error_message = await self.check_error_message(data)
            if error_message:
                self._error_messages.append(error_message)
            await self.on_message(data)
        elif message.type == WSMsgType.ERROR:
            await self.on_error(message)
        elif message.type in (WSMsgType.CLOSE, WSMsgType.CLOSED, WSMsgType.CLOSING):
            # From what I could tell, whenever we get any one of
            # these, the ClientWebsocketResponse already has a close_code
            # and an exception (when there is one), so we should be able to
            # handle the close on any one of these message types, but I may
            # end up being wrong
            await self.on_close(message)
            raise StopAsyncIteration


class NotificationWebsocketConnector(WebsocketConnectorBase[str]):
    def __init__(
        self,
        endpoint: str,
        session: ClientSession,
        log_output=sys.stdout,
    ):
        super().__init__(endpoint, session)
        self.log_output = log_output

    async def on_message(self, message_data: Dict) -> None:
        # This could be there as a None value
        data = message_data.get("data") or {}
        # Ignore notifications that are unrelated to this context
        if not data.get("coiled-operation-id", "") == COILED_OP_CONTEXT.get(""):
            return
        message_data = message_data["message"]
        print(message_data, file=self.log_output)

    async def on_error(self, error: WSMessage) -> None:
        print(
            f"Error with connection to notifications endpoint: {error}",
            file=self.log_output,
        )

    async def check_error_message(self, message_data: Dict) -> Optional[str]:
        if message_data.get("is_error", False):
            return message_data["message"]

    async def on_close(self, message: WSMessage) -> None:
        # Right now notifications are always riding sidecar to another
        # connection. We may need to add visibility here but I didn't
        # want to clutter the user's screen with potentially confusing
        # messages. Hopefully our server logs would capture bad things
        # related to notification connections.
        pass


class WebsocketConnector(WebsocketConnectorBase[str]):
    def __init__(
        self,
        endpoint: str,
        notifications_endpoint: str,
        session: ClientSession,
        log_output=sys.stdout,
        connection_error_message: str = "Unable to connect to server",
    ):
        super().__init__(endpoint, session)
        self.log_output = log_output
        self.notification_connector = NotificationWebsocketConnector(
            endpoint=notifications_endpoint,
            session=session,
            log_output=log_output,
        )
        self.connection_error_message = connection_error_message

    async def connect(self):
        try:
            await super().connect()
            await self.notification_connector.connect()
        except WSServerHandshakeError:
            raise ValueError(self.connection_error_message)

    async def on_message(self, message_data: Dict) -> None:
        if "message" in message_data:
            message = message_data["message"]
            print(message, file=self.log_output)

    async def check_error_message(self, message_data: Dict) -> Optional[str]:
        if message_data.get("is_error") or message_data.get("raise"):
            return message_data["message"]

    async def on_error(self, message: WSMessage) -> None:
        print("Error with connection: ", str(message.extra), file=self.log_output)

    async def on_close(self, message: WSMessage) -> None:
        ws_exception = self.ws.exception()
        close_code: Optional[int] = self.ws.close_code
        is_bad_close_code = close_code and 1000 < close_code < 3000
        error_messages = self.error_messages()

        try:
            if self.notification_connector:
                await self.notification_connector.close()
        except Exception:
            # The notification connector is not mission critical,
            pass

        if error_messages:
            # Just print the ws_exception and close code, raise the last
            # error message we sent
            if ws_exception:
                print(f"Websocket exception: {ws_exception}", file=self.log_output)
            raise ServerError(error_messages[-1])
        elif ws_exception or is_bad_close_code:
            ws_error_message = f"Error with connection to server: code {close_code}"
            if ws_exception:
                raise ValueError(ws_error_message) from ws_exception
            else:
                raise ValueError(ws_error_message)

    async def stream_messages(self):
        await asyncio.gather(
            _exhaust_async_iterator(self),
            _exhaust_async_iterator(self.notification_connector),
        )


class ConfigureBackendConnector(WebsocketConnector):
    async def on_message(self, message_data: Dict) -> None:
        if message_data.get("type") != "update_options":
            return

        message = message_data["message"]
        if message == "FINISHED":
            await self.close()
            return
        elif message in ["CONFIGURING_BACKEND", "NOT_CONFIGURING_BACKEND"]:
            # These are messages used by the web UI, we can ignore
            # them here.
            return

        print(message, file=self.log_output)
