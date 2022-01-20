from decimal import Decimal
from typing import Any, Dict, List, Tuple

# from nautilus_trader.core.datetime import millis_to_nanos
from nautilus_trader.model.currency import Currency
from nautilus_trader.model.data.base import DataType
from nautilus_trader.model.data.base import GenericData
from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.enums import OrderTypeParser
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.identifiers import PositionId
from nautilus_trader.model.objects import AccountBalance
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.orderbook.data import Order as BookOrder
from nautilus_trader.model.orderbook.data import OrderBookDelta
from nautilus_trader.model.orderbook.data import OrderBookDeltas
from nautilus_trader.model.orders.base import Order

from nacre.model.data.tick import MarkTick
from nacre.model.report_position import ReportedPosition
from nacre.model.report_position import SideWithModeParser
from nacre.model.report_position import WalletBalance


def parse_diff_depth_stream_ws(
    instrument_id: InstrumentId, msg: Dict, ts_init: int
) -> OrderBookDeltas:
    # ts_event: int = millis_to_nanos(msg["E"])
    ts_event = ts_init
    update_id: int = msg["U"]

    bid_deltas = [
        parse_book_delta_ws(instrument_id, OrderSide.BUY, d, ts_event, ts_init, update_id)
        for d in msg.get("b")
    ]
    ask_deltas = [
        parse_book_delta_ws(instrument_id, OrderSide.SELL, d, ts_event, ts_init, update_id)
        for d in msg.get("a")
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

    order = BookOrder(
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


def parse_future_order_type(order_type: str) -> OrderType:
    if order_type == "STOP":
        return OrderType.STOP_LIMIT
    elif order_type == "TAKE_PROFIT":
        return OrderType.STOP_LIMIT
    elif order_type == "TAKE_PROFIT_MARKET":
        return OrderType.STOP_MARKET
    else:
        return OrderTypeParser.from_str_py(order_type)


def binance_future_order_type(order: Order, market_price: Decimal = None) -> str:  # noqa
    if order.type == OrderType.LIMIT:
        return "LIMIT"
    elif order.type == OrderType.STOP_MARKET:
        if order.side == OrderSide.BUY:
            if order.price > market_price:
                return "TAKE_PROFIT_MARKET"
            else:
                return "STOP_MARKET"
        else:  # OrderSide.SELL
            if order.price < market_price:
                return "TAKE_PROFIT_MARKET"
            else:
                return "STOP_MARKET"
    elif order.type == OrderType.STOP_LIMIT:
        if order.side == OrderSide.BUY:
            if order.trigger > market_price:
                return "TAKE_PROFIT"
            else:
                return "STOP"
        else:  # OrderSide.SELL
            if order.trigger < market_price:
                return "TAKE_PROFIT"
            else:
                return "STOP"
    elif order.type == OrderType.MARKET:
        return "MARKET"
    else:  # pragma: no cover (design-time error)
        raise RuntimeError("invalid order type")


def parse_reported_position(
    provider,
    raw_positions: List[Dict[str, Any]],
) -> List[ReportedPosition]:
    positions = []
    for po in raw_positions:
        symbol: str = po["symbol"]
        try:
            instrument_id = provider.find_instrument_id_by_local_symbol(symbol)
        except KeyError:
            # self._log.debug(f"Unknown instrument {symbol}")
            continue

        net_qty = Decimal(po["positionAmt"])
        # init_margin = Decimal(po["initialMargin"])
        maint_margin = Decimal(po["maintMargin"])

        position = ReportedPosition(
            instrument_id=instrument_id,
            side=SideWithModeParser.from_str_py(po["positionSide"]),
            position_id=PositionId(f"{symbol}-{po['positionSide']}"),
            net_qty=net_qty,
            multiplier=int(po["leverage"]),
            avg_px_open=Decimal(po["entryPrice"]),
            unrealized_pnl=Decimal(po["unrealizedProfit"]),
            maint_margin=maint_margin,
        )

        positions.append(position)
    return positions


def parse_reported_wallet_balance(
    provider,
    raw_balances: List[Dict[str, Any]],
) -> List[WalletBalance]:
    balances = []
    for b in raw_balances:
        currency = provider.currency(b["asset"])
        if not currency:
            # self._log.debug(f"Unknown currency: {b['asset']}")
            continue

        total = Decimal(b["walletBalance"])
        margin = Decimal(b["marginBalance"])
        maint_margin = Decimal(b["maintMargin"])

        # ignore empty asset
        if total == 0:
            continue

        wb = WalletBalance(
            asset=currency,
            total=total,
            margin=margin,
            maint_margin=maint_margin,
        )
        balances.append(wb)
    return balances


def parse_balances(
    provider,
    raw_balances: List[Dict[str, str]],
    asset_key: str,
    free_key: str,
    locked_key: str,
) -> List[AccountBalance]:
    parsed_balances: Dict[Currency, Tuple[Decimal, Decimal, Decimal]] = {}
    for b in raw_balances:
        currency = provider.currency(b[asset_key])
        if not currency:
            # self._log.debug(f"Unknown currency: {b[asset_key]}")
            continue

        free = Money(b[free_key], currency)
        locked = Money(b.get(locked_key, 0), currency)
        total = Money(free + locked, currency)

        # Ignore empty asset
        if Decimal(b[free_key]) + Decimal(b.get(locked_key, 0)) == 0:
            continue

        parsed_balances[currency] = (total, locked, free)

    balances: List[AccountBalance] = [
        AccountBalance(
            currency=currency,
            total=values[0],
            locked=values[1],
            free=values[2],
        )
        for currency, values in parsed_balances.items()
    ]

    return balances


def parse_positions(raw_positions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    info = []
    for po in raw_positions:
        if float(po["notional"]) == 0:
            continue

        position = dict(
            sym=po["symbol"],
            qty=float(po["positionAmt"]),
            notional=float(po["notional"]),
            ep=float(po["entryPrice"]),  # entry price
            upnl=float(po["unrealizedProfit"]),  # unrealized pnl
            mt="isolated" if po["isolated"] else "cross",  # margin type
            ps=po["positionSide"],  # position side
            lg=int(po["leverage"]),
            im=float(po["initialMargin"]),  # initial margin
            mm=float(po["maintMargin"]),  # maintenance margin
            pim=float(po["positionInitialMargin"]),  # position Initial Margin
        )
        info.append(position)
    return info


def parse_reported_wallet_balance_ws(
    provider,
    raw_balances: List[Dict[str, Any]],
) -> List[WalletBalance]:
    balances = []
    for b in raw_balances:
        currency = provider.currency(b["a"])
        if not currency:
            # self._log.warning(f"Unknown currency: {b['a']}")
            continue

        total = Decimal(b["wb"])
        balances.append(
            WalletBalance(
                asset=currency,
                total=total,
            )
        )

    return balances


def parse_reported_positions_ws(
    provider, raw_positions: List[Dict[str, Any]]
) -> List[ReportedPosition]:
    positions = []
    for po in raw_positions:
        symbol: str = po["s"]
        instrument_id = provider.find_instrument_id_by_local_symbol(symbol)

        net_qty = Decimal(po["pa"])

        kwargs = dict(
            instrument_id=instrument_id,
            side=SideWithModeParser.from_str_py(po["ps"]),
            position_id=PositionId(f"{symbol}-{po['ps']}"),
            net_qty=net_qty,
            avg_px_open=Decimal(po["ep"]),
            unrealized_pnl=Decimal(po["up"]),
        )
        # for isolated position
        if po["mt"] == "isolated":
            kwargs["margin"] = Decimal(po["iw"])

        position = ReportedPosition(**kwargs)
        positions.append(position)
    return positions
