import asyncio
from datetime import timedelta
from typing import Callable, Dict

import orjson
from aiohttp import ClientConnectorError
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger
from nautilus_trader.common.timer import TimeEvent
from nautilus_trader.common.uuid import UUIDFactory
from tenacity import retry
from tenacity.retry import retry_if_exception_type

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
        self._subscriptions: Dict = {}
        self._pager_name = None

    def _set_up_pager(self):
        self._pager_name = UUIDFactory().generate().value
        self._clock.set_timer(
            name=self._pager_name,
            interval=timedelta(seconds=3),  # Ping interval Hardcoded for now
            start_time=None,
            stop_time=None,
            callback=self._on_pager_inteval,
        )

    def _on_pager_inteval(self, event: TimeEvent):
        self._loop.create_task(self.ping())

    async def ping(self):
        await self.send(orjson.dumps({"action": "ping"}))

    async def post_connect(self):
        # Multiple writer should exist in other tasks
        # Ref: https://docs.aiohttp.org/en/stable/client_quickstart.html#websockets
        self._loop.create_task(self._post_connect())

    async def _post_connect(self):
        if self._pager_name is None:
            self._set_up_pager()

        await self.on_post_connect()

    async def on_post_connect(self):
        """Abstract method (implement in subclass)."""
        raise NotImplementedError("method must be implemented in the subclass")  # pragma: no cover

    async def post_disconnect(self):
        if self._pager_name:
            self._clock.cancel_timer(self._pager_name)
            self._pager_name = None

    async def _resubscribe(self):
        for channel, subscription in self._subscriptions.items():
            self._log.debug(f"Resubscribe channel {channel} ... {subscription}")
            await self.send(orjson.dumps(subscription))

    @retry(retry=retry_if_exception_type(ClientConnectorError))
    async def connect(self, start: bool = True, **ws_kwargs) -> None:
        if "ws_url" in ws_kwargs:
            ws_kwargs.pop("ws_url")
        try:
            await super().connect(ws_url=self._base_url, start=start, **ws_kwargs)
        except ClientConnectorError as ex:
            self._log.warning(f"{ex}, Retrying...")
            raise ex

    async def _subscribe_channel(self, channel: str, **kwargs):
        payload = {"channel": channel}
        if kwargs:
            payload.update(kwargs)

        self._subscriptions[channel] = payload
        while not self.is_connected:
            await self._sleep0()

        await self.send(orjson.dumps(payload))

    async def _unsubscribe_channel(self, channel: str, **kwargs):
        payload = {"channel": channel}
        if kwargs:
            payload.update(kwargs)

        self._subscriptions.pop(channel, None)
        await self.send(orjson.dumps(payload))
