import asyncio
import base64
import hashlib
import hmac
from typing import Any, Callable, Dict, Optional

import orjson
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger

from nacre.adapters.zb.common import format_symbol
from nacre.adapters.zb.websocket.client import ZbWebSocketClient


class ZbUserDataWebSocket(ZbWebSocketClient):
    """
    Provides access to the `Zb User Data` streaming WebSocket API.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        clock: LiveClock,
        logger: Logger,
        handler: Callable[[bytes], None],
        key: str,
        hashed_secret: str,
        socks_proxy: str = None,
    ):
        super().__init__(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=handler,
            base_url="wss://fapi.zb.com/ws/private/api/v2",
            socks_proxy=socks_proxy,
        )

        self._key = key
        self._hashed_secret = hashed_secret
        self.is_logged_in = False

    def _get_sign(self, timestamp, http_method, url_path) -> str:
        whole_data = timestamp + http_method + url_path
        m = hmac.new(self._hashed_secret.encode(), whole_data.encode(), hashlib.sha256)
        return str(base64.b64encode(m.digest()), "utf-8")

    async def _login(self):
        """
        Login to the user data stream.

        """
        timestamp = self._clock.utc_now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        signature = self._get_sign(timestamp, "GET", "login")
        payload = {
            "action": "login",
            "ZB-APIKEY": self._key,
            "ZB-TIMESTAMP": timestamp,
            "ZB-SIGN": signature,
        }

        await self.send(orjson.dumps(payload))

    async def logged_in(self):
        while not self.is_logged_in:
            await self._sleep0()
        self._log.debug("Websocket logged in")


class ZbSpotUserDataWebSocket(ZbUserDataWebSocket):
    pass


class ZbFutureUserDataWebSocket(ZbUserDataWebSocket):
    async def post_connect(self):
        # Multiple writer should exist in other tasks
        # Ref: https://docs.aiohttp.org/en/stable/client_quickstart.html#websockets
        self._loop.create_task(self._prepare_user_stream())

    async def _prepare_user_stream(self):
        await self._login()

        await self.subscribe_asset_update()
        await self.subscribe_position_update()
        await self.subscribe_order_update()

        self.is_logged_in = True

    async def subscribe_funding_update(self, currency: str):
        await self._subscribe_channel(
            channel="Fund.change", futuresAccountType=1, currency=currency
        )

    async def subscribe_asset_update(self):
        await self._subscribe_channel(channel="Fund.assetChange", futuresAccountType=1)

    async def subscribe_position_update(self, symbol: Optional[str] = None):
        payload: Dict[str, Any] = {"futuresAccountType": 1}
        if symbol:
            payload["symbol"] = format_symbol(symbol)

        await self._subscribe_channel(channel="Positions.change", **payload)

    async def subscribe_order_update(self, symbol: Optional[str] = None):
        payload = {}
        if symbol:
            payload["symbol"] = format_symbol(symbol)

        await self._subscribe_channel(channel="Trade.orderChange", **payload)

    async def new_order(
        self,
        symbol: str,
        side: int,
        amount: float,
        price: Optional[float] = None,
        action: Optional[int] = None,
        client_order_id: Optional[str] = None,
    ):
        payload: Dict[str, Any] = {"symbol": format_symbol(symbol), "side": side, "amount": amount}
        if price is not None:
            payload["price"] = price
        if action is not None:
            payload["actionType"] = action
        if client_order_id is not None:
            payload["clientOrderId"] = client_order_id

        await self._subscribe_channel(channel="Trade.order", **payload)

    async def cancel_order(
        self,
        symbol: str,
        order_id: Optional[str] = None,
        client_order_id: Optional[str] = None,
    ):
        payload: Dict[str, Any] = {"symbol": format_symbol(symbol)}
        if order_id is not None:
            payload["orderId"] = order_id
        elif client_order_id is not None:
            payload["clientOrderId"] = client_order_id

        await self._subscribe_channel(channel="Trade.cancelOrder", **payload)

    async def cancel_open_orders(self, symbol: str):
        payload: Dict[str, Any] = {"symbol": format_symbol(symbol)}
        await self._subscribe_channel(channel="Trade.cancelAllOrders", **payload)

    async def get_trade_list(self, symbol: str, order_id: str):
        payload = {}
        payload["symbol"] = format_symbol(symbol)
        payload["orderId"] = order_id
        await self._subscribe_channel(channel="Trade.getTradeList", **payload)
