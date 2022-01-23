import logging, typing, inspect, asyncio

import uvicorn, uvloop
from fastapi import FastAPI, Request, WebSocket
from discord.ext.ipc.errors import *
from unsync import unsync
import sys

log = logging.getLogger(__name__)


def route(name=None):
    """
    Used to register a coroutine as an endpoint when you don't have
    access to an instance of :class:`.Server`

    Parameters
    ----------
    name: str
        The endpoint name. If not provided the method name will be
        used.
    """

    def decorator(func):
        if not name:
            Server.ROUTES[func.__name__] = func
        else:
            Server.ROUTES[name] = func

        return func

    return decorator


class IpcServerResponse:
    def __init__(self, data):
        self._json = data
        self.length = len(data)

        self.endpoint = data["endpoint"]

        for key, value in data["data"].items():
            setattr(self, key, value)

    def to_json(self):
        return self._json

    def __repr__(self):
        return "<IpcServerResponse length={0.length}>".format(self)

    def __str__(self):
        return self.__repr__()


class Server:
    """The IPC server. Usually used on the bot process for receiving
    requests from the client.

    Attributes
    ----------
    bot: :class:`~discord.ext.commands.Bot`
        Your bot instance
    host: str
        The host to run the IPC Server on. Defaults to localhost.
    port: int
        The port to run the IPC Server on. Defaults to 8765.
    secret_key: str
        A secret key. Used for authentication and should be the same as
        your client's secret key.
    multicast_port: int
        The port to run the multicasting server on. Defaults to 20000
    """

    ROUTES = {}

    def __init__(
        self,
        bot,
        host="localhost",
        port=8765,
        secret_key=None,
    ):
        self.bot = bot
        self.loop = bot.loop

        self.secret_key = secret_key

        self.host = host
        self.port = port

        self._server = None
        self.endpoints = {}

    def route(self, name=None):
        """Used to register a coroutine as an endpoint when you have
        access to an instance of :class:`.Server`.

        Parameters
        ----------
        name: str
            The endpoint name. If not provided the method name will be used.
        """

        def decorator(func):
            if not name:
                self.endpoints[func.__name__] = func
            else:
                self.endpoints[name] = func

            return func

        return decorator

    def update_endpoints(self):
        """Called internally to update the server's endpoints for cog routes."""
        self.endpoints = {**self.endpoints, **self.ROUTES}

        self.ROUTES = {}

    @unsync
    def __start(self, application : FastAPI):
        """Starts the application server"""
        self.bot.dispatch("ipc_app_ready", app=application)
        log.info("IPC Application running")
        return uvicorn.run(host=self.host, port=self.port, app=application, loop="uvloop", ws="wsproto")

    def start(self):
        """Starts the IPC server and handles websocket requests/endpoint requests."""
        self.bot.dispatch("ipc_ready")

        self._server = FastAPI()
        @self._server.websocket_route("/")
        async def run_accept(ws : WebSocket):
            await ws.accept()
            while True:
                data = await ws.receive_json()
                log.debug("Server < %r", data)

                try:
                    endpoint = data['endpoint']
                except KeyError:
                    headers = data.get('headers')

                    if not headers or headers.get("Authorization") != self.secret_key:
                        response = {"error": "Invalid or no token provided.", "code": 403}
                    else:
                        response = {
                            "message": "Connection success",
                            "port": self.port,
                            "code": 200,
                        }

                    log.debug("Server > %r", response)

                    await ws.send_json(response)
                else:
                    self.update_endpoints()
                    endpoint = data['endpoint']
                    headers = data.get('headers')
                    log.info("Initiating IPC Server.")
                    if not headers or headers.get("Authorization") != self.secret_key:
                        log.info("Received unauthorized request (Invalid or no token provided).")
                        response = {"error": "Invalid or no token provided.", "code": 403}
                    else:
                        if not endpoint or endpoint not in self.endpoints:
                            log.info("Received invalid request (Invalid or no endpoint given).")
                            response = {"error": "Invalid or no endpoint given.", "code": 400}
                        else:
                            server_response = IpcServerResponse(data)
                        try:
                            attempted_cls = self.bot.cogs.get(
                                self.endpoints[endpoint].__qualname__.split(".")[0]
                            )

                            if attempted_cls:
                                arguments = (attempted_cls, server_response)
                            else:
                                arguments = (server_response,)
                        except AttributeError:
                            # Support base Client
                            arguments = (server_response,)

                        try:
                            ret = await self.endpoints[endpoint](*arguments)
                            response = ret
                        except Exception as error:
                            log.error(
                                "Received error while executing %r with %r",
                                endpoint,
                                data,
                            )
                            self.bot.dispatch("ipc_error", endpoint, error)

                            response = {
                                "error": "IPC route raised error of type {}".format(
                                    type(error).__name__
                                ),
                                "code": 500,
                            }

                        try:
                            await ws.send_json(response)
                            log.debug("IPC Server > %r", response)
                        except TypeError as error:
                            if str(error).startswith("Object of type") and str(error).endswith(
                                "is not JSON serializable"
                            ):
                                error_response = (
                                    "IPC route returned values which are not able to be sent over sockets."
                                    " If you are trying to send a discord.py object,"
                                    " please only send the data you need."
                                )
                                log.error(error_response)

                                response = {"error": error_response, "code": 500}

                                await ws.send_json(response)
                                log.debug("IPC Server > %r", response)

                                raise JSONEncodeError(error_response)

        with __import__("contextlib").suppress(TypeError):
            try:
                stuff = self.loop.create_task(self.__start(self._server))
                print(stuff.result())
            except KeyboardInterrupt:
                sys.exit(1)
