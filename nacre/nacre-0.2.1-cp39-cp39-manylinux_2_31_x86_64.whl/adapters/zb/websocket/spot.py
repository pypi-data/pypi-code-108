import asyncio
from typing import Callable

from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger

from nacre.adapters.zb.common import format_websocket_market
from nacre.adapters.zb.websocket.client import ZbWebSocketClient


class ZbSpotWebSocket(ZbWebSocketClient):
    """
    Provides access to the `Zb SPOT` streaming WebSocket API.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        clock: LiveClock,
        logger: Logger,
        handler: Callable[[bytes], None],
    ):
        super().__init__(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=handler,
            base_url="wss://api.zb.company/websocket",
        )

    async def on_post_connect(self):
        if self._subscriptions:
            await self._resubscribe()

    async def ping(self):
        await self.send("ping".encode())

    async def _subscribe_channel(self, channel: str, **kwargs):
        kwargs["event"] = "addChannel"

        await super()._subscribe_channel(channel, **kwargs)

    async def subscribe_markets(self):
        await self._subscribe_channel(channel="markets")

    async def subscribe_ticker(self, symbol: str):
        channel = f"{format_websocket_market(symbol)}_ticker"
        await self._subscribe_channel(channel=channel)

    async def subscribe_depth(self, symbol: str):
        channel = f"{format_websocket_market(symbol)}_depth"
        await self._subscribe_channel(channel=channel)

    async def subscribe_trades(self, symbol: str):
        channel = f"{format_websocket_market(symbol)}_trades"
        await self._subscribe_channel(channel=channel)
