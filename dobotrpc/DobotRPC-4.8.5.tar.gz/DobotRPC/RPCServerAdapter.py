from .RPCServer import RPCServer
from typing import Any


class ModuleAdapter(object):
    def __init__(self, rpc_server: RPCServer):
        self.__name = None
        self.__rpc_server = rpc_server

    def set_name(self, name: str):
        self.__name = name

    def __getattr__(self, func_name: str) -> Any:
        async def send_warpper(**params) -> None:
            method = f"gui.{self.__name}.{func_name}"
            return await self.__rpc_server.notify(method, params)

        return send_warpper


class GUIAdapter(object):
    def __init__(self):
        self.__rpc_server = None

    def init(self, rpc_server: RPCServer):
        self.__rpc_server = rpc_server
        self.__module = ModuleAdapter(rpc_server)

    @property
    def is_connected(self):
        return self.__rpc_server and self.__rpc_server.is_connected

    def __getattr__(self, name: str) -> Any:
        self.__module.set_name(name)
        return self.__module
