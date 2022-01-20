import asyncio
from typing import Callable

import orjson
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger

from nacre.network.websocket import WebSocketClient


class ZbWebSocketClient(WebSocketClient):
    """
    Provides a `Zb` streaming WebSocket client.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        clock: LiveClock,
        logger: Logger,
        handler: Callable[[bytes], None],
        base_url: str,
        socks_proxy: str = None,
    ):
        super().__init__(
            loop=loop,
            logger=logger,
            handler=handler,
            max_retry_connection=5,
            socks_proxy=socks_proxy,
        )

        self._base_url = base_url
        self._clock = clock

    async def connect(self, start: bool = True, **ws_kwargs) -> None:
        if "ws_url" in ws_kwargs:
            shadowed_ws_url = ws_kwargs.pop("ws_url")
            self._log.warning(
                f"Shadow parameters ws_url: {shadowed_ws_url}, override with {self._base_url}"
            )
        await super().connect(ws_url=self._base_url, start=start, **ws_kwargs)

    async def _subscribe_channel(self, channel: str, **kwargs):
        payload = {
            "action": "subscribe",
            "channel": channel,
        }
        if kwargs:
            payload.update(kwargs)

        while not self.is_connected:
            await self._sleep0()

        await self.send(orjson.dumps(payload))

    async def _unsubscribe_channel(self, channel: str):
        payload = {
            "action": "unsubscribe",
            "channel": channel,
        }
        await self.send(orjson.dumps(payload))

    async def close(self):
        for task in self._tasks:
            self._log.debug(f"Canceling {task}...")
            task.cancel()
