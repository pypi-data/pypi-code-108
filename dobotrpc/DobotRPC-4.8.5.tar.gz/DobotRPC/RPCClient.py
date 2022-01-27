import websockets
import asyncio
import json
from .NetworkError import RpcVersionInvaild, CommNotConnectError, NetworkError
from .NetworkError import InvaildJsonMsg, RpcIdInvaild
from .Utils import loggers
from typing import Any, Callable

LOGGER_NAME = "RPCClient"


class RPCClient(object):
    def __init__(self,
                 ip: str = "localhost",
                 port: int = 9090,
                 cb_connected: Callable[[], None] = None,
                 cb_disconnected: Callable[[], None] = None,
                 loop: asyncio.BaseEventLoop = None):
        self.__cb_connected = cb_connected
        self.__cb_disconnected = cb_disconnected
        self.__loop = loop if loop else asyncio.get_event_loop()
        self.__id = 0
        self.__exchange_map = {}
        self.__recv_task_timer = None
        self.__ws = None
        self.__client_name = "DobotRPC-WSClient"
        self.__ip = ip
        self.__port = port

        self.__loop.create_task(self.__connect_recv_worker())

    def __del__(self):
        if self.__recv_task_timer:
            self.__recv_task_timer.stop()

        if self.__ws:
            self.__ws.close()
            self.__ws.wait_closed()

    @property
    def address(self):
        return "%s:%d" % (self.__ip, self.__port)

    @property
    def remote_address(self):
        return "%s:%d" % (self.__ws.remote_address[0],
                          self.__ws.remote_address[1])

    @property
    def local_address(self):
        return "%s:%d" % (self.__ws.local_address[0],
                          self.__ws.local_address[1])

    def __pack_rpc(self,
                   rpc_id: int,
                   rpc_playload: Any,
                   method: str = None) -> str:
        if rpc_id is None:
            data = {"jsonrpc": "2.0"}
        else:
            data = {"id": rpc_id, "jsonrpc": "2.0"}

        if method:
            data["method"] = method
            data["params"] = rpc_playload
        else:
            if isinstance(rpc_playload, Exception):
                # TODO: 所有异常捕捉并处理
                error_str = str(rpc_playload)
                if "code" in error_str:
                    rpc_playload = json.loads(error_str)
                else:
                    rpc_playload = {
                        "code": -32000,
                        "message": "VM >> %s" % error_str
                    }
                loggers.get(LOGGER_NAME).error(rpc_playload, exc_info=True)
                data["error"] = rpc_playload
            else:
                data["result"] = rpc_playload

        rpc_packet = json.dumps(data)
        return rpc_packet

    def __unpack_rpc(self, message: str) -> (int, str, str, str, Exception):
        try:
            data = json.loads(message)
        except Exception as e:
            raise InvaildJsonMsg(e)

        rpc_id = data.get("id", None)
        if type(rpc_id) is not int:
            raise RpcIdInvaild()

        rpc_verison = data.get("jsonrpc", None)
        if rpc_verison != "2.0":
            raise RpcVersionInvaild()

        method = data.get("method", None)
        params = data.get("params", None)
        result = data.get("result", None)
        error = data.get("error", None)
        if error:
            error = Exception(error)

        return rpc_id, method, params, result, error

    async def __connect_recv_worker(self):
        ws_data = None
        while True:
            if self.is_connected:
                try:
                    # 阻塞获取，不担心性能问题
                    ws_data = await self.__ws.recv()
                    loggers.get(LOGGER_NAME).debug(
                        "C(%s) << S(%s):%s" %
                        (str(self.local_address), str(
                            self.remote_address), str(ws_data)))
                except Exception as e:
                    loggers.get(LOGGER_NAME).debug("error:", e)
                    if self.__cb_disconnected:
                        result = self.__cb_disconnected()
                        if isinstance(result, asyncio.Future):
                            await result

                try:
                    if ws_data:
                        rpc_id, _, _, result, error = self.__unpack_rpc(
                            ws_data)
                        exchange = self.__exchange_map.get(rpc_id, None)
                        if exchange:
                            cb_feedback = exchange["feedback"]
                            if cb_feedback:
                                await cb_feedback(error, result)
                            else:
                                exchange["result"] = result
                                exchange["error"] = error
                                exchange["event"].set()
                        else:
                            loggers.get(LOGGER_NAME).warning(
                                "Invalid request:%s" % str(ws_data))
                except Exception as e:
                    loggers.get(LOGGER_NAME).debug("error", e)

            else:
                try:
                    self.__ws = await websockets.connect(
                        "ws://%s:%s" % (self.__ip, self.__port),
                        timeout=10,
                    )
                    loggers.get(LOGGER_NAME).info("Have connected dobotlink")
                    if self.__cb_connected:
                        result = self.__cb_connected()
                        if isinstance(result, asyncio.Future):
                            await result
                except Exception as e:
                    loggers.get(LOGGER_NAME).warning(
                        "Can not connect dobotlink: %s" % str(e))
                    print("RPCClient - connect server error: %s" % str(e))
                    await asyncio.sleep(0.5)

    async def send(self, method: str, params: dict = {}) -> Any:
        if not self.is_connected:
            raise CommNotConnectError("Had not connected Dobotlink!")

        cb_feedback = params.pop("cb_feedback", None)

        self.__id += 1
        comm_id = self.__id

        payload = {
            "method": method,
            "jsonrpc": "2.0",
            "params": {} if params is None else params,
            "id": comm_id
        }

        loggers.get(LOGGER_NAME).debug(
            "C(%s) >> S(%s): %s" %
            (str(self.local_address), str(self.remote_address), str(payload)))
        await self.__ws.send(json.dumps(payload))

        if cb_feedback:
            self.__exchange_map[comm_id] = {
                "feedback": cb_feedback,
                "event": None,
                "result": None,
                "error": None
            }
            return None
        else:
            event = asyncio.Event()
            self.__exchange_map[comm_id] = {
                "feedback": None,
                "event": event,
                "result": None,
                "error": None
            }
            await event.wait()

            exchange = self.__exchange_map.pop(comm_id, None)
            if exchange is None:
                raise Exception()

            if exchange["error"] is not None:
                raise NetworkError(exchange["error"])

            return exchange["result"]

    @property
    def is_connected(self) -> bool:
        return self.__ws is not None and self.__ws.open

    async def wait_for_connected(self):
        while not self.is_connected:
            await asyncio.sleep(0.01)

    async def wait_for_disconnected(self):
        while self.is_connected:
            await asyncio.sleep(0.01)

    async def notify(self, method: str, data: Any) -> Any:
        if self.__ws_client is None:
            raise Exception("Had not connected!")

        rpc_packet = self.__pack_rpc(None, data, method)
        loggers.get(LOGGER_NAME).debug("C(%s) >> S(%s): %s" % (str(
            self.local_address), str(self.remote_address), str(rpc_packet)))
        await self.__ws.send(json.dumps(rpc_packet))
