from datetime import datetime
from typing import List

from nehushtan.ws.NehushtanWebsocketAgent import NehushtanWebsocketAgent
from nehushtan.ws.NehushtanWebsocketConnectionEntity import NehushtanWebsocketConnectionEntity
from tests.ws.TestWebsocketRegisterAgent import TestWebsocketRegisterAgent


class TestWebsocketAgent(NehushtanWebsocketAgent):
    register_agent: TestWebsocketRegisterAgent

    def register_raw_websocket_connection(self, websocket):
        TestWebsocketAgent.register_agent.register(websocket)

    def unregister_raw_websocket_connection(self, websocket_key: str):
        TestWebsocketAgent.register_agent.unregister(websocket_key)

    def build_response_content(self, websocket_key: str, received_content: str) -> str:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        return f'RESPONSE ON {current_time} TO {websocket_key} FOR {received_content}'

    def get_connections_related_to_this_agent(self) -> List[NehushtanWebsocketConnectionEntity]:
        if not self.get_local_key():
            return []

        return TestWebsocketAgent.register_agent.list_for_server(self.get_local_key())

    def check_content_to_send_to_target_client(self, connection: NehushtanWebsocketConnectionEntity) -> str:
        return f"Broadcast to [{connection.get_key()}]"
