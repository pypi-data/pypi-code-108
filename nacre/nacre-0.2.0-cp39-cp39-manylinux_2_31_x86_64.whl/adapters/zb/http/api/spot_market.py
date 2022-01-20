from nautilus_trader.core.correctness import PyCondition

from nacre.adapters.zb.http.client import ZbHttpClient


class ZbSpotMarketHttpAPI:
    """
    Provides access to the `ZB FUTURE Market` HTTP REST API.
    """

    BASE_ENDPOINT = "/api/public/v1/"

    def __init__(self, client: ZbHttpClient):
        """
        Initialize a new instance of the ``ZbSpotMarketHttpAPI`` class.

        Parameters
        ----------
        client : ZbHttpClient
            The Binance REST API client.

        """
        PyCondition.not_none(client, "client")

        self.client = client

    # async def market_list(self) -> Dict[str, Any]:
    #
    #     return await self.client.query(
    #         url_path="/Server/api/v2/" + "config/marketList",
    #     )
    #
    # async def depth(self, symbol: str, size: Optional[int] = None, scale: Optional[int] = None) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {"symbol": format_symbol(symbol).upper()}
    #     if size is not None:
    #         payload["size"] = str(size)
    #     if scale is not None:
    #         payload["scale"] = str(scale)
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "depth",
    #         payload=payload,
    #     )
    #
    # async def trades(self, symbol: str, size: Optional[int] = None) -> List[Dict[str, Any]]:
    #     payload: Dict[str, str] = {"symbol": format_symbol(symbol).upper()}
    #     if size is not None:
    #         payload["size"] = str(size)
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "trade",
    #         payload=payload,
    #     )
    #
    # async def klines(
    #     self,
    #     symbol: str,
    #     period: str,
    #     size: Optional[int] = None,
    # ) -> List[List[Any]]:
    #     payload: Dict[str, str] = {
    #         "symbol": format_symbol(symbol).upper(),
    #         "period": period,
    #     }
    #     if size is not None:
    #         payload["size"] = str(size)
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "kline",
    #         payload=payload,
    #     )
    #
    # async def mark_klines(
    #     self,
    #     symbol: str,
    #     period: str,
    #     size: Optional[int] = None,
    # ) -> List[List[Any]]:
    #     payload: Dict[str, str] = {
    #         "symbol": format_symbol(symbol).upper(),
    #         "period": period,
    #     }
    #     if size is not None:
    #         payload["size"] = str(size)
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "markKline",
    #         payload=payload,
    #     )
    #
    # async def index_klines(
    #     self,
    #     symbol: str,
    #     period: str,
    #     size: Optional[int] = None,
    # ) -> List[List[Any]]:
    #     payload: Dict[str, str] = {
    #         "symbol": format_symbol(symbol).upper(),
    #         "period": period,
    #     }
    #     if size is not None:
    #         payload["size"] = str(size)
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "indexKline",
    #         payload=payload,
    #     )
    #
    # async def ticker_price(self, symbol: str = None) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {}
    #     if symbol is not None:
    #         payload["symbol"] = format_symbol(symbol).upper()
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "ticker",
    #         payload=payload,
    #     )
    #
    # async def mark_price(self, symbol: str = None) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {}
    #     if symbol is not None:
    #         payload["symbol"] = format_symbol(symbol).upper()
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "markPrice",
    #         payload=payload,
    #     )
    #
    # async def index_price(self, symbol: str = None) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {}
    #     if symbol is not None:
    #         payload["symbol"] = format_symbol(symbol).upper()
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "indexPrice",
    #         payload=payload,
    #     )
    #
    # async def premium_index(self, symbol: str = None) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {}
    #     if symbol is not None:
    #         payload["symbol"] = format_symbol(symbol).upper()
    #
    #     return await self.client.query(
    #         url_path="/Server/api/v2/" + "premiumIndex",
    #         payload=payload,
    #     )
    #
    # async def historical_funding_rate(
    #     self,
    #     symbol: str = None,
    #     start_time_ms: Optional[int] = None,
    #     end_time_ms: Optional[int] = None,
    #     limit: Optional[int] = None,
    # ) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {}
    #     if symbol is not None:
    #         payload["symbol"] = format_symbol(symbol).upper()
    #     if start_time_ms is not None:
    #         payload["startTime"] = str(start_time_ms)
    #     if end_time_ms is not None:
    #         payload["endTime"] = str(end_time_ms)
    #     if limit is not None:
    #         payload["limit"] = str(limit)
    #
    #     return await self.client.query(
    #         url_path="/Server/api/v2/" + "fundingRate",
    #         payload=payload,
    #     )
    #
    # async def historical_liquidated_orders(
    #     self,
    #     symbol: str = None,
    #     start_time_ms: Optional[int] = None,
    #     end_time_ms: Optional[int] = None,
    #     limit: Optional[int] = None,
    # ) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {}
    #     if symbol is not None:
    #         payload["symbol"] = format_symbol(symbol).upper()
    #     if start_time_ms is not None:
    #         payload["startTime"] = str(start_time_ms)
    #     if end_time_ms is not None:
    #         payload["endTime"] = str(end_time_ms)
    #     if limit is not None:
    #         payload["limit"] = str(limit)
    #
    #     return await self.client.query(
    #         url_path="/Server/api/v2/" + "allForceOrders",
    #         payload=payload,
    #     )
    #
    # async def funding_rate(self, symbol: str) -> Dict[str, Any]:
    #     payload: Dict[str, str] = {"symbol": format_symbol(symbol).upper()}
    #
    #     return await self.client.query(
    #         url_path=self.BASE_ENDPOINT + "fundingRate",
    #         payload=payload,
    #     )
