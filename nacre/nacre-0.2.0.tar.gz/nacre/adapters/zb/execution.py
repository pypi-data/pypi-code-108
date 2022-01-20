import asyncio
import os
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import orjson
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
from nautilus_trader.model.enums import OrderStatus
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.enums import PositionSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TimeInForceParser
from nautilus_trader.model.enums import VenueType
from nautilus_trader.model.events.account import AccountState
from nautilus_trader.model.identifiers import AccountId
from nautilus_trader.model.identifiers import ClientId
from nautilus_trader.model.identifiers import ClientOrderId
from nautilus_trader.model.identifiers import ExecutionId
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import Symbol
from nautilus_trader.model.identifiers import VenueOrderId
from nautilus_trader.model.instruments.base import Instrument
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orders.base import Order
from nautilus_trader.model.orders.list import OrderList
from nautilus_trader.msgbus.bus import MessageBus

from nacre.adapters.zb.http.api.future_account import ZbFutureAccountHttpAPI
from nacre.adapters.zb.http.api.future_market import ZbFutureMarketHttpAPI
from nacre.adapters.zb.http.api.spot_account import ZbSpotAccountHttpAPI
from nacre.adapters.zb.http.api.spot_market import ZbSpotMarketHttpAPI
from nacre.adapters.zb.http.client import ZbHttpClient
from nacre.adapters.zb.http.error import ZbError
from nacre.adapters.zb.parsing import parse_account_balances_raw
from nacre.adapters.zb.parsing import parse_positions
from nacre.adapters.zb.parsing import parse_reported_position
from nacre.adapters.zb.parsing import parse_reported_wallet_balance
from nacre.adapters.zb.parsing import parse_zb_order_side
from nacre.adapters.zb.parsing import parse_zb_order_type
from nacre.adapters.zb.parsing import zb_order_params
from nacre.adapters.zb.providers import ZbInstrumentProvider
from nacre.adapters.zb.websocket.user import ZbFutureUserDataWebSocket
from nacre.adapters.zb.websocket.user import ZbSpotUserDataWebSocket
from nacre.adapters.zb.websocket.user import ZbUserDataWebSocket
from nacre.live.execution_client import LiveExecutionClient


VALID_TIF = (TimeInForce.GTC, TimeInForce.FOK, TimeInForce.IOC)


class ZbExecutionClient(LiveExecutionClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: ZbHttpClient,
        account_type: AccountType,
        name: str,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        instrument_provider: ZbInstrumentProvider,
        account_api: ZbFutureAccountHttpAPI,
        market_api: ZbFutureMarketHttpAPI,
        ws_user_api: ZbUserDataWebSocket,
    ):

        self._client = client

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
            config={"name": f"ZbExecClient-{name}"},
        )
        self._client = client

        # Hot caches
        self._instrument_ids: Dict[str, InstrumentId] = {}
        self._order_types: Dict[VenueOrderId, OrderType] = {}
        self._last_filled: Dict[VenueOrderId, Quantity] = {}

        # HTTP API
        self._account_api = account_api
        self._market_api = market_api

        # WebSocket API
        self._ws_user_api = ws_user_api

        # if take account_snapshot
        self._snapshot_enabled = os.environ.get("SNAPSHOT_ENABLED", False)

        self._snapshot_task = None
        self._snapshot_timer = None
        self._dual_side_position = True  # Zb future only support hedge mode for now

    def connect(self):
        self._log.info("Connecting...")
        self._loop.create_task(self._connect())

    def disconnect(self):
        self._log.info("Disconnecting...")
        self._loop.create_task(self._disconnect())

    async def _connect(self):
        if not self._client.connected:
            await self._client.connect()
        try:
            await self._instrument_provider.load_all_or_wait_async()
            self._log.info("ZbHttpClient connected")
        except Exception as ex:
            self._log.exception(ex)
            return

        await self._update_account_state()

        # Connect WebSocket clients
        await self._connect_websockets()

        self._set_connected(True)
        assert self.is_connected
        self._log.info("Connected.")

        if self._snapshot_enabled:
            self._snapshot_timer = self._clock.set_timer(
                name=self.account_id.value,
                interval=timedelta(minutes=1),
                start_time=None,
                stop_time=None,
                callback=self._on_snapshot_inteval,
            )

    async def _connect_websockets(self):
        await self._ws_user_api.connect()
        await self._ws_user_api.logged_in()

    async def _disconnect(self):
        if self._snapshot_timer:
            self._log.debug("Canceling `snapshot_timer` timer...")
            self._snapshot_timer.cancel()

        if self._snapshot_task:
            self._log.debug("Canceling `snapshot_task` task...")
            self._snapshot_task.cancel()

        # Disconnect WebSocket clients
        if self._ws_user_api.is_connected:
            await self._ws_user_api.disconnect()

        if self._client.connected:
            await self._client.disconnect()

        self._set_connected(False)
        self._log.info("Disconnected.")

    def _on_snapshot_inteval(self, event: TimeEvent):
        self._log.debug(f"Taking snapshot; event: {event.name}")
        self._snapshot_task = self._loop.create_task(self._take_snapshot())

    async def _take_snapshot(self):
        aws = [
            self._account_api.get_account(),
            self._account_api.get_positions(),
        ]
        try:
            responses = await asyncio.gather(*aws)
            raw_account, raw_positions = responses
        except ZbError as ex:
            self._log.error(ex.message)
            return

        equity = raw_account["data"]["account"]["accountNetBalance"]

        self._log.debug(f"Account {self.account_id} equity: {equity}")

        balances = parse_account_balances_raw(
            self._instrument_provider, raw_account["data"]["assets"]
        )

        positions = parse_positions(raw_positions["data"])

        account_state = AccountState(
            account_id=self.account_id,
            account_type=self.account_type,
            base_currency=self.base_currency,
            reported=True,
            balances=balances,
            info={"positions": positions, "equity": float(equity)},
            event_id=self._uuid_factory.generate(),
            ts_event=self._clock.timestamp_ns(),
            ts_init=self._clock.timestamp_ns(),
        )

        self.generate_account_snapshot(account_state)


class ZbSpotExecutionClient(ZbExecutionClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: ZbHttpClient,
        name: str,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        instrument_provider: ZbInstrumentProvider,
    ):
        # HTTP API
        account_api = ZbSpotAccountHttpAPI(client=client)
        market_api = ZbSpotMarketHttpAPI(client=client)

        ws_user_api = ZbSpotUserDataWebSocket(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=self._handle_user_ws_message,
            key=client.api_key,
            hashed_secret=client.hashed_secret,
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
            ws_user_api=ws_user_api,
        )

    async def _update_account_state(self) -> None:
        pass


class ZbFutureExecutionClient(ZbExecutionClient):
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        client: ZbHttpClient,
        name: str,
        account_id: AccountId,
        msgbus: MessageBus,
        cache: Cache,
        clock: LiveClock,
        logger: Logger,
        instrument_provider: ZbInstrumentProvider,
        socks_proxy: str = None,
    ):
        # HTTP API
        account_api = ZbFutureAccountHttpAPI(client=client)
        market_api = ZbFutureMarketHttpAPI(client=client)

        ws_user_api = ZbFutureUserDataWebSocket(
            loop=loop,
            clock=clock,
            logger=logger,
            handler=self._handle_user_ws_message,
            key=client.api_key,
            hashed_secret=client.hashed_secret,
            socks_proxy=socks_proxy,
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
            ws_user_api=ws_user_api,
        )

        # cache for position update
        self._position_changes: Dict[str, float] = {}
        self._position_side_by_client_order_id: Dict[ClientOrderId, PositionSide] = {}

    def _handle_user_ws_message(self, raw: bytes):
        msg: Dict[str, Any] = orjson.loads(raw)
        data = msg.get("data")

        chan: Optional[str] = msg.get("channel")
        err: Optional[str] = msg.get("errorCode")

        if err:
            self._log.error(f"Subscribe failed for channel: {chan}, error: {err}")
            return
        if msg.get("action") == "login" and data == "success":
            return

        if chan == "Fund.assetChange":
            self._handle_asset_update(data)
        elif chan == "Positions.change":
            self._handle_position_update(data)
        elif chan == "Trade.orderChange":
            self._handle_order_update(data)
        elif chan in ("Trade.order", "Trade.cancelAllOrders", "Trade.cancelOrder"):
            pass
        else:
            self._log.warning(f"Unrecognized websocket message type, msg {msg}")
            return

    def _handle_asset_update(self, data: Dict[str, Any]):
        if self._snapshot_enabled:
            self.generate_reported_account(
                [],
                parse_reported_wallet_balance(self._instrument_provider, data),
                self._clock.timestamp_ns(),
            )

    def _handle_position_update(self, data: Dict[str, Any]):
        if self._snapshot_enabled:
            # ignore unrealized pnl update
            if not self._check_if_position_changed(data):
                return

            self.generate_reported_account(
                parse_reported_position(self._instrument_provider, [data]),
                [],
                millis_to_nanos(float(data["modifyTime"])),
            )

    def _check_if_position_changed(self, data: Dict[str, Any]) -> bool:
        symbol = data["marketName"]
        if symbol not in self._position_changes:
            self._position_changes[symbol] = data["amount"]
            return True

        if self._position_changes[symbol] == data["amount"]:
            # position not changed
            return False

        self._position_changes[symbol] = data["amount"]
        return True

    def _handle_order_update(self, data: Dict[str, Any]):  # noqa: C901
        self._log.debug(f"Received order update {data}")

        venue_order_id = VenueOrderId(data["id"])
        client_order_id_str = data.get("orderCode")
        if client_order_id_str is None:
            self._log.warning(f"Cannot fill un-cached order with {repr(venue_order_id)}")
            return
        client_order_id = ClientOrderId(client_order_id_str)

        strategy_id = self._cache.strategy_id_for_order(client_order_id)
        if strategy_id is None:
            if not self._snapshot_enabled:
                self._log.error(
                    f"Cannot handle order update: " f"strategy ID for {client_order_id} not found",
                )
            return
        ts_event: int = millis_to_nanos(int(data["modifyTime"]))

        instrument_id = self._instrument_provider.find_instrument_id_by_local_market_id(
            data["marketId"]
        )

        order_status = data["showStatus"]
        if order_status == 1:  # 1 for accepted
            self.generate_order_accepted(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                ts_event=ts_event,
            )
        elif order_status == 2 or order_status == 3:  # 2 for partial filled, 3 for filled
            instrument: Instrument = self._instrument_provider.find(instrument_id)
            order_type = parse_zb_order_type(data["action"])

            # calculate last qty
            current_filled = Quantity.from_str(data["tradeAmount"])
            if venue_order_id not in self._last_filled:
                self._last_filled[venue_order_id] = current_filled
                last_qty = current_filled
            else:
                last_qty = Quantity(
                    current_filled - self._last_filled[venue_order_id], instrument.size_precision
                )
                self._last_filled[venue_order_id] = current_filled

            # get commission and liquidity_side, hard code for now
            if order_type == OrderType.MARKET:
                commission_fee = (
                    Decimal(data["avgPrice"]) * last_qty.as_decimal()
                ) * instrument.taker_fee
                liquidity_side = LiquiditySide.TAKER
            else:
                commission_fee = (
                    Decimal(data["avgPrice"]) * last_qty.as_decimal()
                ) * instrument.maker_fee
                liquidity_side = LiquiditySide.MAKER
            commission = Money(commission_fee, instrument.quote_currency)

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
                execution_id=ExecutionId(
                    data["modifyTime"]
                ),  # no trade id returned, use create time instead
                order_side=parse_zb_order_side(data["type"]),
                order_type=order_type,
                last_qty=last_qty,
                last_px=Price.from_str(data["avgPrice"]),
                quote_currency=instrument.quote_currency,
                commission=commission,  # temp fix
                liquidity_side=liquidity_side,  # temp fix
                ts_event=ts_event,
            )
        elif order_status == 4:  # 4 for canceling
            self.generate_order_pending_cancel(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                ts_event=ts_event,
            )
        elif (
            order_status == 5 or order_status == 7
        ):  # 5 for canceled, 7 for partial filled partial cancel
            # Some order canceled immediately without "showStatus" = 1 pushed
            if (
                order_status == 5
                and self._cache.order(client_order_id).status == OrderStatus.SUBMITTED
            ):
                self.generate_order_accepted(
                    strategy_id=strategy_id,
                    instrument_id=instrument_id,
                    client_order_id=client_order_id,
                    venue_order_id=venue_order_id,
                    ts_event=ts_event,
                )
            self.generate_order_canceled(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                ts_event=ts_event,
            )
        elif order_status == 6:  # 6 for cancel failed
            self.generate_order_cancel_rejected(
                strategy_id=strategy_id,
                instrument_id=instrument_id,
                client_order_id=client_order_id,
                venue_order_id=venue_order_id,
                reason="",  # type: ignore  # TODO(cs): Improve errors
                ts_event=ts_event,
            )

    async def _update_account_state(self) -> None:
        aws = [
            self._account_api.get_account(),
            self._account_api.get_positions(),
        ]
        try:
            responses = await asyncio.gather(*aws)
            raw_account, raw_positions = responses
        except (asyncio.TimeoutError, ZbError) as ex:
            self._log.exception(ex)
            return

        if self._snapshot_enabled:
            self.generate_reported_account(
                parse_reported_position(self._instrument_provider, raw_positions["data"]),
                parse_reported_wallet_balance(
                    self._instrument_provider, raw_account["data"]["account"]
                ),
                self._clock.timestamp_ns(),
            )

        balances = parse_account_balances_raw(
            self._instrument_provider, raw_account["data"]["assets"]
        )
        if not balances:
            return

        self.generate_account_state(
            balances=balances,
            reported=True,
            ts_event=self._clock.timestamp_ns(),  # zb account doesn't provide updateTime
        )

    # -- COMMAND HANDLERS --------------------------------------------------------------------------

    def submit_order(self, command: SubmitOrder) -> None:
        order: Order = command.order
        if order.type == OrderType.STOP_MARKET:
            self._log.error(
                "Cannot submit order: "
                "STOP_MARKET orders not supported by the exchange for zb FUTURE markets. "
                "Use any of MARKET, LIMIT, STOP_LIMIT."
            )
            return
        elif order.type == OrderType.STOP_LIMIT:
            self._log.error(
                "Cannot submit order: "
                "STOP_LIMIT orders not supported by the exchange for zb FUTURE markets. "
                "Use any of MARKET, LIMIT, STOP_LIMIT."
            )
            return
        if order.time_in_force not in VALID_TIF:
            self._log.error(
                f"Cannot submit order: "
                f"{TimeInForceParser.to_str_py(order.time_in_force)} "
                f"not supported by the exchange. Use any of {VALID_TIF}.",
            )
            return
        self._loop.create_task(self._submit_order(command))

    def submit_order_list(self, command: SubmitOrderList) -> None:
        order_list: OrderList = command.list
        self._loop.create_task(self._submit_order_list(order_list))

    def modify_order(self, command: ModifyOrder) -> None:
        self._log.error(  # pragma: no cover
            "Cannot modify order: Not supported by the exchange.",
        )

    def cancel_order(self, command: CancelOrder) -> None:
        self._loop.create_task(self._cancel_order(command))

    def cancel_all_orders(self, command: CancelAllOrders) -> None:
        self._loop.create_task(self._cancel_all_order(command))

    async def _submit_order(self, command: SubmitOrder) -> None:
        order: Order = command.order
        self._log.debug(f"Submitting {order}.")

        position = None
        position_id = command.position_id
        if position_id is not None:
            position = self._cache.position(position_id)
            if position is None:
                self._log.error(f"Position {position_id} not found")
                return
        elif self._dual_side_position:  # When not specify position_id, open position with same side
            if order.side == OrderSide.BUY:
                side = PositionSide.LONG
            else:
                side = PositionSide.SHORT
            self._position_side_by_client_order_id[order.client_order_id] = side

        # Generate event here to ensure correct ordering of events
        self.generate_order_submitted(
            strategy_id=command.strategy_id,
            instrument_id=command.instrument_id,
            client_order_id=order.client_order_id,
            ts_event=self._clock.timestamp_ns(),
        )

        try:
            kwargs = zb_order_params(order, position)
            await self._account_api.new_order(**kwargs)
            # await self._ws_user_api.new_order(**kwargs)
        except ZbError as ex:
            self.generate_order_rejected(
                strategy_id=command.strategy_id,
                instrument_id=command.instrument_id,
                client_order_id=order.client_order_id,
                reason=ex.message,  # type: ignore  # TODO(cs): Improve errors
                ts_event=self._clock.timestamp_ns(),  # TODO(cs): Parse from response
            )
        except Exception as ex:
            self._log.exception(ex)

    async def _submit_order_list(self, order_list: OrderList) -> None:
        batch_params = []
        for order in order_list.orders:
            if order.contingency_ids:  # TODO(cs): Implement
                self._log.warning(f"Cannot yet handle contingency orders, {order}.")
            params = zb_order_params(order)
            params["orderCode"] = params.pop("client_order_id")
            batch_params.append(params)

        response = await self._account_api.new_batch_order(orders=batch_params)
        self._log.debug(f"Submit batch order response {response}", LogColor.YELLOW)

    async def _cancel_order(self, order: CancelOrder) -> None:
        self._log.debug(f"Canceling order {order.client_order_id.value}.")

        self.generate_order_pending_cancel(
            strategy_id=order.strategy_id,
            instrument_id=order.instrument_id,
            client_order_id=order.client_order_id,
            venue_order_id=order.venue_order_id,
            ts_event=self._clock.timestamp_ns(),
        )

        try:
            await self._account_api.cancel_order(
                # await self._ws_user_api.cancel_order(
                symbol=order.instrument_id.symbol.value,
                client_order_id=order.client_order_id.value,
            )
        except ZbError as ex:
            self.generate_order_cancel_rejected(
                strategy_id=order.strategy_id,
                instrument_id=order.instrument_id,
                client_order_id=order.client_order_id,
                venue_order_id=order.venue_order_id,
                reason=ex.message,  # type: ignore  # TODO(cs): Improve errors
                ts_event=self._clock.timestamp_ns(),  # TODO(cs): Parse from response
            )
        except Exception as ex:
            self._log.exception(ex)

    async def _cancel_all_order(self, command: CancelAllOrders) -> None:
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
            # await self._ws_user_api.cancel_open_orders(command.instrument_id.symbol.value)
            await self._account_api.cancel_open_orders(command.instrument_id.symbol.value)
        except ZbError as ex:
            self._log.error(ex)  # type: ignore  # TODO(cs): Improve errors
        except Exception as ex:
            self._log.exception(ex)

    # -- RECONCILIATION ----------------------------------------------------------------------------

    async def generate_order_status_report(self, order: Order) -> OrderStatusReport:
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
        raise NotImplementedError("method must be implemented in the subclass")  # pragma: no cover

    async def generate_exec_reports(
        self,
        venue_order_id: VenueOrderId,
        symbol: Symbol,
        since: datetime = None,
    ) -> List[ExecutionReport]:
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
        raise NotImplementedError("method must be implemented in the subclass")  # pragma: no cover
