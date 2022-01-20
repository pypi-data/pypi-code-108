import asyncio
import os
from functools import lru_cache
from typing import Any, Dict, Optional

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import LiveLogger
from nautilus_trader.common.logging import Logger
from nautilus_trader.live.factories import LiveDataClientFactory
from nautilus_trader.live.factories import LiveExecutionClientFactory
from nautilus_trader.model.identifiers import AccountId
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.msgbus.bus import MessageBus

from nacre.adapters.zb.data import ZbDataClient
from nacre.adapters.zb.data import ZbFutureDataClient
from nacre.adapters.zb.data import ZbSpotDataClient
from nacre.adapters.zb.execution import ZbFutureExecutionClient
from nacre.adapters.zb.execution import ZbSpotExecutionClient
from nacre.adapters.zb.http.api.future_market import ZbFutureMarketHttpAPI
from nacre.adapters.zb.http.api.spot_market import ZbSpotMarketHttpAPI
from nacre.adapters.zb.http.client import ZbHttpClient

# from nacre.adapters.client.providers import ZB_VENUE
from nacre.adapters.zb.providers import ZbInstrumentProvider


HTTP_CLIENTS: Dict[str, ZbHttpClient] = {}


def get_cached_zb_http_client(
    loop: asyncio.AbstractEventLoop,
    clock: LiveClock,
    logger: Logger,
    key: Optional[str] = None,
    sec: Optional[str] = None,
    account_type: Optional[str] = None,
    proxy: Optional[str] = None,
) -> ZbHttpClient:

    global HTTP_CLIENTS
    key = key or os.environ.get("BINANCE_API_KEY", "")
    sec = sec or os.environ.get("BINANCE_API_SECRET", "")
    account_type = account_type or "future"

    client_key: str = "|".join((key, sec, account_type, str(proxy or "")))
    if client_key not in HTTP_CLIENTS:
        base_url = None
        if account_type == "future":
            base_url = "https://fapi.zb.com"
        elif account_type == "spot":
            base_url = "https://api.zb.team"

        client = ZbHttpClient(
            loop=loop,
            clock=clock,
            logger=logger,
            key=key,
            secret=sec,
            base_url=base_url,
            proxy=proxy,
        )
        HTTP_CLIENTS[client_key] = client
    return HTTP_CLIENTS[client_key]


@lru_cache(1)
def get_cached_zb_instrument_provider(
    client: ZbHttpClient,
    logger: Logger,
    venue: Venue,
    market_api: ZbFutureMarketHttpAPI,
    account_type: str,
) -> ZbInstrumentProvider:
    return ZbInstrumentProvider(
        client=client,
        logger=logger,
        venue=venue,
        market_api=market_api,
        account_type=account_type,
    )


class ZbLiveDataClientFactory(LiveDataClientFactory):
    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config: Dict[str, Any],
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: LiveLogger,
        client_cls=None,
    ) -> ZbDataClient:

        proxy = config.get("httpProxy", None)
        account_type_str = config.get("defaultType", "spot")
        client = get_cached_zb_http_client(
            account_type=account_type_str,
            loop=loop,
            clock=clock,
            logger=logger,
            proxy=proxy,
        )

        if account_type_str == "spot":
            venue = Venue("ZB_SPOT")
            market_api = ZbSpotMarketHttpAPI(client=client)
        elif account_type_str == "future":
            venue = Venue("ZB_FUTURE")
            market_api = ZbFutureMarketHttpAPI(client=client)
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")
        ins_client = get_cached_zb_http_client(
            account_type=account_type_str,
            loop=loop,
            clock=clock,
            logger=logger,
        )
        # Get instrument provider singleton
        provider = get_cached_zb_instrument_provider(
            client=ins_client,
            logger=logger,
            venue=venue,
            market_api=market_api,
            account_type=account_type_str,
        )

        # Create client
        if account_type_str == "spot":
            data_client = ZbSpotDataClient(
                loop=loop,
                client=client,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                venue=venue,
                instrument_provider=provider,
            )
        elif account_type_str == "future":
            data_client = ZbFutureDataClient(
                loop=loop,
                client=client,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                venue=venue,
                instrument_provider=provider,
            )
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")

        return data_client


class ZbLiveExecutionClientFactory(LiveExecutionClientFactory):
    @staticmethod
    def create(
        loop: asyncio.AbstractEventLoop,
        name: str,
        config,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: LiveLogger,
        client_cls=None,
    ):

        proxy = config.get("httpProxy", None)
        socks_proxy = config.get("socksProxy", None)
        account_type_str = config.get("defaultType", "spot")
        client = get_cached_zb_http_client(
            key=config.get("api_key"),
            sec=config.get("api_secret"),
            loop=loop,
            clock=clock,
            logger=logger,
            account_type=account_type_str,
            proxy=proxy,
        )

        if account_type_str == "spot":
            venue = Venue("ZB_SPOT")
            market_api = ZbSpotMarketHttpAPI(client=client)
        elif account_type_str == "future":
            venue = Venue("ZB_FUTURE")
            market_api = ZbFutureMarketHttpAPI(client=client)
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")

        ins_client = get_cached_zb_http_client(
            loop=loop,
            clock=clock,
            logger=logger,
            account_type=account_type_str,
        )

        provider = get_cached_zb_instrument_provider(
            client=ins_client,
            logger=logger,
            venue=venue,
            market_api=market_api,
            account_type=account_type_str,
        )

        account_id = AccountId.from_str(name)

        if account_type_str == "spot":
            exec_client = ZbSpotExecutionClient(
                loop=loop,
                client=client,
                name=name,
                account_id=account_id,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                instrument_provider=provider,
            )
        elif account_type_str == "future":
            exec_client = ZbFutureExecutionClient(
                loop=loop,
                client=client,
                name=name,
                account_id=account_id,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                instrument_provider=provider,
                socks_proxy=socks_proxy,
            )
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")

        return exec_client
