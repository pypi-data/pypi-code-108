import asyncio
from typing import Callable, Dict, List, Optional

import orjson
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger

from nacre.adapters.zb.common import format_symbol
from nacre.adapters.zb.websocket.client import ZbWebSocketClient


class ZbFuturesWebSocket(ZbWebSocketClient):
    """
    Provides access to the `Zb FUTURES` streaming WebSocket API.
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
            base_url="wss://fapi.zb.com/ws/public/v1",
        )
        self._subscriptions: List[Dict] = []

    async def post_connect(self):
        if self._subscriptions:
            self._loop.create_task(self._subscribe_existing_channels())

    async def _subscribe_existing_channels(self):
        for subscription in self._subscriptions:
            await self.send(orjson.dumps(subscription))

    async def _subscribe_channel(self, channel: str, **kwargs):
        payload = {
            "action": "subscribe",
            "channel": channel,
        }
        if kwargs:
            payload.update(kwargs)

        self._subscriptions.append(payload)
        while not self.is_connected:
            await self._sleep0()

        await self.send(orjson.dumps(payload))

    async def _unsubscribe_channel(self, channel: str):
        payload = {
            "action": "unsubscribe",
            "channel": channel,
        }
        await self.send(orjson.dumps(payload))

    async def subscribe_mark_price(self, symbol: str = None):
        chan = "All"
        if symbol:
            chan = format_symbol(symbol)
        await self._subscribe_channel(channel=f"{chan}.mark")

    async def subscribe_index_price(self, symbol: str = None):
        chan = "All"
        if symbol:
            chan = format_symbol(symbol)
        await self._subscribe_channel(channel=f"{chan}.index")

    async def subscribe_mark_bars(self, symbol: str, interval: str, size: int = 1):
        channel = f"{format_symbol(symbol)}.mark_{interval}"
        await self._subscribe_channel(channel=channel, size=size)

    async def subscribe_index_bars(self, symbol: str, interval: str, size: int = 1):
        channel = f"{format_symbol(symbol)}.index_{interval}"
        await self._subscribe_channel(channel=channel, size=size)

    async def subscribe_trades(self, symbol: str, size: int = 50):
        """
        Trade Streams.

        The Trade Streams push raw trade information; each trade has a unique buyer and seller.
        Update Speed: Real-time

        """
        await self._subscribe_channel(channel=f"{format_symbol(symbol)}.Trade", size=size)

    async def subscribe_bars(self, symbol: str, interval: str, size: int = 1):
        """
        Subscribe to bar (kline/candlestick) stream.

        The Kline/Candlestick Stream push updates to the current klines/candlestick every second.
        interval:
        1M,5M,15M, 30M, 1H, 6H, 1D, 5D
        Update Speed: 2000ms

        """
        channel = f"{format_symbol(symbol)}.KLine_{interval}"
        await self._subscribe_channel(channel=channel, size=size)

    async def subscribe_ticker(self, symbol: str = None):
        """
        Individual symbol or all symbols ticker.

        24hr rolling window ticker statistics for a single symbol.
        These are NOT the statistics of the UTC day, but a 24hr rolling window for the previous 24hrs.
        Stream Name: <symbol>@ticker or
        Stream Name: !ticker@arr
        Update Speed: 1000ms

        """
        if symbol is None:
            await self._subscribe_channel(channel="All.Ticker")
        else:
            await self._subscribe_channel(channel=f"{format_symbol(symbol)}.Ticker")

    async def subscribe_book_deltas(
        self, symbol: str, depth: int = 50, precision: Optional[float] = None
    ):
        """
        Partial Book Depth Streams.

        Top bids and asks, Valid are min - 5000, default 50
        Update Speed: real time

        """
        channel = f"{format_symbol(symbol)}.Depth"
        if precision:
            channel = f"{format_symbol(symbol)}.Depth@{precision}"
        await self._subscribe_channel(channel=channel, size=depth)

    async def subscribe_book_snapshot(
        self, symbol: str, depth: int = 5, precision: Optional[float] = None
    ):
        """
        Diff book depth stream.

        Top bids and asks, Valid are 5 - 10
        Update Speed: 200ms
        Order book price and quantity depth updates used to locally manage an order book.

        """
        channel = f"{format_symbol(symbol)}.DepthWhole"
        if precision:
            channel = f"{format_symbol(symbol)}.DepthWhole@{precision}"
        await self._subscribe_channel(channel=channel, size=depth)
