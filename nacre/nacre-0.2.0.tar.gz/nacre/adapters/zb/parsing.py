from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from nautilus_trader.core.datetime import secs_to_nanos
from nautilus_trader.model.c_enums.time_in_force import TimeInForce
from nautilus_trader.model.data.bar import BarSpecification
from nautilus_trader.model.data.bar import BarType
from nautilus_trader.model.data.base import DataType
from nautilus_trader.model.data.base import GenericData
from nautilus_trader.model.data.tick import TradeTick
from nautilus_trader.model.enums import AggregationSource
from nautilus_trader.model.enums import AggressorSide
from nautilus_trader.model.enums import BarAggregation
from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.enums import PositionSide
from nautilus_trader.model.enums import PriceType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import PositionId
from nautilus_trader.model.objects import AccountBalance
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orderbook.data import Order
from nautilus_trader.model.orderbook.data import OrderBookDelta
from nautilus_trader.model.orderbook.data import OrderBookDeltas
from nautilus_trader.model.orderbook.data import OrderBookSnapshot
from nautilus_trader.model.orders.limit import LimitOrder
from nautilus_trader.model.orders.market import MarketOrder
from nautilus_trader.model.position import Position

from nacre.adapters.zb.data_types import ZbBar
from nacre.adapters.zb.data_types import ZbTicker
from nacre.model.data.tick import MarkTick
from nacre.model.report_position import ReportedPosition
from nacre.model.report_position import SideWithMode
from nacre.model.report_position import WalletBalance


def parse_mark_price(instrument_id: InstrumentId, price: str, ts_init: int) -> MarkTick:
    tick = MarkTick(
        instrument_id=instrument_id,
        price=Price.from_str(price),
        ts_event=ts_init,
        ts_init=ts_init,
    )
    return GenericData(
        data_type=DataType(MarkTick, metadata={"instrument_id": instrument_id}),
        data=tick,
    )


def parse_book_snapshot_ws(
    instrument_id: InstrumentId, msg: Dict, ts_init: int
) -> OrderBookSnapshot:
    ts_event: int = ts_init

    return OrderBookSnapshot(
        instrument_id=instrument_id,
        book_type=BookType.L2_MBP,
        bids=[[float(o[0]), float(o[1])] for o in msg.get("bids", [])],
        asks=[[float(o[0]), float(o[1])] for o in msg.get("asks", [])],
        ts_event=ts_event,
        ts_init=ts_init,
        update_id=int(msg.get("time")),
    )


def parse_diff_depth_stream_ws(
    instrument_id: InstrumentId, msg: Dict, ts_init: int
) -> OrderBookDeltas:
    ts_event: int = ts_init
    update_id: int = int(msg["time"])

    bid_deltas = [
        parse_book_delta_ws(instrument_id, OrderSide.BUY, d, ts_event, ts_init, update_id)
        for d in msg.get("bids", [])
    ]
    ask_deltas = [
        parse_book_delta_ws(instrument_id, OrderSide.SELL, d, ts_event, ts_init, update_id)
        for d in msg.get("asks", [])
    ]

    return OrderBookDeltas(
        instrument_id=instrument_id,
        book_type=BookType.L2_MBP,
        deltas=bid_deltas + ask_deltas,
        ts_event=ts_event,
        ts_init=ts_init,
        update_id=update_id,
    )


def parse_book_delta_ws(
    instrument_id: InstrumentId,
    side: OrderSide,
    delta: Tuple[str, str],
    ts_event: int,
    ts_init: int,
    update_id: int,
) -> OrderBookDelta:
    price = float(delta[0])
    size = float(delta[1])

    order = Order(
        price=price,
        size=size,
        side=side,
    )

    return OrderBookDelta(
        instrument_id=instrument_id,
        book_type=BookType.L2_MBP,
        action=BookAction.UPDATE if size > 0.0 else BookAction.DELETE,
        order=order,
        ts_event=ts_event,
        ts_init=ts_init,
        update_id=update_id,
    )


def parse_ticker_ws(instrument_id: InstrumentId, msg: List, ts_init: int) -> ZbTicker:
    return ZbTicker(
        instrument_id=instrument_id,
        price_change=Decimal(msg[5]),
        last_price=Decimal(msg[3]),
        open_price=Decimal(msg[0]),
        high_price=Decimal(msg[1]),
        low_price=Decimal(msg[2]),
        volume=Decimal(msg[4]),
        last_id=msg[6],
        # ts_event=secs_to_nanos(float(msg[6])-1),  # zb time not accurate
        ts_event=ts_init,
        ts_init=ts_init,
    )


def parse_trade_tick(instrument_id: InstrumentId, msg: List, ts_init: int) -> TradeTick:
    return TradeTick(
        instrument_id=instrument_id,
        price=Price.from_str(str(msg[0])),
        size=Quantity.from_str(str(msg[1])),
        aggressor_side=AggressorSide.SELL if msg[2] == -1 else AggressorSide.BUY,
        match_id=str(msg[3]),  # zb future does not provide match id
        ts_event=secs_to_nanos(float(msg[3])),
        ts_init=ts_init,
    )


def parse_trade_tick_ws(instrument_id: InstrumentId, msg: List, ts_init: int) -> TradeTick:
    return TradeTick(
        instrument_id=instrument_id,
        price=Price.from_str(str(msg[0])),
        size=Quantity.from_str(str(msg[1])),
        aggressor_side=AggressorSide.SELL if msg[2] == -1 else AggressorSide.BUY,
        match_id=str(msg[3]),
        # ts_event=secs_to_nanos(float(msg[3])),  # zb time not accurate
        ts_event=ts_init,
        ts_init=ts_init,
    )


def parse_bar(bar_type: BarType, values: List, ts_init: int) -> ZbBar:
    return ZbBar(
        bar_type=bar_type,
        open=Price.from_str(str(values[0])),
        high=Price.from_str(str(values[1])),
        low=Price.from_str(str(values[2])),
        close=Price.from_str(str(values[3])),
        volume=Quantity.from_str(str(values[4])),
        ts_event=secs_to_nanos(float(values[5])),
        ts_init=ts_init,
    )


def parse_bar_ws(
    instrument_id: InstrumentId,
    kline: List,
    chan_type: str,
    ts_init: int,
) -> ZbBar:

    _, _, interval = chan_type.partition("_")
    resolution = interval[-1]
    if resolution == "M":
        aggregation = BarAggregation.MINUTE
    elif resolution == "H":
        aggregation = BarAggregation.HOUR
    elif resolution == "D":
        aggregation = BarAggregation.DAY
    else:  # pragma: no cover (design-time error)
        raise RuntimeError(f"unsupported time aggregation resolution, was {resolution}")

    bar_spec = BarSpecification(
        step=int(interval[:-1]),
        aggregation=aggregation,
        price_type=PriceType.LAST,
    )

    bar_type = BarType(
        instrument_id=instrument_id,
        bar_spec=bar_spec,
        aggregation_source=AggregationSource.EXTERNAL,
    )

    return ZbBar(
        bar_type=bar_type,
        open=Price.from_str(str(kline[0])),
        high=Price.from_str(str(kline[1])),
        low=Price.from_str(str(kline[2])),
        close=Price.from_str(str(kline[3])),
        volume=Quantity.from_str(str(kline[4])),
        ts_event=secs_to_nanos(float(kline[5])),
        ts_init=ts_init,
    )


# Account parsing


def parse_positions(positions: List[Dict[str, Any]]) -> List[Dict]:
    results = []
    for po in positions:
        # Zb future currently only support dual side
        # if po["positionsMode"] == 1:
        #     position_side = "BOTH"
        if po["side"] == 1:
            position_side = "LONG"
        elif po["side"] == 0:
            position_side = "SHORT"
        else:
            raise ValueError(f"not recognized side {po['side']}")

        notional = float(po["nominalValue"])
        position = dict(
            id=po["id"],
            sym=po["marketName"],
            qty=float(po["amount"]),
            notional=notional if po["side"] == 1 else -1 * notional,
            ep=float(po["avgPrice"]),  # entry price
            lp=float(po["liquidatePrice"]),  # liquidate Price
            upnl=float(po["unrealizedPnl"]),  # unrealized pnl
            mt="isolated" if po["marginMode"] == 1 else "cross",  # margin type
            ps=position_side,  # position side
            lg=int(po["leverage"]),
            # im=float(po["initialMargin"]),  # initial margin
            mm=float(po["maintainMargin"]),  # maintenance margin
            mr=float(po["marginRate"]),  # margin rate
            # pim=float(po["positionInitialMargin"]),  # position Initial Margin
            m=float(po["margin"]),  # margin
            mb=float(po["marginBalance"]),  # margin balance
        )
        results.append(position)
    return results


def parse_account_balances_raw(provider, raw_balances: List) -> List[AccountBalance]:
    balances = []
    for b in raw_balances:
        currency = provider.currency(b["currencyName"].upper())
        if not currency:
            continue

        locked = Money(b["freezeAmount"], currency)
        free = Money(b["amount"], currency)
        total = Money(locked + free, currency)

        balances.append(
            AccountBalance(
                currency=currency,
                total=total,
                locked=locked,
                free=free,
            )
        )
    return balances


# ZB future use USDT as default
def parse_reported_wallet_balance(provider, raw: Dict) -> List[WalletBalance]:
    currency = provider.currency(raw["unit"].upper())

    total = Decimal(raw["accountBalance"])
    margin = Decimal(raw["allMargin"])
    maint_margin = Decimal(raw["freeze"])

    wb = WalletBalance(
        asset=currency,
        total=total,
        margin=margin,
        maint_margin=maint_margin,
    )
    return [wb]


def parse_reported_position(provider, raw_positions: List) -> List[ReportedPosition]:
    positions = []
    for po in raw_positions:
        symbol: str = po["marketName"]
        instrument_id = provider.find_instrument_id_by_local_symbol(symbol)

        # Zb currently only support Hedge mode
        # zb_position_mode = po["positionsMode"]
        # if zb_position_mode == 1:  # One way / Both
        #     side = SideWithMode.BOTH
        # else:  # zb_position_mode == 2:  # Hedge Mode
        if po["side"] == 1:
            side = SideWithMode.LONG
        elif po["side"] == 0:
            side = SideWithMode.SHORT
        else:
            raise ValueError(f"not recognized side {po['side']}")

        sign = 1 if po["side"] > 0 else -1
        net_qty = sign * Decimal(po["amount"])

        position = ReportedPosition(
            instrument_id=instrument_id,
            position_id=PositionId(po["id"]),
            side=side,
            net_qty=net_qty,
            multiplier=int(po["leverage"]),
            avg_px_open=Decimal(po["avgPrice"]),
            unrealized_pnl=Decimal(po["unrealizedPnl"]),
            margin=Decimal(po["marginBalance"]),
            maint_margin=Decimal(po["maintainMargin"]),
            liquidity_px=Decimal(po["liquidatePrice"]),
        )

        positions.append(position)
    return positions


def parse_zb_position_side(side: int) -> PositionSide:
    if side == 3 or side == 1:
        return "LONG"
    else:
        return "SHORT"


def parse_zb_order_side(type: int) -> OrderSide:
    if type == 1:
        return OrderSide.BUY
    elif type == -1:
        return OrderSide.SELL
    else:
        raise ValueError(f"Unknown order side: {type}")


def parse_zb_order_type(action: int) -> OrderType:
    if action == 11 or action == 31 or action == 51:
        return OrderType.MARKET
    else:  # TODO: parse other STOP LIMIT
        return OrderType.LIMIT


def zb_order_side(order: Order, position: Optional[Position] = None) -> int:
    if order.side == OrderSide.BUY:
        if not position:
            return 1
        return 1 if position.side == PositionSide.LONG else 4
    else:  # order.side == OrderSide.SELL
        if not position:
            return 2
        return 3 if position.side == PositionSide.LONG else 2


def zb_order_params(order: Order, position: Optional[Position] = None) -> Dict[str, Any]:
    if order.type == OrderType.MARKET:
        return dict(
            symbol=order.instrument_id.symbol.value,
            side=zb_order_side(order, position),
            amount=order.quantity.as_double(),
            action=zb_order_action_market(order),
            client_order_id=order.client_order_id.value,
        )
    elif order.type == OrderType.LIMIT:
        return dict(
            symbol=order.instrument_id.symbol.value,
            side=zb_order_side(order, position),
            amount=order.quantity.as_double(),
            action=zb_order_action_limit(order),
            price=order.price.as_double(),
            client_order_id=order.client_order_id.value,
        )
    else:
        raise ValueError(f"Unsupported order type for zb: {order.type}")


def zb_order_action_market(order: MarketOrder) -> int:
    if order.time_in_force == TimeInForce.GTC:
        return 11
    elif order.time_in_force == TimeInForce.IOC:
        return 31
    elif order.time_in_force == TimeInForce.FOK:
        return 51
    else:
        raise ValueError(f"Unsupported time_in_force market for zb: {order.time_in_force}")


def zb_order_action_limit(order: LimitOrder) -> int:
    if order.is_post_only:
        return 4
    elif order.time_in_force == TimeInForce.GTC:
        return 1
    elif order.time_in_force == TimeInForce.IOC:
        return 3
    elif order.time_in_force == TimeInForce.FOK:
        return 5
    else:
        raise ValueError(f"Unsupported time_in_force limit for zb: {order.time_in_force}")
