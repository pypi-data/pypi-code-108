import asyncio
import base64
import hashlib
import hmac
import json
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional  # noqa: TYP001

import orjson
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger

from nacre.adapters.zb.common import format_market
from nacre.adapters.zb.common import format_symbol
from nacre.adapters.zb.websocket.client import ZbWebSocketClient


class ZbSpotUserDataWebSocket(ZbWebSocketClient):
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
            base_url="wss://api.zb.company/websocket",
            socks_proxy=socks_proxy,
        )

        self._key = key
        self._hashed_secret = hashed_secret
        self.is_logged_in = False
        self._post_connect_callbacks: List[Callable[..., Awaitable]] = []

    async def ping(self):
        await self.send("ping".encode())

    def add_after_connect_callback(self, callback: Callable[..., Awaitable]):
        self._post_connect_callbacks.append(callback)

    async def on_post_connect(self):
        await self.subscribe_asset_snapshot()
        for callback in self._post_connect_callbacks:
            await callback()

        self.is_logged_in = True

    async def _subscribe_channel(self, channel: str, **kwargs):
        kwargs["event"] = "addChannel"
        kwargs["accesskey"] = self._key
        kwargs["sign"] = self._get_sign(channel, kwargs)
        await super()._subscribe_channel(channel, **kwargs)

    async def logged_in(self):
        while not self.is_logged_in:
            await self._sleep0()
        self._log.debug("Websocket logged in")

    def _get_sign(self, channel: str, payload: Dict[str, Any]) -> str:
        params = {"channel": channel, **payload}
        sorted_params = dict(sorted(params.items()))
        query_string = json.dumps(sorted_params, separators=(",", ":"))
        return hmac.new(
            bytes(self._hashed_secret, encoding="utf-8"), query_string.encode("utf-8"), hashlib.md5
        ).hexdigest()

    async def subscribe_recent_order(self, market: str) -> None:
        payload = {
            "market": f"{format_market(market)}",
        }
        await self._subscribe_channel(channel="push_user_record", **payload)

    async def subscribe_order_update(self, market: str) -> None:
        payload = {
            "market": f"{format_market(market)}",
        }
        await self._subscribe_channel(channel="push_user_incr_record", **payload)

    async def subscribe_asset_snapshot(self):
        await self._subscribe_channel(channel="push_user_asset")

    async def subscribe_asset_update(self):
        await self._subscribe_channel(channel="push_user_incr_asset")

    async def get_account_info(self):
        payload = {"no": str(int(time.time() * 1000))}
        await self._subscribe_channel(channel="getaccountinfo", **payload)


class ZbFutureUserDataWebSocket(ZbWebSocketClient):
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

    async def _subscribe_channel(self, channel: str, **kwargs):
        kwargs["action"] = "subscribe"

        await super()._subscribe_channel(channel, **kwargs)

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

    async def on_post_connect(self):
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

    async def get_asset_snapshot(self, currency: str):
        await self._subscribe_channel(
            channel="Fund.balance", futuresAccountType=1, currency=currency
        )

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
