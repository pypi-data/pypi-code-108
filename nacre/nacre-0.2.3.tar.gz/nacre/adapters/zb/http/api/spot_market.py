from typing import Any, Dict, Optional

from nautilus_trader.core.correctness import PyCondition

from nacre.adapters.zb.common import format_market
from nacre.adapters.zb.http.spot import ZbSpotHttpClient


class ZbSpotMarketHttpAPI:
    """
    Provides access to the `ZB FUTURE Market` HTTP REST API.
    """

    BASE_ENDPOINT = "/data/v1/"

    def __init__(self, client: ZbSpotHttpClient):
        """
        Initialize a new instance of the ``ZbSpotMarketHttpAPI`` class.

        Parameters
        ----------
        client : ZbSpotHttpClient
            The Binance REST API client.

        """
        PyCondition.not_none(client, "client")

        self.client = client

    async def markets(self) -> Dict[str, Any]:
        return await self.client.query(
            url_path=self.BASE_ENDPOINT + "markets",
        )

    async def all_ticker(self) -> Dict[str, Any]:
        return await self.client.query(url_path=self.BASE_ENDPOINT + "allTicker")

    async def ticker(self, market: str) -> Dict[str, Any]:
        payload: Dict[str, str] = {"market": format_market(market)}

        return await self.client.query(
            url_path=self.BASE_ENDPOINT + "ticker",
            payload=payload,
        )

    async def depth(
        self, market: str, size: Optional[int] = None, merge: Optional[float] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"market": format_market(market)}
        if size is not None:
            payload["size"] = size
        if merge is not None:
            payload["merge"] = merge

        return await self.client.query(
            url_path=self.BASE_ENDPOINT + "depth",
            payload=payload,
        )

    async def trades(self, market: str, since: Optional[int] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"market": format_market(market)}
        if since is not None:
            payload["since"] = since

        return await self.client.query(
            url_path=self.BASE_ENDPOINT + "trades",
            payload=payload,
        )

    async def kline(
        self,
        market: str,
        type: Optional[str] = None,
        since: Optional[int] = None,
        size: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"market": format_market(market)}
        if type is not None:
            payload["type"] = type
        if since is not None:
            payload["since"] = since
        if size is not None:
            payload["size"] = size

        return await self.client.query(
            url_path=self.BASE_ENDPOINT + "kline",
            payload=payload,
        )
