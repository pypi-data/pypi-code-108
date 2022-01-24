import asyncio
from typing import Callable, Optional

from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger

from nacre.adapters.binance.websocket.client import BinanceWebSocketClient


class BinanceUserDataWebSocket(BinanceWebSocketClient):
    """
    Provides access to the `Binance User Data` streaming WebSocket API.
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
            base_url="wss://stream.binance.com:9443",
        )

    def subscribe(self, key: str):
        """
        Subscribe to the user data stream.

        Parameters
        ----------
        key : str
            The listen key for the subscription.

        """
        self._add_stream(key)


class BinanceSpotUserDataWebSocket(BinanceUserDataWebSocket):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        clock: LiveClock,
        logger: Logger,
        handler: Callable[[bytes], None],
        testnet: Optional[bool] = False,
    ):
        super(BinanceUserDataWebSocket, self).__init__(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=handler,
            base_url="wss://stream.binance.com:9443"
            if not testnet
            else "wss://testnet.binance.vision",
        )


class BinanceFutureUserDataWebSocket(BinanceUserDataWebSocket):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        clock: LiveClock,
        logger: Logger,
        handler: Callable[[bytes], None],
        testnet: Optional[bool] = False,
    ):
        super(BinanceUserDataWebSocket, self).__init__(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=handler,
            base_url="wss://fstream.binance.com"
            if not testnet
            else "wss://stream.binancefuture.com",
        )
