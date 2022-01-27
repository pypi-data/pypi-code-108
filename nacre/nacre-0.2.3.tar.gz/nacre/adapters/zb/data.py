import asyncio
from typing import Any, Dict, List, Optional, Union

import orjson
import pandas as pd
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import Logger
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.core.uuid import UUID4
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.model.c_enums.bar_aggregation import BarAggregationParser
from nautilus_trader.model.data.bar import BarType
from nautilus_trader.model.data.base import DataType
from nautilus_trader.model.data.tick import QuoteTick
from nautilus_trader.model.data.tick import TradeTick
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import ClientId
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orderbook.data import OrderBookDeltas
from nautilus_trader.model.orderbook.data import OrderBookSnapshot
from nautilus_trader.msgbus.bus import MessageBus

from nacre.adapters.zb.data_types import ZbBar
from nacre.adapters.zb.data_types import ZbTicker
from nacre.adapters.zb.http.api.future_market import ZbFutureMarketHttpAPI
from nacre.adapters.zb.http.api.spot_market import ZbSpotMarketHttpAPI
from nacre.adapters.zb.http.client import ZbHttpClient
from nacre.adapters.zb.http.error import ZbError
from nacre.adapters.zb.http.spot import ZbSpotHttpClient
from nacre.adapters.zb.parsing import parse_bar
from nacre.adapters.zb.parsing import parse_bar_ws
from nacre.adapters.zb.parsing import parse_book_snapshot_ws
from nacre.adapters.zb.parsing import parse_diff_depth_stream_ws
from nacre.adapters.zb.parsing import parse_mark_price
from nacre.adapters.zb.parsing import parse_spot_bar
from nacre.adapters.zb.parsing import parse_spot_book_snapshot_ws
from nacre.adapters.zb.parsing import parse_spot_ticker_ws
from nacre.adapters.zb.parsing import parse_spot_trade_tick_ws
from nacre.adapters.zb.parsing import parse_ticker_ws
from nacre.adapters.zb.parsing import parse_trade_tick
from nacre.adapters.zb.parsing import parse_trade_tick_ws
from nacre.adapters.zb.providers import ZbInstrumentProvider

# from nacre.adapters.zb.websocket.client import ZbWebSocketClient
from nacre.adapters.zb.websocket.future import ZbFuturesWebSocket
from nacre.adapters.zb.websocket.spot import ZbSpotWebSocket
from nacre.model.data.tick import MarkTick


# from nautilus_trader.adapters.binance.common import BINANCE_VENUE


class ZbDataClient(LiveMarketDataClient):
    def connect(self):
        """
        Connect the client to Zb.
        """
        self._log.info("Connecting...")
        self._loop.create_task(self._connect())

    def disconnect(self):
        """
        Disconnect the client from Zb.
        """
        self._log.info("Disconnecting...")
        self._loop.create_task(self._disconnect())

    async def _connect(self):
        # Connect HTTP client
        if not self._client.connected:
            await self._client.connect()
        try:
            await self._instrument_provider.load_all_or_wait_async()
        except ZbError as ex:
            self._log.exception(ex)
            return

        self._send_all_instruments_to_data_engine()
        self._update_instruments_task = self._loop.create_task(self._update_instruments())

        # Connect WebSocket clients
        self._loop.create_task(self._connect_websockets())

        self._set_connected(True)
        self._log.info("Connected.")

    async def _connect_websockets(self):
        self._log.info("Awaiting subscriptions...")
        await self._ws_api.connect()

    async def _update_instruments(self):
        while True:
            self._log.debug(
                f"Scheduled `update_instruments` to run in "
                f"{self._update_instruments_interval}s."
            )
            await asyncio.sleep(self._update_instruments_interval)
            await self._instrument_provider.load_all_async()
            self._send_all_instruments_to_data_engine()

    async def _disconnect(self):
        # Cancel tasks
        if self._update_instruments_task:
            self._log.debug("Canceling `update_instruments` task...")
            self._update_instruments_task.cancel()

        # Disconnect WebSocket clients
        if self._ws_api.is_connected:
            await self._ws_api.disconnect()

        # Disconnect HTTP client
        if self._client.connected:
            await self._client.disconnect()

        self._set_connected(False)
        self._log.info("Disconnected.")

    # -- SUBSCRIPTIONS -----------------------------------------------------------------------------

    def subscribe_instruments(self):
        """
        Subscribe to instrument data for the venue.

        """
        for instrument_id in list(self._instrument_provider.get_all().keys()):
            self._add_subscription_instrument(instrument_id)

    def subscribe_instrument(self, instrument_id: InstrumentId):
        """
        Subscribe to instrument data for the given instrument ID.

        Parameters
        ----------
        instrument_id : InstrumentId
            The instrument ID to subscribe to.

        """
        self._add_subscription_instrument(instrument_id)

    def subscribe_ticker(self, instrument_id: InstrumentId):
        self._loop.create_task(self._ws_api.subscribe_ticker(instrument_id.symbol.value))
        self._add_subscription_ticker(instrument_id)

    def subscribe_trade_ticks(self, instrument_id: InstrumentId):
        self._loop.create_task(self._ws_api.subscribe_trades(instrument_id.symbol.value))
        self._add_subscription_trade_ticks(instrument_id)

    def subscribe_instrument_status_updates(self, instrument_id: InstrumentId):
        self._log.warning(
            "Cannot subscribe to instrument status updates: "
            "Not currently supported for the Zb integration.",
        )

    def subscribe_instrument_close_prices(self, instrument_id: InstrumentId):
        self._log.warning(
            "Cannot subscribe to instrument status updates: "
            "Not currently supported for the Zb integration.",
        )

    def unsubscribe_instruments(self):
        """
        Unsubscribe from instrument data for the venue.

        """
        for instrument_id in list(self._instrument_provider.get_all().keys()):
            self._remove_subscription_instrument(instrument_id)

    def unsubscribe_instrument(self, instrument_id: InstrumentId):
        """
        Unsubscribe from instrument data for the given instrument ID.

        Parameters
        ----------
        instrument_id : InstrumentId
            The instrument ID to unsubscribe from.

        """
        self._remove_subscription_instrument(instrument_id)

    def unsubscribe_order_book_deltas(self, instrument_id: InstrumentId):
        self._remove_subscription_order_book_deltas(instrument_id)

    def unsubscribe_order_book_snapshots(self, instrument_id: InstrumentId):
        self._remove_subscription_order_book_snapshots(instrument_id)

    def unsubscribe_ticker(self, instrument_id: InstrumentId):
        self._remove_subscription_ticker(instrument_id)

    def unsubscribe_quote_ticks(self, instrument_id: InstrumentId):
        self._remove_subscription_quote_ticks(instrument_id)

    def unsubscribe_trade_ticks(self, instrument_id: InstrumentId):
        self._remove_subscription_trade_ticks(instrument_id)

    def unsubscribe_bars(self, bar_type: BarType):
        self._remove_subscription_bars(bar_type)

    def unsubscribe_instrument_status_updates(self, instrument_id: InstrumentId):
        self._remove_subscription_instrument_status_updates(instrument_id)

    def unsubscribe_instrument_close_prices(self, instrument_id: InstrumentId):
        self._remove_subscription_instrument_close_prices(instrument_id)

    # -- REQUESTS ----------------------------------------------------------------------------------

    def request_quote_ticks(
        self,
        instrument_id: InstrumentId,
        from_datetime: pd.Timestamp,
        to_datetime: pd.Timestamp,
        limit: int,
        correlation_id: UUID4,
    ):
        self._log.error(
            "Cannot request historical quote ticks: not published by Zb.",
        )

    def request_bars(
        self,
        bar_type: BarType,
        from_datetime: pd.Timestamp,
        to_datetime: pd.Timestamp,
        limit: int,
        correlation_id: UUID4,
    ):
        if bar_type.is_internally_aggregated():
            self._log.error(
                f"Cannot request {bar_type}: "
                f"only historical bars with EXTERNAL aggregation available from Zb.",
            )
            return

        if not bar_type.spec.is_time_aggregated():
            self._log.error(
                f"Cannot request {bar_type}: only time bars are aggregated by Zb.",
            )
            return

        if bar_type.spec.aggregation == BarAggregation.SECOND:
            self._log.error(
                f"Cannot request {bar_type}: second bars are not aggregated by Zb.",
            )
            return

        if bar_type.spec.price_type != PriceType.LAST:
            self._log.error(
                f"Cannot request {bar_type}: "
                f"only historical bars for LAST price type available from Zb.",
            )
            return

        self._loop.create_task(
            self._request_bars(
                bar_type=bar_type,
                from_datetime=from_datetime,
                to_datetime=to_datetime,
                limit=limit,
                correlation_id=correlation_id,
            )
        )

    def _send_all_instruments_to_data_engine(self):
        for instrument in self._instrument_provider.get_all().values():
            self._handle_data(instrument)

        for currency in self._instrument_provider.currencies().values():
            self._cache.add_currency(currency)

    def _handle_pong(self):
        # reset ping timer
        pass


class ZbSpotDataClient(ZbDataClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: ZbSpotHttpClient,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        venue: Venue,
        instrument_provider: ZbInstrumentProvider,
    ):
        # HTTP API
        self._market_api = ZbSpotMarketHttpAPI(client=client)
        # websocket api
        self._ws_api = ZbSpotWebSocket(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=self._handle_ws_message,
        )
        super(ZbDataClient, self).__init__(
            loop=loop,
            client_id=ClientId(venue.value),
            instrument_provider=instrument_provider,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            logger=logger,
            config={"name": f"ZbDataClient-{venue.value}"},
        )

        self._client = client

        self._update_instrument_interval: int = 60 * 60  # Once per hour (hardcode)
        self._update_instruments_task: Optional[asyncio.Task] = None

    def subscribe_order_book_deltas(
        self,
        instrument_id: InstrumentId,
        book_type: BookType,
        depth: Optional[int] = None,
        kwargs: dict = None,
    ):
        self._loop.create_task(
            self._subscribe_order_book_snapshot(
                instrument_id=instrument_id,
                book_type=book_type,
                depth=depth,
            )
        )

        self._add_subscription_order_book_deltas(instrument_id)

    def subscribe_order_book_snapshots(
        self,
        instrument_id: InstrumentId,
        book_type: BookType,
        depth: Optional[int] = None,
        kwargs: dict = None,
    ):
        self._loop.create_task(
            self._subscribe_order_book_snapshot(
                instrument_id=instrument_id,
                book_type=book_type,
                depth=depth,
            )
        )

        self._add_subscription_order_book_snapshots(instrument_id)

    async def _subscribe_order_book_snapshot(
        self,
        instrument_id: InstrumentId,
        book_type: BookType,
        depth: Optional[int] = None,
    ):
        if book_type == BookType.L3_MBO:
            self._log.error(
                "Cannot subscribe to order book deltas: "
                "L3_MBO data is not published by Zb. "
                "Valid book types are L1_TBBO, L2_MBP.",
            )
            return

        if depth is not None and depth != 0:
            self._log.warning(
                "Cannot subscribe to depth order book snapshots: "
                f"invalid depth, was {depth}. "
                "Zb does not support custom depth.",
            )

        await self._ws_api.subscribe_depth(
            symbol=instrument_id.symbol.value,
        )

    def subscribe_quote_ticks(self, instrument_id: InstrumentId):
        self._log.warning(
            "Cannot subscribe to quote tick updates: "
            "Not currently supported for the Zb spot integration.",
        )

    def request_trade_ticks(
        self,
        instrument_id: InstrumentId,
        from_datetime: pd.Timestamp,
        to_datetime: pd.Timestamp,
        limit: int,
        correlation_id: UUID4,
    ):
        if limit == 0 or limit > 50:
            limit = 50

        if from_datetime is not None or to_datetime is not None:
            self._log.warning(
                "Trade ticks have been requested with a from/to time range, "
                f"however the request will be for the most recent {limit}."
            )

        self._loop.create_task(self._request_trade_ticks(instrument_id, limit, correlation_id))

    async def _request_trade_ticks(
        self,
        instrument_id: InstrumentId,
        limit: int,
        correlation_id: UUID4,
    ):
        response: Dict[str, Any] = await self._market_api.trades(instrument_id.symbol.value, limit)

        ticks: List[TradeTick] = [
            parse_trade_tick(
                msg=t,
                instrument_id=instrument_id,
                ts_init=self._clock.timestamp_ns(),
            )
            for t in response["data"]
        ]

        self._handle_trade_ticks(instrument_id, ticks, correlation_id)

    async def _request_bars(
        self,
        bar_type: BarType,
        from_datetime: pd.Timestamp,
        to_datetime: pd.Timestamp,
        limit: int,
        correlation_id: UUID4,
    ):
        if limit == 0 or limit > 1000:
            limit = 1000

        if bar_type.spec.aggregation == BarAggregation.MINUTE:
            resolution = "min"
        elif bar_type.spec.aggregation == BarAggregation.HOUR:
            resolution = "hour"
        elif bar_type.spec.aggregation == BarAggregation.DAY:
            resolution = "day"
        else:  # pragma: no cover (design-time error)
            raise RuntimeError(
                f"invalid aggregation period, "
                f"was {BarAggregationParser.from_str(bar_type.spec.aggregation)}",
            )

        if to_datetime is not None:
            self._log.warning(
                "Trade ticks have been requested with to_datetime option, "
                f"however the request will be for the most recent {limit} or after from_datetime."
            )

        start_time_ms = from_datetime.to_datetime64() * 1000 if from_datetime is not None else None

        data: Dict[str, Any] = await self._market_api.kline(
            market=bar_type.instrument_id.symbol.value,
            type=f"{bar_type.spec.step}{resolution}",
            since=start_time_ms,
            size=limit,
        )

        bars: List[ZbBar] = [
            parse_spot_bar(bar_type, values=b, ts_init=self._clock.timestamp_ns())
            for b in data["data"]
        ]
        partial: ZbBar = bars.pop()

        self._handle_bars(bar_type, bars, partial, correlation_id)

    def _handle_ws_message(self, raw: bytes):
        try:
            msg: Dict[str, Any] = orjson.loads(raw)
        except orjson.JSONDecodeError as ex:
            if raw.decode() == "pong":
                self._handle_pong()
                return
            else:
                raise ex

        # data = msg.get("data")
        chan: Optional[str] = msg.get("channel")

        if not chan:
            self._log.error(f"Unknown response: {msg}")
            return

        symbol, _, chan_type = chan.partition("_")

        if chan_type == "ticker":
            self._handle_24hr_ticker(msg["ticker"], symbol)
        elif chan_type == "trades":
            self._handle_trade(msg["data"], symbol)
        elif chan_type == "depth":
            self._handle_book_snapshot(msg, symbol)
        else:
            self._log.error(f"Unrecognized websocket message type, was {chan}")
            return

    def _handle_24hr_ticker(self, data: Dict[str, str], symbol: str):
        instrument_id = self._instrument_provider.find_instrument_id_by_local_market_id(symbol)
        ticker: ZbTicker = parse_spot_ticker_ws(
            instrument_id=instrument_id,
            msg=data,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(ticker)

    def _handle_trade(self, data: List[Dict[str, str]], symbol: str):
        instrument_id = self._instrument_provider.find_instrument_id_by_local_market_id(symbol)
        for d in data:
            trade_tick: TradeTick = parse_spot_trade_tick_ws(
                instrument_id=instrument_id,
                msg=d,
                ts_init=self._clock.timestamp_ns(),
            )
            self._handle_data(trade_tick)

    def _handle_book_snapshot(
        self,
        data: Dict,
        symbol: str,
    ):
        instrument_id = self._instrument_provider.find_instrument_id_by_local_market_id(symbol)
        book_snapshot: OrderBookSnapshot = parse_spot_book_snapshot_ws(
            instrument_id=instrument_id,
            msg=data,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(book_snapshot)


class ZbFutureDataClient(ZbDataClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: ZbHttpClient,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        venue: Venue,
        instrument_provider: ZbInstrumentProvider,
    ):
        # HTTP API
        self._market_api = ZbFutureMarketHttpAPI(client=client)
        # websocket api
        self._ws_api = ZbFuturesWebSocket(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=self._handle_ws_message,
        )

        super(ZbDataClient, self).__init__(
            loop=loop,
            client_id=ClientId(venue.value),
            instrument_provider=instrument_provider,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            logger=logger,
            config={"name": f"ZbDataClient-{venue.value}"},
        )

        self._client = client

        self._update_instrument_interval: int = 60 * 60  # Once per hour (hardcode)
        self._update_instruments_task: Optional[asyncio.Task] = None

        self._kline_buffer: Dict[InstrumentId, List[Any]] = {}
        self._quote_tick_subscribed = False
        self._last_quote_tick: Dict[InstrumentId, QuoteTick] = {}

    def subscribe(self, data_type: DataType) -> None:
        if data_type.type == MarkTick:
            instrument_id = data_type.metadata.get("instrument_id")
            if instrument_id:
                self._loop.create_task(self._subscribe_mark_price())
                self._add_subscription(
                    DataType(MarkTick, metadata={"instrument_id": instrument_id})
                )
            else:
                self._loop.create_task(self._subscribe_mark_price(instrument_id))
                self._add_subscription(DataType(MarkTick))

    async def _subscribe_mark_price(self, instrument_id: Optional[InstrumentId] = None):
        if instrument_id:
            await self._ws_api.subscribe_mark_price(symbol=instrument_id.symbol.value)
        else:
            await self._ws_api.subscribe_mark_price()

    def subscribe_quote_ticks(self, instrument_id: InstrumentId):
        self._loop.create_task(
            self._ws_api.subscribe_book_deltas(
                symbol=instrument_id.symbol.value,
                depth=1,
            )
        )
        self._quote_tick_subscribed = True
        self._add_subscription_quote_ticks(instrument_id)

    def subscribe_bars(self, bar_type: BarType):
        PyCondition.true(bar_type.is_externally_aggregated(), "aggregation_source is not EXTERNAL")

        if not bar_type.spec.is_time_aggregated():
            self._log.error(
                f"Cannot subscribe to {bar_type}: only time bars are aggregated by Zb.",
            )
            return

        if bar_type.spec.aggregation == BarAggregation.SECOND:
            self._log.error(
                f"Cannot subscribe to {bar_type}: second bars are not aggregated by Zb.",
            )
            return

        if bar_type.spec.aggregation == BarAggregation.MINUTE:
            resolution = "M"
        elif bar_type.spec.aggregation == BarAggregation.HOUR:
            resolution = "H"
        elif bar_type.spec.aggregation == BarAggregation.DAY:
            resolution = "D"
        else:  # pragma: no cover (design-time error)
            raise RuntimeError(
                f"invalid aggregation period, "
                f"was {BarAggregationParser.from_str(bar_type.spec.aggregation)}",
            )

        if bar_type.instrument_id not in self._kline_buffer:
            self._kline_buffer[bar_type.instrument_id] = []

        self._loop.create_task(
            self._ws_api.subscribe_bars(
                symbol=bar_type.instrument_id.symbol.value,
                interval=f"{bar_type.spec.step}{resolution}",
            )
        )
        self._add_subscription_bars(bar_type)

    def subscribe_order_book_deltas(
        self,
        instrument_id: InstrumentId,
        book_type: BookType,
        depth: Optional[int] = None,
        kwargs: dict = None,
    ):
        self._loop.create_task(
            self._subscribe_order_book_deltas(
                instrument_id=instrument_id,
                book_type=book_type,
                depth=depth,
            )
        )

        self._add_subscription_order_book_deltas(instrument_id)

    def subscribe_order_book_snapshots(
        self,
        instrument_id: InstrumentId,
        book_type: BookType,
        depth: Optional[int] = None,
        kwargs: dict = None,
    ):
        self._loop.create_task(
            self._subscribe_order_book_snapshot(
                instrument_id=instrument_id,
                book_type=book_type,
                depth=depth,
            )
        )

        self._add_subscription_order_book_snapshots(instrument_id)

    async def _subscribe_order_book_snapshot(
        self,
        instrument_id: InstrumentId,
        book_type: BookType,
        depth: Optional[int] = None,
    ):
        if book_type == BookType.L3_MBO:
            self._log.error(
                "Cannot subscribe to order book deltas: "
                "L3_MBO data is not published by Zb. "
                "Valid book types are L1_TBBO, L2_MBP.",
            )
            return

        if depth is None or depth == 0:
            depth = 5

        if depth > 10:
            self._log.error(
                "Cannot subscribe to order book snapshots: "
                f"invalid depth, was {depth}. "
                "Valid depths are 1 to 10.",
            )
            return

        await self._ws_api.subscribe_book_snapshot(
            symbol=instrument_id.symbol.value,
            depth=depth,
        )

    async def _subscribe_order_book_deltas(
        self,
        instrument_id: InstrumentId,
        book_type: BookType,
        depth: Optional[int] = None,
    ):
        if book_type == BookType.L3_MBO:
            self._log.error(
                "Cannot subscribe to order book deltas: "
                "L3_MBO data is not published by Zb. "
                "Valid book types are L1_TBBO, L2_MBP.",
            )
            return

        if depth is None or depth == 0:
            depth = 50

        if depth >= 1000:
            self._log.error(
                "Cannot subscribe to order book deltas: "
                f"invalid depth, was {depth}. "
                "Valid depths are 1 to 1000.",
            )
            return

        await self._ws_api.subscribe_book_deltas(
            symbol=instrument_id.symbol.value,
            depth=depth,
        )

    def request_trade_ticks(
        self,
        instrument_id: InstrumentId,
        from_datetime: pd.Timestamp,
        to_datetime: pd.Timestamp,
        limit: int,
        correlation_id: UUID4,
    ):
        if limit == 0 or limit > 1000:
            limit = 1000

        if from_datetime is not None or to_datetime is not None:
            self._log.warning(
                "Trade ticks have been requested with a from/to time range, "
                f"however the request will be for the most recent {limit}."
            )

        self._loop.create_task(self._request_trade_ticks(instrument_id, limit, correlation_id))

    async def _request_trade_ticks(
        self,
        instrument_id: InstrumentId,
        limit: int,
        correlation_id: UUID4,
    ):
        response: Dict[str, Any] = await self._market_api.trades(instrument_id.symbol.value, limit)

        ticks: List[TradeTick] = [
            parse_trade_tick(
                msg=t,
                instrument_id=instrument_id,
                ts_init=self._clock.timestamp_ns(),
            )
            for t in response["data"]
        ]

        self._handle_trade_ticks(instrument_id, ticks, correlation_id)

    async def _request_bars(
        self,
        bar_type: BarType,
        from_datetime: pd.Timestamp,
        to_datetime: pd.Timestamp,
        limit: int,
        correlation_id: UUID4,
    ):
        if limit == 0 or limit > 1440:
            limit = 1440

        if bar_type.spec.aggregation == BarAggregation.MINUTE:
            resolution = "M"
        elif bar_type.spec.aggregation == BarAggregation.HOUR:
            resolution = "H"
        elif bar_type.spec.aggregation == BarAggregation.DAY:
            resolution = "D"
        else:  # pragma: no cover (design-time error)
            raise RuntimeError(
                f"invalid aggregation period, "
                f"was {BarAggregationParser.from_str(bar_type.spec.aggregation)}",
            )

        if from_datetime is not None or to_datetime is not None:
            self._log.warning(
                "Trade ticks have been requested with a from/to time range, "
                f"however the request will be for the most recent {limit}."
            )

        data: Dict[str, Any] = await self._market_api.klines(
            symbol=bar_type.instrument_id.symbol.value,
            period=f"{bar_type.spec.step}{resolution}",
            size=limit,
        )

        bars: List[ZbBar] = [
            parse_bar(bar_type, values=b, ts_init=self._clock.timestamp_ns()) for b in data["data"]
        ]
        partial: ZbBar = bars.pop()

        self._handle_bars(bar_type, bars, partial, correlation_id)

    def _handle_ws_message(self, raw: bytes):  # noqa: C901
        msg: Dict[str, Any] = orjson.loads(raw)
        data = msg.get("data")
        chan: Optional[str] = msg.get("channel")
        err: Optional[str] = msg.get("errorCode")

        if err:
            self._log.error(f"Subscribe failed for channel: {chan}, error: {err}")
            return

        if not chan:
            if msg.get("action", "") == "pong":
                self._handle_pong()
            else:
                self._log.error(f"Unknown response: {msg}")
            return

        msg_type: Optional[str] = msg.get("type")

        symbol, _, chan_type = chan.partition(".")

        if chan_type.startswith("DepthWhole"):
            self._handle_book_snapshot(data, symbol)
        elif chan_type.startswith("Depth"):
            if msg_type == "Whole":
                self._handle_book_snapshot(data, symbol)
            else:
                self._handle_depth_update(data, symbol)
        elif chan_type.startswith("KLine"):
            self._handle_kline(data, symbol, chan_type, msg_type)
        elif chan_type == "Trade":
            self._handle_trade(data, symbol, msg_type)
        elif chan_type == "Ticker":
            self._handle_24hr_ticker(data, symbol)
        elif chan_type == "mark":
            self._handle_mark_price(data, symbol)
        elif chan_type == "index":
            self._handle_index_price(data, symbol)
        elif chan_type == "FundingRate":
            self._handle_funding_rate(data, symbol)
        elif chan_type.startswith("mark_"):
            self._handle_mark_kline(data, symbol, chan_type, msg_type)
        elif chan_type.startswith("index_"):
            self._handle_index_kline(data, symbol, chan_type, msg_type)
        else:
            self._log.error(f"Unrecognized websocket message type, was {chan}")
            return

    def _handle_book_snapshot(
        self,
        data: Dict[str, Any],
        symbol: str,
    ):
        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)
        book_snapshot: OrderBookSnapshot = parse_book_snapshot_ws(
            instrument_id=instrument_id,
            msg=data,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(book_snapshot)

        if self._quote_tick_subscribed:
            self._handle_quote_tick_from_snapshot(data, instrument_id)

    def _handle_quote_tick_from_snapshot(self, data: Dict[str, Any], instrument_id: InstrumentId):
        bid = data["bids"][0]
        ask = data["asks"][0]
        quote_tick = QuoteTick(
            instrument_id=instrument_id,
            bid=Price.from_str(str(bid[0])),
            ask=Price.from_str(str(ask[0])),
            bid_size=Quantity.from_str(str(bid[1])),
            ask_size=Quantity.from_str(str(ask[1])),
            ts_event=self._clock.timestamp_ns(),
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(quote_tick)
        self._last_quote_tick[instrument_id] = quote_tick

    def _handle_depth_update(
        self,
        data: Dict[str, Any],
        symbol: str,
    ):
        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)
        book_deltas: OrderBookDeltas = parse_diff_depth_stream_ws(
            instrument_id=instrument_id,
            msg=data,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(book_deltas)
        if self._quote_tick_subscribed:
            self._handle_quote_tick_from_deltas(data, instrument_id)

    def _handle_quote_tick_from_deltas(self, data: Dict[str, Any], instrument_id: InstrumentId):
        bid, bid_size = next((x for x in data.get("bids", []) if float(x[1]) != 0), [0, 0])
        ask, ask_size = next((x for x in data.get("asks", []) if float(x[1]) != 0), [0, 0])

        bid = self._last_quote_tick[instrument_id].bid if bid == 0 else Price.from_str(str(bid))
        bid_size = (
            self._last_quote_tick[instrument_id].bid_size
            if bid_size == 0
            else Quantity.from_str(str(bid_size))
        )
        ask = self._last_quote_tick[instrument_id].ask if ask == 0 else Price.from_str(str(ask))
        ask_size = (
            self._last_quote_tick[instrument_id].ask_size
            if ask_size == 0
            else Quantity.from_str(str(ask_size))
        )

        quote_tick = QuoteTick(
            instrument_id=instrument_id,
            bid=bid,
            ask=ask,
            bid_size=bid_size,
            ask_size=ask_size,
            ts_event=self._clock.timestamp_ns(),
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(quote_tick)
        self._last_quote_tick[instrument_id] = quote_tick

    def _handle_24hr_ticker(self, data: List[Any], symbol: str):
        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)
        ticker: ZbTicker = parse_ticker_ws(
            instrument_id=instrument_id,
            msg=data,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(ticker)

    def _handle_trade(self, data: List[List[Any]], symbol: str, msg_type: Optional[str] = None):
        if msg_type and msg_type == "Whole":
            return

        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)
        for d in data:
            trade_tick: TradeTick = parse_trade_tick_ws(
                instrument_id=instrument_id,
                msg=d,
                ts_init=self._clock.timestamp_ns(),
            )
            self._handle_data(trade_tick)

    def _handle_kline(
        self,
        data: List[List[Any]],
        symbol: str,
        chan_type: str,
        msg_type: Optional[str] = None,
    ):
        if msg_type and msg_type == "Whole":
            return

        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)
        for d in data:
            last_kline = self._kline_buffer[instrument_id]
            self._kline_buffer[instrument_id] = d
            if not last_kline:
                continue
            elif last_kline[5] != d[5]:
                bar: ZbBar = parse_bar_ws(
                    instrument_id=instrument_id,
                    chan_type=chan_type,
                    kline=last_kline,
                    ts_init=self._clock.timestamp_ns(),
                )
                self._handle_data(bar)

    def _handle_mark_price(self, data: Union[Dict, str], symbol: str):
        if isinstance(data, dict):
            for sym, price in data.items():
                self._handle_single_mark_price(price, sym)
        else:
            self._handle_single_mark_price(data, symbol)

    def _handle_single_mark_price(self, price: str, symbol: str):
        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)
        mark_price = parse_mark_price(
            instrument_id=instrument_id,
            price=price,
            ts_init=self._clock.timestamp_ns(),
        )
        self._handle_data(mark_price)

    def _handle_index_price(self, data: str, symbol: str):
        pass

    def _handle_funding_rate(self, data: Dict[str, Any], symbol: str):
        pass

    def _handle_mark_kline(
        self,
        data: List[List[Any]],
        symbol: str,
        chan_type: str,
        msg_type: Optional[str] = None,
    ):
        pass

    def _handle_index_kline(
        self,
        data: List[List[Any]],
        symbol: str,
        chan_type: str,
        msg_type: Optional[str] = None,
    ):
        pass
