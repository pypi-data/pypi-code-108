from typing import Any, Dict

from nautilus_trader.adapters.binance.http.api.user import (
    BinanceUserDataHttpAPI as _BinanceUserDataHttpAPI,
)


class BinanceUserDataHttpAPI(_BinanceUserDataHttpAPI):
    async def create_listen_key(self) -> Dict[str, Any]:
        raise NotImplementedError("method must be implemented in the subclass")  # pragma: no cover

    async def ping_listen_key(self, key: str) -> Dict[str, Any]:
        raise NotImplementedError("method must be implemented in the subclass")  # pragma: no cover

    async def close_listen_key(self, key: str) -> Dict[str, Any]:
        raise NotImplementedError("method must be implemented in the subclass")  # pragma: no cover


class BinanceSpotUserDataHttpAPI(BinanceUserDataHttpAPI):
    async def create_listen_key(self) -> Dict[str, Any]:
        return await super(BinanceUserDataHttpAPI, self).create_listen_key_spot()

    async def ping_listen_key(self, key: str) -> Dict[str, Any]:
        return await super(BinanceUserDataHttpAPI, self).ping_listen_key_spot(key)

    async def close_listen_key(self, key: str) -> Dict[str, Any]:
        return await super(BinanceUserDataHttpAPI, self).close_listen_key_spot(key)


class BinanceMarginUserDataHttpAPI(BinanceUserDataHttpAPI):
    async def create_listen_key(self) -> Dict[str, Any]:
        return await super(BinanceUserDataHttpAPI, self).create_listen_key_margin()

    async def ping_listen_key(self, key: str) -> Dict[str, Any]:
        return await super(BinanceUserDataHttpAPI, self).ping_listen_key_margin(key)

    async def close_listen_key(self, key: str) -> Dict[str, Any]:
        return await super(BinanceUserDataHttpAPI, self).close_listen_key_margin(key)


class BinanceFutureUserDataHttpAPI(BinanceUserDataHttpAPI):
    BASE_ENDPOINT_FUTURE = "/fapi/v1/listenKey"

    async def create_listen_key(self) -> Dict[str, Any]:
        return await self.client.send_request(
            http_method="POST",
            url_path=self.BASE_ENDPOINT_FUTURE,
        )

    async def ping_listen_key(self, key: str) -> Dict[str, Any]:
        return await self.client.send_request(
            http_method="PUT",
            url_path=self.BASE_ENDPOINT_FUTURE,
            payload={"listenKey": key},
        )

    async def close_listen_key(self, key: str) -> Dict[str, Any]:
        return await self.client.send_request(
            http_method="DELETE",
            url_path=self.BASE_ENDPOINT_FUTURE,
            payload={"listenKey": key},
        )
