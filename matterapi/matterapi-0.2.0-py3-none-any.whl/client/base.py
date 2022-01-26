import abc
import asyncio
import inspect
import json
import logging
import socket
from typing import Any, Callable, Dict, Optional, Union
from urllib.parse import urljoin, urlparse

import httpx
import websockets
from pydantic import AnyHttpUrl, AnyUrl, BaseModel, validator

logger = logging.getLogger("matterapi.client")
logger.setLevel(logging.INFO)


class HttpxClientOptions(BaseModel):
    """Options for the httpx client"""

    class Config:
        extra = "allow"
        arbitrary_types_allowed = True

    timeout: Optional[Any] = 10.0
    """ Timeout for operations """
    verify: Union[bool, Any] = True
    """ If and how TLS should be verified. """
    cert: Optional[Any] = None
    proxies: Optional[Dict] = None
    auth: Optional[Any] = None


class AuthLogin(BaseModel):
    """Mattermost Auhentication Credentials"""

    login_id: str
    """ Login id for authentication """
    password: str
    """ Password """
    mfa_token: Optional[str]
    """ MultiFactorAuthentication token """


class AuthToken(httpx.Auth, BaseModel):
    """Mattermost Auhentication Token"""

    token: str
    """ Bearer Authentication token"""

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class ApiClientOptions(BaseModel):
    """Options to be passed to a api client"""

    url: AnyHttpUrl
    """ Mattermost base url

        Example: https://localhost:8065
    """
    ws_url: Optional[AnyUrl]
    """ Mattermost websocket url """
    basepath: str = "/api/v4"
    """ API path. Usually you won't need to change this """
    auth: Optional[Union[AuthLogin, AuthToken]]
    """ Authentication information for the client

    Provide login information for tasks which require authentication.
    If set, this can be an instance of :class:`.AuthLogin` or :class:`.AuthToken`
    """
    httpx_client_options: Optional[HttpxClientOptions]
    """ Options to be passed to the underlying http client doing the actual requests """
    debug: bool = False
    """ Set to ``true`` to enable debugging """
    ws_concurrent: bool = True
    """ Change handling behaviour of websocket messages

    If set to true, websocket messages will be handled concurrently.
    This means that the loop will not wait until messages are handled
    but continue to wait/handle the next message. If set to false,
    messages will be handled sequentially. Handling of a new message
    only starts after the event_handler returns.
    """
    ws_reconnect_wait_time: int = 5
    """ The waiting time between re-connect attempts for websocket connections """
    skip_response_parsing: bool = False
    """ If this is set, responses will not be parsed into objects, but
        will be returned as raw httpx response """

    @validator("ws_url", pre=True, always=True)
    def _ws_url_setter(cls, v, values):
        """Set the websocket url from the url if not set explicitly"""
        if v is None:
            if "url" in values:
                url = urlparse(values["url"])
                scheme_map = {"https": "wss", "http": "ws"}
                url = url._replace(scheme=scheme_map[url.scheme])
                return url.geturl()
        else:
            return v

        raise ValueError(
            "Url is not present in values and ws_url was not set explicitly"
        )


class BaseClient(BaseModel, metaclass=abc.ABCMeta):
    """
    Contains shared business logic of Sync and Async client for interacting with the mattermost api
    """

    options: ApiClientOptions
    """ Options to be passed to the client """
    active_token: Optional[str]
    """ The currently active authentication token.

    This will either be the token passed as :class:~AuthToken or the session token acquired
    through username/password based authentication.
    Used for websocket connections
    """

    @validator("options")
    def set_logging_mode(cls, v):
        if v.debug:
            logger.setLevel(logging.DEBUG)
        return v

    @abc.abstractmethod
    async def _login(self):
        pass

    async def _relogin(self):
        if inspect.iscoroutinefunction(self._login):
            await self._login()
        else:
            await asyncio.to_thread(self._login)

    async def start_ws(self, event_handler: Callable, relogin=False):
        """Start the websocket connection and pass messages to event_handler

        Connects to the websocket, completes authentication, and
        handles incoming messages. Will automatically try to reconnect
        to the server on connection errors.

        Args:
            event_handler: The message handler. Can be a function or coroutine.
                Get's the message passed as argument
            relogin: Set to ``True`` to run _login() after a connection error.
                This might be useful in case a session ends for username/password based logins
                and you need to acquire a new session token.
        """

        while True:
            try:
                await self._start_ws(event_handler)
            except (
                socket.gaierror,
                websockets.exceptions.ConnectionClosedError,
                ConnectionRefusedError,
            ) as e:
                logger.info(
                    (
                        "Connection to websocket closed. Either the server is not"
                        "reachable or authentication failed. Reconnecting in %s seconds"
                    ),
                    self.options.ws_reconnect_wait_time,
                    exc_info=True,
                )
                logger.info(e)
            except websockets.exceptions.WebSocketException:
                logger.exception("Got an unexpected exception from websocktes")

            await asyncio.sleep(self.options.ws_reconnect_wait_time)

            if relogin:
                await self._relogin()

    def start_ws_sync(self, event_handler: Callable, relogin=False):
        """Same as `.start_ws` but wraps the async call to be called synchronously"""
        asyncio.run(self.start_ws(event_handler, relogin))

    async def _handle_messages(self, event_handler: Callable, message: Dict):
        if inspect.iscoroutinefunction(event_handler):
            return asyncio.create_task(event_handler(message))
        else:
            return asyncio.create_task(asyncio.to_thread(event_handler, message))

    async def _handle_message_async(self, event_handler: Callable, websocket):
        async for raw_message in websocket:
            message = json.loads(raw_message)
            await asyncio.to_thread(event_handler, message)

    async def _start_ws(self, event_handler: Callable):
        json_auth_data = json.dumps(
            {
                "seq": 1,
                "action": "authentication_challenge",
                "data": {"token": self.active_token},
            }
        ).encode("utf8")

        logger.info("Connecting to websocket")
        ws_url = urljoin(self.options.ws_url, "api/v4/websocket")
        async with websockets.connect(ws_url) as websocket:
            # Authenticate
            await websocket.send(json_auth_data)
            hello = json.loads(await websocket.recv())
            logger.debug("%s", hello)
            logger.info(
                "Connected to Mattermost server: %s", hello["data"]["server_version"]
            )
            # Wait for authentication 'OK'
            async for raw_message in websocket:
                message = json.loads(raw_message)
                logger.debug("%s", message)
                if message.get("seq_reply", None) == 1:
                    if message["status"] == "OK":
                        logger.info("Successfully authenticated to websocket")
                        break
                logger.info(
                    "Got a stray message during authentication procedure: %s", message
                )
            tasks = set()
            while True:
                try:
                    raw_message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    message = json.loads(raw_message)
                    task = await self._handle_messages(event_handler, message)
                    if self.options.ws_concurrent:
                        tasks.add(task)
                    else:
                        await task
                except asyncio.TimeoutError:
                    ...
                # In case we handle tasks concurrently we will want to collect results/exceptions
                for task in list(tasks):
                    if task.done():
                        try:
                            await task
                        except Exception:
                            logger.exception("Websocket task failed")
                        tasks.remove(task)
