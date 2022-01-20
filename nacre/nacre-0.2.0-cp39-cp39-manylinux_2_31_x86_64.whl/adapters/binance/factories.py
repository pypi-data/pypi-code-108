# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2021 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

import asyncio
import os
from functools import lru_cache
from typing import Any, Dict, Optional

from nautilus_trader.adapters.binance.http.api.spot_market import BinanceSpotMarketHttpAPI

# from nautilus_trader.adapters.binance.data import BinanceDataClient
# from nautilus_trader.adapters.binance.http.client import BinanceHttpClient
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import LiveLogger
from nautilus_trader.common.logging import Logger
from nautilus_trader.live.factories import LiveDataClientFactory
from nautilus_trader.live.factories import LiveExecutionClientFactory
from nautilus_trader.model.identifiers import AccountId
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.msgbus.bus import MessageBus

from nacre.adapters.binance.data import BinanceDataClient
from nacre.adapters.binance.data import BinanceFutureDataClient
from nacre.adapters.binance.data import BinanceSpotDataClient

# from nautilus_trader.adapters.binance.factories import get_cached_binance_http_client
# from nautilus_trader.adapters.binance.factories import get_cached_binance_instrument_provider
from nacre.adapters.binance.execution import BinanceExecutionClient
from nacre.adapters.binance.execution import BinanceFutureExecutionClient
from nacre.adapters.binance.execution import BinanceSpotExecutionClient
from nacre.adapters.binance.http.api.future_market import BinanceFutureMarketHttpAPI
from nacre.adapters.binance.http.patch import BinanceHttpClient
from nacre.adapters.binance.providers import BinanceInstrumentProvider


# from nautilus_trader.adapters.binance.common import BINANCE_VENUE
# from nautilus_trader.adapters.binance.execution import BinanceSpotExecutionClient


HTTP_CLIENTS: Dict[str, BinanceHttpClient] = {}


def get_cached_binance_http_client(
    loop: asyncio.AbstractEventLoop,
    clock: LiveClock,
    logger: Logger,
    key: Optional[str] = None,
    secret: Optional[str] = None,
    account_type: Optional[str] = None,
    proxy: Optional[str] = None,
    testnet: Optional[bool] = False,
) -> BinanceHttpClient:
    """
    Cache and return a Binance HTTP client with the given key and secret.

    If a cached client with matching key and secret already exists, then that
    cached client will be returned.

    Parameters
    ----------
    key : str, optional
        The API key for the client.
        If None then will source from the `BINANCE_API_KEY` env var.
    secret : str, optional
        The API secret for the client.
        If None then will source from the `BINANCE_API_SECRET` env var.
    account_type: str, optional
        spot future margin delivery
    loop : asyncio.AbstractEventLoop
        The event loop for the client.
    clock : LiveClock
        The clock for the client.
    logger : Logger
        The logger for the client.
    testnet: bool
        If client using testnet

    Returns
    -------
    BinanceHttpClient

    """
    global HTTP_CLIENTS
    key = key or os.environ.get("BINANCE_API_KEY", "")
    secret = secret or os.environ.get("BINANCE_API_SECRET", "")
    account_type = account_type or "spot"

    client_key: str = "|".join((key, secret, account_type, str(proxy or "")))
    if client_key not in HTTP_CLIENTS:
        base_url = None
        if account_type == "future":
            base_url = (
                "https://fapi.binance.com" if not testnet else "https://testnet.binancefuture.com"
            )
        elif account_type == "delivery":
            base_url = "https://dapi.binance.com"
        elif account_type == "spot":
            base_url = (
                "https://api.binance.com" if not testnet else "https://testnet.binance.vision"
            )

        client = BinanceHttpClient(
            loop=loop,
            clock=clock,
            logger=logger,
            key=key,
            secret=secret,
            base_url=base_url,
            proxy=proxy,
        )
        HTTP_CLIENTS[client_key] = client
    return HTTP_CLIENTS[client_key]


@lru_cache(1)
def get_cached_binance_instrument_provider(
    client: BinanceHttpClient,
    logger: Logger,
    venue: Venue,
    market_api: BinanceSpotMarketHttpAPI,
    account_type: str,
) -> BinanceInstrumentProvider:
    """
    Cache and return a BinanceInstrumentProvider.

    If a cached provider already exists, then that cached provider will be returned.

    Parameters
    ----------
    client : BinanceHttpClient
        The client for the instrument provider.
    logger : Logger
        The logger for the instrument provider.
    account_type: str
        spot, margin, future ...

    Returns
    -------
    BinanceInstrumentProvider

    """
    return BinanceInstrumentProvider(
        client=client,
        logger=logger,
        venue=venue,
        market_api=market_api,
        account_type=account_type,
    )


class BinanceLiveDataClientFactory(LiveDataClientFactory):
    """
    Provides a `Binance` live data client factory.
    """

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
    ) -> BinanceDataClient:
        """
        Create a new Binance data client.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The event loop for the client.
        name : str
            The client name.
        config : dict
            The configuration dictionary.
        msgbus : MessageBus
            The message bus for the client.
        cache : Cache
            The cache for the client.
        clock : LiveClock
            The clock for the client.
        logger : LiveLogger
            The logger for the client.
        client_cls : class, optional
            The class to call to return a new internal client.

        Returns
        -------
        BinanceDataClient

        """
        proxy = config.get("httpProxy", None)
        account_type_str = config.get("defaultType", "spot")
        testnet = config.get("testnet", False)
        client = get_cached_binance_http_client(
            account_type=account_type_str,
            loop=loop,
            clock=clock,
            logger=logger,
            proxy=proxy,
            testnet=testnet,
        )

        if account_type_str == "spot":
            venue = Venue("BINANCE_SPOT")
            market_api = BinanceSpotMarketHttpAPI(client=client)
        elif account_type_str == "future":
            venue = Venue("BINANCE_FUTURE")
            market_api = BinanceFutureMarketHttpAPI(client=client)
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")
        ins_client = get_cached_binance_http_client(
            account_type=account_type_str,
            loop=loop,
            clock=clock,
            logger=logger,
            testnet=testnet,
        )
        # Get instrument provider singleton
        provider = get_cached_binance_instrument_provider(
            client=ins_client,
            logger=logger,
            venue=venue,
            market_api=market_api,
            account_type=account_type_str,
        )

        # Create client
        if account_type_str == "spot":
            data_client = BinanceSpotDataClient(
                loop=loop,
                client=client,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                venue=venue,
                instrument_provider=provider,
                testnet=testnet,
            )
        elif account_type_str == "future":
            data_client = BinanceFutureDataClient(
                loop=loop,
                client=client,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                venue=venue,
                instrument_provider=provider,
                testnet=testnet,
            )
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")

        return data_client


class BinanceLiveExecutionClientFactory(LiveExecutionClientFactory):
    """
    Provides a `Binance` live execution client factory.
    """

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
    ) -> BinanceExecutionClient:
        """
        Create a new Binance execution client.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The event loop for the client.
        name : str
            The client name.
        config : dict[str, object]
            The configuration for the client.
        msgbus : MessageBus
            The message bus for the client.
        cache : Cache
            The cache for the client.
        clock : LiveClock
            The clock for the client.
        logger : LiveLogger
            The logger for the client.
        client_cls : class, optional
            The internal client constructor. This allows external library and
            testing dependency injection.

        Returns
        -------
        BinanceExecutionClient

        """
        proxy = config.get("httpProxy", None)
        account_type_str = config.get("defaultType", "spot")
        testnet = config.get("testnet", False)
        client = get_cached_binance_http_client(
            key=config.get("api_key"),
            secret=config.get("api_secret"),
            account_type=account_type_str,
            loop=loop,
            clock=clock,
            logger=logger,
            proxy=proxy,
            testnet=testnet,
        )

        if account_type_str == "spot":
            venue = Venue("BINANCE_SPOT")
            market_api = BinanceSpotMarketHttpAPI(client=client)
        elif account_type_str == "future":
            venue = Venue("BINANCE_FUTURE")
            market_api = BinanceFutureMarketHttpAPI(client=client)
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")

        ins_client = get_cached_binance_http_client(
            account_type=account_type_str,
            loop=loop,
            clock=clock,
            logger=logger,
            testnet=testnet,
        )

        # Get instrument provider singleton
        provider = get_cached_binance_instrument_provider(
            client=ins_client,
            logger=logger,
            venue=venue,
            market_api=market_api,
            account_type=account_type_str,
        )

        # Set account ID
        account_id = AccountId.from_str(name)

        # Create client
        if account_type_str == "spot":
            exec_client = BinanceSpotExecutionClient(
                loop=loop,
                client=client,
                name=name,
                account_id=account_id,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                instrument_provider=provider,
                testnet=testnet,
            )
        elif account_type_str == "future":
            exec_client = BinanceFutureExecutionClient(
                loop=loop,
                client=client,
                name=name,
                account_id=account_id,
                msgbus=msgbus,
                cache=cache,
                clock=clock,
                logger=logger,
                instrument_provider=provider,
                testnet=testnet,
            )
        else:
            raise ValueError(f"Account type not implemented: {account_type_str}")

        return exec_client
