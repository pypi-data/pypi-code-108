import uuid
from typing import Dict, List

from nehushtan.ws.NehushtanWebsocketConnectionEntity import NehushtanWebsocketConnectionEntity


class TestWebsocketRegisterAgent:

    def __init__(self):
        self.__map: Dict[str, NehushtanWebsocketConnectionEntity] = {}
        self.agent_identity = str(uuid.uuid4())

    def register(self, websocket):
        entity = NehushtanWebsocketConnectionEntity(websocket)
        self.__map[entity.get_key()] = entity
        print(f"TestWebsocketRegisterAgent[{self.agent_identity}] registered [{entity.get_key()}]")
        return entity

    def unregister(self, key: str):
        if self.__map.get(key):
            del self.__map[key]
            print(f"TestWebsocketRegisterAgent[{self.agent_identity}] unregistered [{key}]")

    def read(self, key: str):
        print(f"TestWebsocketRegisterAgent[{self.agent_identity}] reading [{key}]")
        return self.__map.get(key)

    def list_for_server(self, local_key: str) -> List[NehushtanWebsocketConnectionEntity]:
        print(f"TestWebsocketRegisterAgent[{self.agent_identity}] listing for [{local_key}]")
        enities = []
        for k, v in self.__map.items():
            if v.get_local_key() == local_key:
                enities.append(v)
        return enities
