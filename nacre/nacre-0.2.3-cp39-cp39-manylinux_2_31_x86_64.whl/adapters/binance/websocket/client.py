import asyncio
from typing import Awaitable, Callable, List  # noqa: TYP001

from aiohttp import ClientConnectorError
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger
from tenacity import retry
from tenacity.retry import retry_if_exception_type

from nacre.network.websocket import WebSocketClient


class BinanceWebSocketClient(WebSocketClient):
    """
    Provides a `Binance` streaming WebSocket client.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        clock: LiveClock,
        logger: Logger,
        handler: Callable[[bytes], None],
        base_url: str,
    ):
        super().__init__(
            loop=loop,
            logger=logger,
            handler=handler,
            max_retry_connection=5,
        )

        self._base_url = base_url
        self._clock = clock
        self._streams: List[str] = []
        self._post_connect_callbacks: List[Callable[..., Awaitable]] = []

    @property
    def subscriptions(self):
        return self._streams.copy()

    @property
    def has_subscriptions(self):
        if self._streams:
            return True
        else:
            return False

    @retry(retry=retry_if_exception_type(ClientConnectorError))
    async def connect(self, start: bool = True, **ws_kwargs) -> None:
        if not self._streams:
            raise RuntimeError("No subscriptions for connection.")

        # Always connecting combined streams for consistency
        ws_url = self._base_url + "/stream?streams=" + "/".join(self._streams)
        if "ws_url" in ws_kwargs:
            shadowed_ws_url = ws_kwargs.pop("ws_url")
            self._log.warning(
                f"Shadow parameters ws_url: {shadowed_ws_url}, override with {ws_url}"
            )
        try:
            await super().connect(ws_url=ws_url, start=start, **ws_kwargs)
        except ClientConnectorError as ex:
            self._log.warning(f"{ex}, Retrying...")
            raise ex

    def _add_stream(self, stream: str):
        if stream not in self._streams:
            self._streams.append(stream)

    def add_after_connect_callback(self, callback: Callable[..., Awaitable]):
        self._post_connect_callbacks.append(callback)

    async def post_connect(self):
        # Multiple writer should exist in other tasks
        # Ref: https://docs.aiohttp.org/en/stable/client_quickstart.html#websockets
        self._loop.create_task(self._post_connect())

    async def _post_connect(self):
        for callback in self._post_connect_callbacks:
            await callback()
