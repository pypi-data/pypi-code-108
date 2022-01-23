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
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import orjson
from nautilus_trader.adapters.binance.http.api.spot_account import BinanceSpotAccountHttpAPI
from nautilus_trader.adapters.binance.http.api.spot_market import BinanceSpotMarketHttpAPI
from nautilus_trader.adapters.binance.http.client import BinanceHttpClient
from nautilus_trader.adapters.binance.http.error import BinanceError
from nautilus_trader.adapters.binance.parsing import binance_order_type
from nautilus_trader.adapters.binance.parsing import parse_order_type
from nautilus_trader.adapters.binance.providers import BinanceInstrumentProvider
from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import LogColor
from nautilus_trader.common.logging import Logger
from nautilus_trader.common.timer import TimeEvent
from nautilus_trader.core.datetime import millis_to_nanos
from nautilus_trader.execution.messages import ExecutionReport
from nautilus_trader.execution.messages import OrderStatusReport
from nautilus_trader.model.commands.trading import CancelAllOrders
from nautilus_trader.model.commands.trading import CancelOrder
from nautilus_trader.model.commands.trading import ModifyOrder
from nautilus_trader.model.commands.trading import SubmitOrder
from nautilus_trader.model.commands.trading import SubmitOrderList
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import LiquiditySide
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import OrderSideParser
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.enums import PositionSide
from nautilus_trader.model.enums import PositionSideParser
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TimeInForceParser
from nautilus_trader.model.enums import VenueType
from nautilus_trader.model.events.account import AccountState
from nautilus_trader.model.identifiers import AccountId
from nautilus_trader.model.identifiers import ClientId
from nautilus_trader.model.identifiers import ClientOrderId
from nautilus_trader.model.identifiers import ExecutionId
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import StrategyId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import VenueOrderId
from nautilus_trader.model.instruments.base import Instrument
from nautilus_trader.model.objects import AccountBalance
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orders.base import Order
from nautilus_trader.model.orders.limit import LimitOrder
from nautilus_trader.model.orders.market import MarketOrder
from nautilus_trader.model.orders.stop_limit import StopLimitOrder
from nautilus_trader.model.orders.stop_market import StopMarketOrder
from nautilus_trader.model.position import Position
from nautilus_trader.msgbus.bus import MessageBus

from nacre.adapters.binance.http.api.future_account import BinanceFutureAccountHttpAPI
from nacre.adapters.binance.http.api.future_market import BinanceFutureMarketHttpAPI
from nacre.adapters.binance.http.api.user import BinanceFutureUserDataHttpAPI
from nacre.adapters.binance.http.api.user import BinanceSpotUserDataHttpAPI
from nacre.adapters.binance.http.api.user import BinanceUserDataHttpAPI
from nacre.adapters.binance.parsing import binance_future_order_type
from nacre.adapters.binance.parsing import parse_balances
from nacre.adapters.binance.parsing import parse_future_order_type
from nacre.adapters.binance.parsing import parse_positions
from nacre.adapters.binance.parsing import parse_reported_position
from nacre.adapters.binance.parsing import parse_reported_positions_ws
from nacre.adapters.binance.parsing import parse_reported_wallet_balance
from nacre.adapters.binance.parsing import parse_reported_wallet_balance_ws
from nacre.adapters.binance.websocket.user import BinanceFutureUserDataWebSocket
from nacre.adapters.binance.websocket.user import BinanceSpotUserDataWebSocket
from nacre.adapters.binance.websocket.user import BinanceUserDataWebSocket
from nacre.live.execution_client import LiveExecutionClient
from nacre.model.report_position import ReportedPosition
from nacre.model.report_position import SideWithMode


# import json


VALID_TIF = (TimeInForce.GTC, TimeInForce.FOK, TimeInForce.IOC)


class BinanceExecutionClient(LiveExecutionClient):
    """
    Provides an execution client for Binance SPOT markets.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: BinanceHttpClient,
        account_type: AccountType,
        name: str,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        instrument_provider: BinanceInstrumentProvider,
        account_api: BinanceSpotAccountHttpAPI,
        market_api: BinanceSpotMarketHttpAPI,
        user_api: BinanceUserDataHttpAPI,
        ws_user_api: BinanceUserDataWebSocket,
    ):
        """
        Initialize a new instance of the ``BinanceExecutionClient`` class.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            The event loop for the client.
        client : BinanceHttpClient
            The binance HTTP client.
        account_type : AccountType
            The account type.
        account_id : AccountId
            The account ID for the client.
        msgbus : MessageBus
            The message bus for the client.
        cache : Cache
            The cache for the client.
        clock : LiveClock
            The clock for the client.
        logger : Logger
            The logger for the client.
        instrument_provider : BinanceInstrumentProvider
            The instrument provider.

        """
        super().__init__(
            loop=loop,
            client_id=ClientId(name),
            instrument_provider=instrument_provider,
            venue_type=VenueType.EXCHANGE,
            account_id=account_id,
            account_type=account_type,
            base_currency=None,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            logger=logger,
            config={"name": f"BinanceExecClient-{name}"},
        )

        self._client = client

        # Hot caches
        self._instrument_ids: Dict[str, InstrumentId] = {}

        # HTTP API
        self._account_api = account_api
        self._market_api = market_api
        self._user_api = user_api

        # Listen keys
        self._ping_listen_keys_interval: int = 60 * 5  # Once every 5 mins (hardcode)
        self._ping_listen_keys_task: Optional[asyncio.Task] = None
        self._listen_key: Optional[str] = None

        # WebSocket API
        self._ws_user_api = ws_user_api

        # if take account_snapshot
        self._snapshot_enabled = os.environ.get("SNAPSHOT_ENABLED", False)

    def connect(self) -> None:
        """
        Connect the client to Binance.
        """
        self._log.info("Connecting...")
        self._loop.create_task(self._connect())

    def disconnect(self) -> None:
        """
        Disconnect the client from Binance.
        """
        self._log.info("Disconnecting...")
        self._loop.create_task(self._disconnect())

    async def _connect(self) -> None:
        # Connect HTTP client
        if not self._client.connected:
            await self._client.connect()
        try:
            await self._instrument_provider.load_all_or_wait_async()
        except BinanceError as ex:
            self._log.exception(ex)
            return

        # Authenticate API key and update account(s)
        response: Dict[str, Any] = await self._account_api.account(recv_window=5000)

        self._authenticate_api_key(response=response)
        self._update_account_state(response=response)

        await self._get_account_setting()

        # Get listen keys
        response = await self._user_api.create_listen_key()
        self._listen_key = response["listenKey"]
        self._ping_listen_keys_task = self._loop.create_task(self._ping_listen_keys())

        # Connect WebSocket clients
        self._ws_user_api.subscribe(key=self._listen_key)
        await self._ws_user_api.connect()
        self._ws_user_api.add_after_connect_callback(self._sync_account_state)

        self._set_connected(True)
        self._log.info("Connected.")

        if self._snapshot_enabled:
            self._clock.set_timer(
                name=self.account_id.value,
                interval=timedelta(minutes=1),
                start_time=None,
                stop_time=None,
                callback=self._on_snapshot_inteval,
            )

    async def _get_account_setting(self):
        pass

    async def _sync_account_state(self):
        try:
            response: Dict[str, Any] = await self._account_api.account(recv_window=5000)
        except BinanceError as ex:
            self._log.error(ex.message)
            return

        self._update_account_state(response=response)

    def _authenticate_api_key(self, response: Dict[str, Any]) -> None:
        if response["canTrade"]:
            self._log.info("Binance API key authenticated.", LogColor.GREEN)
            self._log.info(f"API key {self._client.api_key} has trading permissions.")
        else:
            self._log.error("Binance API key does not have trading permissions.")

    async def _ping_listen_keys(self):
        while True:
            self._log.debug(
                f"Scheduled `ping_listen_keys` to run in " f"{self._ping_listen_keys_interval}s."
            )
            await asyncio.sleep(self._ping_listen_keys_interval)
            if self._listen_key:
                self._log.debug(f"Pinging WebSocket listen key {self._listen_key}...")
                await self._user_api.ping_listen_key(self._listen_key)

    async def _disconnect(self) -> None:
        # Cancel tasks
        if self._ping_listen_keys_task:
            self._log.debug("Canceling `ping_listen_keys` task...")
            self._ping_listen_keys_task.cancel()

        # Disconnect WebSocket clients
        if self._ws_user_api.is_connected:
            await self._ws_user_api.disconnect()

        # Disconnect HTTP client
        if self._client.connected:
            await self._client.disconnect()

        self._set_connected(False)
        self._log.info("Disconnected.")

    def _on_snapshot_inteval(self, event: TimeEvent):
        self._log.debug(f"Taking snapshot; event: {event.name}")
        self._snapshot_task = self._loop.create_task(self._take_snapshot())

    async def _calculate_balance_equity(
        self, balances: List[AccountBalance], quote_currency_code: str = "USDT"
    ) -> Decimal:
        equity = Decimal(0)
        symbols = {}
        usdt = self._instrument_provider.currency(quote_currency_code)
        for b in balances:
            if b.currency == usdt:
                equity += b.total.as_decimal()
            else:
                symbols[f"{b.currency.code}USDT"] = b.total.as_decimal()

        response: List[Dict[str, Any]] = await self._market_api.ticker_price()
        prices = {entry["symbol"]: entry["price"] for entry in response}
        for sym, total in symbols.items():
            try:
                price = prices[sym]
                quote_qty = total * Decimal(price)
                equity += quote_qty
            except KeyError:
                self._log.debug(f"Currency {sym} price not found")
        return equity

    # -- RECONCILIATION ----------------------------------------------------------------------------

    async def generate_order_status_report(self, order: Order) -> OrderStatusReport:  # type: ignore
        """
        Generate an order status report for the given order.

        If an error occurs then logs and returns ``None``.

        Parameters
        ----------
        order : Order
            The order for the report.

        Returns
        -------
        OrderStatusReport or ``None``

        """
        self._log.error(  # pragma: no cover
            "Cannot generate order status report: not yet implemented.",
        )

    async def generate_exec_reports(
        self,
        venue_order_id: VenueOrderId,
        symbol: Symbol,
        since: datetime = None,
    ) -> List[ExecutionReport]:  # type: ignore
        """
        Generate a list of execution reports.

        The returned list may be empty if no trades match the given parameters.

        Parameters
        ----------
        venue_order_id : VenueOrderId
            The venue order ID for the trades.
        symbol : Symbol
            The symbol for the trades.
        since : datetime, optional
            The timestamp to filter trades on.

        Returns
        -------
        list[ExecutionReport]

        """
        self._log.error(  # pragma: no cover
            "Cannot generate execution report: not yet implemented.",
        )

        return []


class BinanceSpotExecutionClient(BinanceExecutionClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: BinanceHttpClient,
        name: str,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        instrument_provider: BinanceInstrumentProvider,
        testnet: Optional[bool] = False,
    ):
        # HTTP API
        account_api = BinanceSpotAccountHttpAPI(client=client)
        market_api = BinanceSpotMarketHttpAPI(client=client)
        user_api = BinanceSpotUserDataHttpAPI(client=client)

        ws_user_api = BinanceSpotUserDataWebSocket(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=self._handle_user_ws_message,
            testnet=testnet,
        )

        super().__init__(
            loop=loop,
            client=client,
            account_type=AccountType.CASH,
            name=name,
            account_id=account_id,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            logger=logger,
            instrument_provider=instrument_provider,
            account_api=account_api,
            market_api=market_api,
            user_api=user_api,
            ws_user_api=ws_user_api,
        )

    def _update_account_state(self, response: Dict[str, Any]) -> None:
        balances = parse_balances(
            self._instrument_provider, response["balances"], "asset", "free", "locked"
        )
        self._log.debug(f"Balances: {balances}")
        if not balances:
            return

        self.generate_account_state(
            balances=balances,
            reported=True,
            ts_event=millis_to_nanos(response["updateTime"]),
        )

    async def _take_snapshot(self):
        try:
            response: Dict[str, Any] = await self._account_api.account(recv_window=5000)
            balances = parse_balances(
                self._instrument_provider, response["balances"], "asset", "free", "locked"
            )
            if not balances:
                return

            balance_equity = await self._calculate_balance_equity(balances)
            self._log.debug(f"Balance: {balances}")
        except BinanceError as ex:
            self._log.error(ex.message)
            return

        account_state: AccountState = AccountState(
            account_id=self.account_id,
            account_type=self.account_type,
            base_currency=self.base_currency,
            reported=True,
            balances=balances,
            info={"positions": [], "equity": float(balance_equity)},
            event_id=self._uuid_factory.generate(),
            ts_event=self._clock.timestamp_ns(),  # binance account updateTime is last change time
            ts_init=self._clock.timestamp_ns(),
        )

        self.generate_account_snapshot(account_state)

    def _handle_user_ws_message(self, raw: bytes):
        msg: Dict[str, Any] = orjson.loads(raw)
        data: Dict[str, Any] = msg.get("data", {})

        # TODO(cs): Uncomment for development
        # self._log.info(str(json.dumps(msg, indent=4)), color=LogColor.GREEN)

        try:
            msg_type: str = data.get("e", "")
            if msg_type == "outboundAccountPosition":
                self._handle_account_position(data)
            elif msg_type == "executionReport":
                self._handle_execution_report(data)
        except Exception as ex:
            self._log.exception(ex)

    def _handle_account_position(self, data: Dict[str, Any]):
        balances = parse_balances(self._instrument_provider, data["B"], "a", "f", "l")
        if not balances:
            return

        self.generate_account_state(
            balances=balances,
            reported=True,
            ts_event=millis_to_nanos(data["u"]),
        )

    def _handle_execution_report(self, data: Dict[str, Any]):
        execution_type: str = data["x"]

        # Parse instrument ID
        symbol: str = data["s"]
        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)

        # Parse client order ID
        client_order_id_str: str = data["c"]
        if not client_order_id_str or not client_order_id_str.startswith("O"):
            client_order_id_str = data["C"]
            if not client_order_id_str:
                if not self._snapshot_enabled:
                    self._log.error(
                        f"Cannot handle execution report: "
                        f"client_order_id ID for {client_order_id_str} not found.",
                    )
            return
        client_order_id = ClientOrderId(client_order_id_str)

        # Fetch strategy ID
        strategy_id: StrategyId = self._cache.strategy_id_for_order(client_order_id)
        if strategy_id is None:
            # TODO(cs): Implement external order handling
            if not self._snapshot_enabled:
                self._log.error(
                    f"Cannot handle execution report: "
                    f"strategy ID for {client_order_id} not found.",
                )
            return

        venue_order_id = VenueOrderId(str(data["i"]))
        order_type_str: str = data["o"]
        ts_event: int = millis_to_nanos(data["E"])

        if execution_type == "NEW":
            self.generate_order_accepted(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                ts_event=ts_event,
            )
        elif execution_type == "TRADE":
            instrument: Instrument = self._instrument_provider.find(instrument_id=instrument_id)

            # Determine commission
            commission_asset: str = data["N"]
            commission_amount: str = data["n"]
            if commission_asset is not None:
                commission = Money.from_str(f"{commission_amount} {commission_asset}")
            else:
                # Binance typically charges commission as base asset or BNB
                commission = Money(0, instrument.base_currency)

            self.generate_order_filled(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                venue_position_id=None,  # NETTING accounts
                execution_id=ExecutionId(str(data["t"])),  # Trade ID
                order_side=OrderSideParser.from_str_py(data["S"]),
                order_type=parse_order_type(order_type_str),
                last_qty=Quantity.from_str(data["l"]),
                last_px=Price.from_str(data["L"]),
                quote_currency=instrument.quote_currency,
                commission=commission,
                liquidity_side=LiquiditySide.MAKER if data["m"] else LiquiditySide.TAKER,
                ts_event=ts_event,
            )
        elif execution_type == "CANCELED" or execution_type == "EXPIRED":
            self.generate_order_canceled(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                ts_event=ts_event,
            )

    # -- COMMAND HANDLERS --------------------------------------------------------------------------

    def submit_order(self, command: SubmitOrder) -> None:
        if command.order.type == OrderType.STOP_MARKET:
            self._log.error(
                "Cannot submit order: "
                "STOP_MARKET orders not supported by the exchange for SPOT markets. "
                "Use any of MARKET, LIMIT, STOP_LIMIT."
            )
            return
        elif command.order.type == OrderType.STOP_LIMIT:
            self._log.warning(
                "STOP_LIMIT `post_only` orders not supported by the exchange. "
                "This order may become a liquidity TAKER."
            )
        if command.order.time_in_force not in VALID_TIF:
            self._log.error(
                f"Cannot submit order: "
                f"{TimeInForceParser.to_str_py(command.order.time_in_force)} "
                f"not supported by the exchange. Use any of {VALID_TIF}.",
            )
            return
        self._loop.create_task(self._submit_order(command))

    def submit_order_list(self, command: SubmitOrderList) -> None:
        self._loop.create_task(self._submit_order_list(command))

    def modify_order(self, command: ModifyOrder) -> None:
        self._log.error(  # pragma: no cover
            "Cannot modify order: Not supported by the exchange.",
        )

    def cancel_order(self, command: CancelOrder) -> None:
        self._loop.create_task(self._cancel_order(command))

    def cancel_all_orders(self, command: CancelAllOrders) -> None:
        self._loop.create_task(self._cancel_all_orders(command))

    async def _submit_order(self, command: SubmitOrder) -> None:
        self._log.debug(f"Submitting {command.order}.")

        # Generate event here to ensure correct ordering of events
        self.generate_order_submitted(
            strategy_id=command.strategy_id,
            instrument_id=command.instrument_id,
            client_order_id=command.order.client_order_id,
            ts_event=self._clock.timestamp_ns(),
        )

        try:
            if command.order.type == OrderType.MARKET:
                await self._submit_market_order(command)
            elif command.order.type == OrderType.LIMIT:
                await self._submit_limit_order(command)
            elif command.order.type == OrderType.STOP_LIMIT:
                await self._submit_stop_limit_order(command)
        except BinanceError as ex:
            self.generate_order_rejected(
                strategy_id=command.strategy_id,
                instrument_id=command.instrument_id,
                client_order_id=command.order.client_order_id,
                reason=ex.message,  # type: ignore  # TODO(cs): Improve errors
                ts_event=self._clock.timestamp_ns(),  # TODO(cs): Parse from response
            )

    async def _submit_market_order(self, command: SubmitOrder):
        order: MarketOrder = command.order
        await self._account_api.new_order(
            symbol=order.instrument_id.symbol.value,
            side=OrderSideParser.to_str_py(order.side),
            type="MARKET",
            quantity=str(order.quantity),
            new_client_order_id=order.client_order_id.value,
            recv_window=5000,
        )

    async def _submit_limit_order(self, command: SubmitOrder):
        order: LimitOrder = command.order
        if order.is_post_only:
            time_in_force = None
        else:
            time_in_force = TimeInForceParser.to_str_py(order.time_in_force)

        await self._account_api.new_order(
            symbol=order.instrument_id.symbol.value,
            side=OrderSideParser.to_str_py(order.side),
            type=binance_order_type(order=order),
            time_in_force=time_in_force,
            quantity=str(order.quantity),
            price=str(order.price),
            iceberg_qty=str(order.display_qty) if order.display_qty is not None else None,
            new_client_order_id=order.client_order_id.value,
            recv_window=5000,
        )

    async def _submit_stop_limit_order(self, command: SubmitOrder):
        order: StopLimitOrder = command.order

        # Get current market price
        response: Dict[str, Any] = await self._market_api.ticker_price(
            order.instrument_id.symbol.value
        )
        market_price = Decimal(response["price"])

        await self._account_api.new_order(
            symbol=order.instrument_id.symbol.value,
            side=OrderSideParser.to_str_py(order.side),
            type=binance_order_type(order=order, market_price=market_price),
            time_in_force=TimeInForceParser.to_str_py(order.time_in_force),
            quantity=str(order.quantity),
            price=str(order.price),
            stop_price=str(order.trigger),
            iceberg_qty=str(order.display_qty) if order.display_qty is not None else None,
            new_client_order_id=order.client_order_id.value,
            recv_window=5000,
        )

    async def _submit_order_list(self, command: SubmitOrderList) -> None:
        self._log.error(  # pragma: no cover
            "Cannot submit order list: not yet implemented.",
        )

    async def _cancel_order(self, command: CancelOrder) -> None:
        self._log.debug(f"Canceling order {command.client_order_id.value}.")

        self.generate_order_pending_cancel(
            strategy_id=command.strategy_id,
            instrument_id=command.instrument_id,
            client_order_id=command.client_order_id,
            venue_order_id=command.venue_order_id,
            ts_event=self._clock.timestamp_ns(),
        )

        try:
            await self._account_api.cancel_order(
                symbol=command.instrument_id.symbol.value,
                orig_client_order_id=command.client_order_id.value,
            )
        except BinanceError as ex:
            self._log.error(ex.message)  # type: ignore  # TODO(cs): Improve errors

    async def _cancel_all_orders(self, command: CancelAllOrders) -> None:
        self._log.debug(f"Canceling all orders for {command.instrument_id.value}.")

        # Cancel all in-flight orders
        inflight_orders = self._cache.orders_inflight(
            instrument_id=command.instrument_id,
            strategy_id=command.strategy_id,
        )
        for order in inflight_orders:
            self.generate_order_pending_cancel(
                strategy_id=order.strategy_id,
                instrument_id=order.instrument_id,
                client_order_id=order.client_order_id,
                venue_order_id=order.venue_order_id,
                ts_event=self._clock.timestamp_ns(),
            )

        # Cancel all working orders
        working_orders = self._cache.orders_working(
            instrument_id=command.instrument_id,
            strategy_id=command.strategy_id,
        )
        for order in working_orders:
            self.generate_order_pending_cancel(
                strategy_id=order.strategy_id,
                instrument_id=order.instrument_id,
                client_order_id=order.client_order_id,
                venue_order_id=order.venue_order_id,
                ts_event=self._clock.timestamp_ns(),
            )

        try:
            await self._account_api.cancel_open_orders(
                symbol=command.instrument_id.symbol.value,
            )
        except BinanceError as ex:
            self._log.error(ex.message)  # type: ignore  # TODO(cs): Improve errors


class BinanceFutureExecutionClient(BinanceExecutionClient):
    """
    Provides an execution client for Binance FUTURE markets.
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: BinanceHttpClient,
        name: str,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        instrument_provider: BinanceInstrumentProvider,
        testnet: Optional[bool] = False,
    ):
        # HTTP API
        account_api = BinanceFutureAccountHttpAPI(client=client)
        market_api = BinanceFutureMarketHttpAPI(client=client)
        user_api = BinanceFutureUserDataHttpAPI(client=client)

        ws_user_api = BinanceFutureUserDataWebSocket(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=self._handle_user_ws_message,
            testnet=testnet,
        )

        super().__init__(
            loop=loop,
            client=client,
            account_type=AccountType.MARGIN,
            name=name,
            account_id=account_id,
            msgbus=msgbus,
            cache=cache,
            clock=clock,
            logger=logger,
            instrument_provider=instrument_provider,
            account_api=account_api,
            market_api=market_api,
            user_api=user_api,
            ws_user_api=ws_user_api,
        )

        self._account_api = account_api
        self._dual_side_position = False
        self._position_side_by_client_order_id: Dict[ClientOrderId, PositionSide] = {}

    def _update_account_state(self, response: Dict[str, Any]) -> None:
        if self._snapshot_enabled:
            self.generate_reported_account(
                parse_reported_position(self._instrument_provider, response["positions"]),
                parse_reported_wallet_balance(self._instrument_provider, response["assets"]),
                millis_to_nanos(response["updateTime"]),
            )

        balances = parse_balances(
            self._instrument_provider, response["assets"], "asset", "marginBalance", "_"
        )
        self._log.debug(f"Balances: {balances}")
        if not balances:
            return

        self.generate_account_state(
            balances=balances,
            reported=True,
            ts_event=millis_to_nanos(response["updateTime"]),
        )

    async def _get_account_setting(self):
        response = await self._account_api.position_mode()
        self._dual_side_position = response["dualSidePosition"]

    async def _take_snapshot(self):
        try:
            response: Dict[str, Any] = await self._account_api.account(recv_window=5000)
            balances = parse_balances(
                self._instrument_provider, response["assets"], "asset", "marginBalance", "_"
            )
            if not balances:
                return

            balance_equity = await self._calculate_balance_equity(balances)
            self._log.debug(f"Balance: {balances}")
        except BinanceError as ex:
            self._log.error(ex.message)
            return

        positions = parse_positions(response["positions"])

        account_state: AccountState = AccountState(
            account_id=self.account_id,
            account_type=self.account_type,
            base_currency=self.base_currency,
            reported=True,
            balances=balances,
            info={"positions": positions, "equity": float(balance_equity)},
            event_id=self._uuid_factory.generate(),
            ts_event=self._clock.timestamp_ns(),  # binance account updateTime is last change time
            ts_init=self._clock.timestamp_ns(),
        )

        self.generate_account_snapshot(account_state)

    def _handle_user_ws_message(self, raw: bytes):
        msg: Dict[str, Any] = orjson.loads(raw)
        data: Dict[str, Any] = msg.get("data", {})

        # TODO(cs): Uncomment for development
        # self._log.info(str(json.dumps(msg, indent=4)), color=LogColor.GREEN)

        try:
            msg_type: str = data.get("e", "")
            if msg_type == "ACCOUNT_UPDATE":
                self._handle_account_position(data)
            elif msg_type == "ORDER_TRADE_UPDATE":
                self._handle_execution_report(data)
            elif msg_type == "ACCOUNT_CONFIG_UPDATE":
                self._handle_account_config(data)
        except Exception as ex:
            self._log.exception(ex)

    def _handle_account_position(self, data: Dict[str, Any]):
        ts_event = millis_to_nanos(data["E"])
        if "a" not in data:
            return

        positions = (
            parse_reported_positions_ws(self._instrument_provider, data["a"]["P"])
            if data["a"].get("P")
            else []
        )
        balances = (
            parse_reported_wallet_balance_ws(self._instrument_provider, data["a"]["B"])
            if data["a"].get("B")
            else []
        )

        if self._snapshot_enabled:
            self.generate_reported_account(positions, balances, ts_event)

        balances = parse_balances(self._instrument_provider, data["a"]["B"], "a", "wb", "_")
        if not balances:
            return

        self.generate_account_state(
            balances=balances,
            reported=True,
            ts_event=ts_event,
        )

    def _handle_account_config(self, data: Dict[str, Any]):
        ts_event = millis_to_nanos(data["E"])

        if "ac" in data and self._snapshot_enabled:
            symbol: str = data["ac"]["s"]
            instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)

            multiplier = int(data["ac"]["l"])
            position_update = []
            for side in (SideWithMode.BOTH, SideWithMode.LONG, SideWithMode.SHORT):
                position_update.append(
                    ReportedPosition(
                        instrument_id=instrument_id,
                        side=side,
                        multiplier=multiplier,
                    )
                )

            self.generate_reported_account(position_update, [], ts_event)

    def _handle_execution_report(self, data: Dict[str, Any]):  # noqa: C901
        ts_event = millis_to_nanos(data["E"])
        data = data["o"]

        execution_type: str = data["x"]

        # Parse instrument ID
        symbol: str = data["s"]
        instrument_id = self._instrument_provider.find_instrument_id_by_local_symbol(symbol)

        # Parse client order ID
        client_order_id_str: str = data["c"]
        if not client_order_id_str or not client_order_id_str.startswith("O"):
            if not self._snapshot_enabled:
                self._log.error(
                    f"Cannot handle execution report: "
                    f"client_order_id ID for {client_order_id_str} not found.",
                )
            return

        client_order_id = ClientOrderId(client_order_id_str)

        # Fetch strategy ID
        strategy_id: StrategyId = self._cache.strategy_id_for_order(client_order_id)
        if strategy_id is None:
            # TODO(cs): Implement external order handling
            if not self._snapshot_enabled:
                self._log.error(
                    f"Cannot handle execution report: "
                    f"strategy ID for {client_order_id} not found.",
                )
            return

        venue_order_id = VenueOrderId(str(data["i"]))
        order_type_str: str = data["o"]

        if execution_type == "NEW":
            self.generate_order_accepted(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                ts_event=ts_event,
            )
        elif execution_type == "TRADE":
            instrument: Instrument = self._instrument_provider.find(instrument_id=instrument_id)

            # Determine commission
            commission_asset: str = data["N"]
            commission_amount: str = data["n"]
            if commission_asset is not None:
                commission = Money.from_str(f"{commission_amount} {commission_asset}")
            else:
                # Binance typically charges commission as base asset or BNB
                commission = Money(0, instrument.base_currency)

            venue_position_id = None
            # TODO: Avoid same side order generate 2 different position_id
            if (
                self._dual_side_position
                and client_order_id in self._position_side_by_client_order_id
            ):
                side = self._position_side_by_client_order_id[client_order_id]
                open_positions = self._cache.positions_open(
                    instrument_id=instrument_id, strategy_id=strategy_id
                )
                position = next(
                    filter(lambda position: position.side == side, open_positions), None
                )
                if position is not None:
                    venue_position_id = position.id

            self.generate_order_filled(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                venue_position_id=venue_position_id,
                execution_id=ExecutionId(str(data["t"])),  # Trade ID
                order_side=OrderSideParser.from_str_py(data["S"]),
                order_type=parse_future_order_type(order_type_str),
                last_qty=Quantity.from_str(data["l"]),
                last_px=Price.from_str(data["L"]),
                quote_currency=instrument.quote_currency,
                commission=commission,
                liquidity_side=LiquiditySide.MAKER if data["m"] else LiquiditySide.TAKER,
                ts_event=ts_event,
            )
        elif execution_type == "CANCELED" or execution_type == "EXPIRED":
            self.generate_order_canceled(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                ts_event=ts_event,
            )

    # -- COMMAND HANDLERS --------------------------------------------------------------------------

    def submit_order(self, command: SubmitOrder) -> None:
        if command.order.time_in_force not in VALID_TIF:
            self._log.error(
                f"Cannot submit order: "
                f"{TimeInForceParser.to_str_py(command.order.time_in_force)} "
                f"not supported by the exchange. Use any of {VALID_TIF}.",
            )
            return
        self._loop.create_task(self._submit_order(command))

    def submit_order_list(self, command: SubmitOrderList) -> None:
        self._loop.create_task(self._submit_order_list(command))

    def modify_order(self, command: ModifyOrder) -> None:
        self._log.error(  # pragma: no cover
            "Cannot modify order: Not supported by the exchange.",
        )

    def cancel_order(self, command: CancelOrder) -> None:
        self._loop.create_task(self._cancel_order(command))

    def cancel_all_orders(self, command: CancelAllOrders) -> None:
        self._loop.create_task(self._cancel_all_orders(command))

    async def _submit_order(self, command: SubmitOrder) -> None:  # noqa: C901
        self._log.debug(f"Submitting {command.order}.")

        position = None
        position_id = command.position_id
        if position_id is not None:
            position = self._cache.position(position_id)
            if position is None:
                self._log.error(f"Position {position_id} not found")
                return
        elif self._dual_side_position:  # When not specify position_id, open position with same side
            if command.order.side == OrderSide.BUY:
                side = PositionSide.LONG
            else:
                side = PositionSide.SHORT
            self._position_side_by_client_order_id[command.order.client_order_id] = side

        # Generate event here to ensure correct ordering of events
        self.generate_order_submitted(
            strategy_id=command.strategy_id,
            instrument_id=command.instrument_id,
            client_order_id=command.order.client_order_id,
            ts_event=self._clock.timestamp_ns(),
        )

        try:
            if command.order.type == OrderType.MARKET:
                await self._submit_market_order(command.order, position)
            elif command.order.type == OrderType.LIMIT:
                await self._submit_limit_order(command.order, position)
            elif command.order.type == OrderType.STOP_LIMIT:
                await self._submit_stop_limit_order(command.order, position)
            elif command.order.type == OrderType.STOP_MARKET:
                await self._submit_stop_market_order(command.order, position)
        except BinanceError as ex:
            self.generate_order_rejected(
                strategy_id=command.strategy_id,
                instrument_id=command.instrument_id,
                client_order_id=command.order.client_order_id,
                reason=ex.message,  # type: ignore  # TODO(cs): Improve errors
                ts_event=self._clock.timestamp_ns(),  # TODO(cs): Parse from response
            )

    def _position_kwargs(self, order: Order, position: Optional[Position] = None) -> Dict:
        if self._dual_side_position:
            if position is None:
                side = "LONG" if order.side == OrderSide.BUY else "SHORT"
            else:
                side = PositionSideParser.to_str_py(position.side)
            return {"position_side": side}
        else:
            return {"position_side": "BOTH", "reduce_only": order.is_reduce_only}

    async def _submit_market_order(self, order: MarketOrder, position: Optional[Position] = None):

        await self._account_api.new_order(
            symbol=order.instrument_id.symbol.value,
            side=OrderSideParser.to_str_py(order.side),
            type="MARKET",
            quantity=str(order.quantity),
            new_client_order_id=order.client_order_id.value,
            recv_window=5000,
            **self._position_kwargs(order, position),
        )

    async def _submit_limit_order(self, order: LimitOrder, position: Optional[Position] = None):
        if order.is_post_only:
            time_in_force = "GTX"  # binance Good Till Crossing
        else:
            time_in_force = TimeInForceParser.to_str_py(order.time_in_force)

        await self._account_api.new_order(
            symbol=order.instrument_id.symbol.value,
            side=OrderSideParser.to_str_py(order.side),
            type="LIMIT",
            time_in_force=time_in_force,
            quantity=str(order.quantity),
            price=str(order.price),
            new_client_order_id=order.client_order_id.value,
            recv_window=5000,
            **self._position_kwargs(order, position),
        )

    async def _submit_stop_limit_order(
        self, order: StopLimitOrder, position: Optional[Position] = None
    ):
        # Get current market price
        response: Dict[str, Any] = await self._market_api.ticker_price(
            order.instrument_id.symbol.value
        )
        market_price = Decimal(response["price"])

        await self._account_api.new_order(
            symbol=order.instrument_id.symbol.value,
            side=OrderSideParser.to_str_py(order.side),
            type=binance_future_order_type(order=order, market_price=market_price),
            time_in_force=TimeInForceParser.to_str_py(order.time_in_force),
            quantity=str(order.quantity),
            price=str(order.price),
            stop_price=str(order.trigger),
            new_client_order_id=order.client_order_id.value,
            recv_window=5000,
            **self._position_kwargs(order, position),
        )

    async def _submit_stop_market_order(
        self, order: StopMarketOrder, position: Optional[Position] = None
    ):
        # Get current market price
        response: Dict[str, Any] = await self._market_api.ticker_price(
            order.instrument_id.symbol.value
        )
        market_price = Decimal(response["price"])

        await self._account_api.new_order(
            symbol=order.instrument_id.symbol.value,
            side=OrderSideParser.to_str_py(order.side),
            type=binance_future_order_type(order=order, market_price=market_price),
            time_in_force=TimeInForceParser.to_str_py(order.time_in_force),
            quantity=str(order.quantity),
            stop_price=str(order.trigger),
            new_client_order_id=order.client_order_id.value,
            recv_window=5000,
            **self._position_kwargs(order, position),
        )

    async def _submit_order_list(self, command: SubmitOrderList) -> None:
        self._log.error(  # pragma: no cover
            "Cannot submit order list: not yet implemented.",
        )

    async def _cancel_order(self, command: CancelOrder) -> None:
        self._log.debug(f"Canceling order {command.client_order_id.value}.")

        self.generate_order_pending_cancel(
            strategy_id=command.strategy_id,
            instrument_id=command.instrument_id,
            client_order_id=command.client_order_id,
            venue_order_id=command.venue_order_id,
            ts_event=self._clock.timestamp_ns(),
        )

        try:
            await self._account_api.cancel_order(
                symbol=command.instrument_id.symbol.value,
                orig_client_order_id=command.client_order_id.value,
            )
        except BinanceError as ex:
            self._log.error(ex.message)  # type: ignore  # TODO(cs): Improve errors

    async def _cancel_all_orders(self, command: CancelAllOrders) -> None:
        self._log.debug(f"Canceling all orders for {command.instrument_id.value}.")

        # Cancel all in-flight orders
        inflight_orders = self._cache.orders_inflight(
            instrument_id=command.instrument_id,
            strategy_id=command.strategy_id,
        )
        for order in inflight_orders:
            self.generate_order_pending_cancel(
                strategy_id=order.strategy_id,
                instrument_id=order.instrument_id,
                client_order_id=order.client_order_id,
                venue_order_id=order.venue_order_id,
                ts_event=self._clock.timestamp_ns(),
            )

        # Cancel all working orders
        working_orders = self._cache.orders_working(
            instrument_id=command.instrument_id,
            strategy_id=command.strategy_id,
        )
        for order in working_orders:
            self.generate_order_pending_cancel(
                strategy_id=order.strategy_id,
                instrument_id=order.instrument_id,
                client_order_id=order.client_order_id,
                venue_order_id=order.venue_order_id,
                ts_event=self._clock.timestamp_ns(),
            )

        try:
            await self._account_api.cancel_open_orders(
                symbol=command.instrument_id.symbol.value,
            )
        except BinanceError as ex:
            self._log.error(ex.message)  # type: ignore  # TODO(cs): Improve errors
