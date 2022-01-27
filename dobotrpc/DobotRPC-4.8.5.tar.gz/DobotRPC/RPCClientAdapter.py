from . import RPCClient
from typing import Any
import asyncio


class DobotlinkAdapter(object):
    class __ModuleAdapter(object):
        def __init__(self, rpc_client: RPCClient, is_sync: bool,
                     module_name: str):
            self.__module_name = module_name
            self.__rpc_client = rpc_client
            self.__is_sync = is_sync
            self.__port_name = None

        def set_port_name(self, port_name: str) -> None:
            self.__port_name = port_name

        def __getattr__(self, func_name: str) -> Any:
            if self.__is_sync:

                def send_warpper(**params) -> Any:
                    method = "dobotlink.%s.%s" % (self.__module_name,
                                                  func_name)
                    if self.__port_name is not None:
                        params["portName"] = self.__port_name
                    fut = self.__rpc_client.send(method, params)
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(fut)
            else:

                async def send_warpper(**params) -> Any:
                    method = "dobotlink.%s.%s" % (self.__module_name,
                                                  func_name)
                    if self.__port_name is not None:
                        params["portName"] = self.__port_name
                    return await self.__rpc_client.send(method, params)

            return send_warpper

    def __init__(self, rpc_client: RPCClient, is_sync: bool = False):
        self.__is_sync = is_sync
        self.__rpc_client = rpc_client

        loop = asyncio.get_event_loop()
        loop.run_until_complete(rpc_client.wait_for_connected())

    @property
    def is_connected(self):
        return self.__rpc_client and self.__rpc_client.is_connected

    def __getattr__(self, module_name: str):
        module = self.__ModuleAdapter(self.__rpc_client, self.__is_sync,
                                      module_name)
        self.__dict__[module_name] = module
        return module


class NormalAdapter(object):
    def __init__(self, rpc_client: RPCClient, is_sync: bool = False):
        self.__rpc_client = rpc_client
        self.__is_sync = is_sync

        loop = asyncio.get_event_loop()
        loop.run_until_complete(rpc_client.wait_for_connected())

    @property
    def is_connected(self):
        return self.__rpc_client and self.__rpc_client.is_connected

    def __getattr__(self, method: str):
        if self.__is_sync:

            def send_warpper(**params) -> Any:
                fut = self.__rpc_client.send(method, params)
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(fut)
        else:

            async def send_warpper(**params) -> Any:
                return await self.__rpc_client.send(method, params)

        return send_warpper
