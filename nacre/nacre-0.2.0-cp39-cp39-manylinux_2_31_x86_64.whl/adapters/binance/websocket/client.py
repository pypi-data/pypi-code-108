import asyncio
from typing import Callable, List, Optional

from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger

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
        self._reconnect_callback: Optional[Callable] = None

    @property
    def subscriptions(self):
        return self._streams.copy()

    @property
    def has_subscriptions(self):
        if self._streams:
            return True
        else:
            return False

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
        await super().connect(ws_url=ws_url, start=start, **ws_kwargs)

    def _add_stream(self, stream: str):
        if stream not in self._streams:
            self._streams.append(stream)

    def set_reconnect_callback(self, callback: Callable):
        self._reconnect_callback = callback

    async def post_connect(self):
        if self._reconnect_callback is not None:
            self._loop.create_task(self._reconnect_callback())
