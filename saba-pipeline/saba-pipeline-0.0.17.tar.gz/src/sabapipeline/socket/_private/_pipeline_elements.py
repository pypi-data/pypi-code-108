import asyncio
import time
from socket import gaierror
from threading import Lock

import websockets
from websockets.exceptions import ConnectionClosedError

from ._data_types import SocketConfig
from ... import TriggererEventSource, Event, EventSink, PipelineException
from ..._private._utilities import *


class SocketConnector(TriggererEventSource, EventSink):
    def __init__(self,
                 socket_config: SocketConfig,
                 deserializer: Callable[[str], List[Any]],
                 serializer: Callable[[Event], str] = None,
                 initial_message_generator: Callable[[], List[str]] = lambda: [],
                 responder: Callable[[str], List[str]] = lambda message: [],
                 **kwargs):
        super().__init__(**kwargs)
        self.socket_config: SocketConfig = socket_config
        self.deserializer = deserializer
        self.serializer = serializer
        self.initial_message_generator = initial_message_generator
        self.responder = responder
        self.last_try_for_connect = None
        self.current_reconnect_timeout = self.socket_config.initial_reconnect_timeout
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.lock = Lock()

    def drown_event(self, event: Event) -> None:
        if self.serializer is None:
            raise PipelineException("Socket Connector cannot serialize event as it has no serializer")
        serialized_event: str = self.serializer(event)
        SocketConnector._get_event_loop().run_until_complete(self._send_message(serialized_event))

    def get_event_batch(self) -> List[Event]:
        event_string = SocketConnector._get_event_loop().run_until_complete(self._get_message_string())
        if event_string is None:
            return []
        try:
            return self.deserializer(event_string)
        except Exception as e:
            self.logger.exception(f"Failed to deserialize socket message \"{event_string}\": {e.__str__()}")

    async def _send_message(self, message: str):
        websocket = await self._get_websocket()
        if websocket is None:
            raise PipelineException("Cannot send message as because failed to load websocket")
        await websocket.send(message)

    async def _get_message_string(self) -> Optional[str]:
        websocket = await self._get_websocket()
        if websocket is None:
            return None
        try:
            message = await websocket.recv()
            responses: List[str] = self.responder(message)
            for response in responses:
                websocket.send(response)
            return message
        except ConnectionClosedError as e:
            self.logger.error(f"Disconnected from {self.socket_config.server.__str__()}: {str(e)}")
        except Exception as e:
            self.logger.exception(f"Disconnected from {self.socket_config.server.__str__()}: {str(e)}")
        self.websocket = None
        return None

    async def _get_websocket(self):
        self.lock.acquire()
        try:
            if self.websocket is None:
                self.websocket = await self._get_initial_websocket()
            return self.websocket
        finally:
            self.lock.release()

    async def _get_initial_websocket(self) -> Optional[websockets.WebSocketClientProtocol]:
        if self.last_try_for_connect is not None and (
                self.last_try_for_connect + self.current_reconnect_timeout) > time.time():
            return None
        self.last_try_for_connect = time.time()
        self.current_reconnect_timeout = min(self.current_reconnect_timeout * 2,
                                             self.socket_config.max_reconnect_timeout)
        self.logger.debug(f"Trying to connect to {self.socket_config.server.__str__()}")
        try:
            result = await websockets.connect(
                uri=self.socket_config.server.address,
                port=self.socket_config.server.port,
                **self.socket_config.connection_kwargs)
            self.logger.info(f"Connected to {self.socket_config.server.__str__()}")
            self.current_reconnect_timeout = self.socket_config.initial_reconnect_timeout
            for initial_message in self.initial_message_generator():
                await result.send(initial_message)
            return result
        except gaierror as e:
            self.logger.info(
                f"Failed to connect to {self.socket_config.server.__str__()}: {str(e)}. Retrying in {self.current_reconnect_timeout} seconds")
        except Exception as e:
            self.logger.exception(
                f"Failed to connect to {self.socket_config.server.__str__()}: {str(e)}. Retrying in {self.current_reconnect_timeout} seconds")
        return None

    @staticmethod
    def _get_event_loop():
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            return event_loop

    def _do_periodic_event_generation(self):
        while self.running:
            try:
                events: List[Event] = self.get_event_batch()
                for event in events:
                    self.event_handler.handle_event(event)
            except Exception as e:
                self.logger.exception("Failed to generate event", e)

    def start_generating(self) -> None:
        self.running = True
        threading.Thread(target=self._do_periodic_event_generation).start()

    def stop_generating(self) -> None:
        self.running = False
