import asyncio
from abc import abstractmethod
from typing import List

from websockets.exceptions import ConnectionClosedError

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.ws.NehushtanWebsocketConnectionEntity import NehushtanWebsocketConnectionEntity


class NehushtanWebsocketAgent:
    def __init__(
            self,
            broadcast_sleep_seconds: int,
            request_handle_logger: NehushtanFileLogger,
            broadcast_logger: NehushtanFileLogger
    ):
        self.__request_handle_logger = request_handle_logger
        self.__broadcast_logger = broadcast_logger
        self.__local_key = ''
        self.broadcast_sleep_seconds = broadcast_sleep_seconds

    def get_local_key(self):
        return self.__local_key

    def make_key_of_websocket(self, websocket) -> str:
        local_key = f'{websocket.local_address[0]}-{websocket.local_address[1]}'
        remote_key = f'{websocket.remote_address[0]}-{websocket.remote_address[1]}'

        if self.__local_key == '':
            self.__local_key = local_key
        elif self.__local_key != local_key:
            raise RuntimeError(f"NehushtanWebsocketAgent LOCAL KEY CHANGED {self.__local_key} -> {local_key}")

        return f'{local_key}~{remote_key}'

    @abstractmethod
    def register_raw_websocket_connection(self, websocket):
        """
        Save the argument `websocket`,
        and bind it to its key, which should be computed by `self.make_key_of_websocket(websocket)`
        """
        pass

    @abstractmethod
    def unregister_raw_websocket_connection(self, websocket_key: str):
        """
        Remove the connection from the registeration according to its key `websocket_key`
        """
        pass

    @abstractmethod
    def build_response_content(self, websocket_key: str, received_content: str) -> str:
        """
        Handle the message and build the response content to send back
        """
        pass

    async def ws_request_handler(self, websocket, path):
        while True:
            connection_key = self.make_key_of_websocket(websocket)
            self.__request_handle_logger.debug(f"Handling connection [{connection_key}] for path [{path}]")
            self.register_raw_websocket_connection(websocket)

            try:
                received_content = await websocket.recv()
                self.__request_handle_logger.info(f"Received From [{connection_key}]", {'content': received_content})

                response_content = self.build_response_content(connection_key, received_content)
                if len(response_content) > 0:
                    await websocket.send(response_content)
                    self.__request_handle_logger.info(f"Sent to [{connection_key}]", {'content': response_content})
            except ConnectionClosedError as theConnectionClosedError:
                self.__request_handle_logger.info(
                    f"Connection [{connection_key}] lost, to remove. Error: {theConnectionClosedError}"
                )
                self.unregister_raw_websocket_connection(connection_key)
                break

    @abstractmethod
    def get_connections_related_to_this_agent(self) -> List[NehushtanWebsocketConnectionEntity]:
        pass

    @abstractmethod
    def check_content_to_send_to_target_client(self, connection: NehushtanWebsocketConnectionEntity) -> str:
        pass

    async def ws_broadcast_handler(self):
        while True:
            connections = self.get_connections_related_to_this_agent()

            for connection in connections:
                self.__broadcast_logger.debug(f"Broadcast to [{connection.get_key()}]")
                try:
                    await connection.get_websocket().ping()

                    content_to_send = self.check_content_to_send_to_target_client(connection)
                    if content_to_send:
                        await connection.get_websocket().send(content_to_send)
                except ConnectionClosedError as theConnectionClosedError:
                    self.__broadcast_logger.info(
                        f"Connection [{connection.get_key()}] lost, to remove. Error: {theConnectionClosedError}"
                    )
                    self.unregister_raw_websocket_connection(connection.get_key())

            await asyncio.sleep(self.broadcast_sleep_seconds)
