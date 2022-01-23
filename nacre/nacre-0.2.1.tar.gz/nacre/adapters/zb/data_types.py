from decimal import Decimal
from typing import Any, Dict

from nautilus_trader.model.data.bar import Bar
from nautilus_trader.model.data.bar import BarType
from nautilus_trader.model.data.ticker import Ticker
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


class ZbTicker(Ticker):
    def __init__(
        self,
        instrument_id: InstrumentId,
        price_change: Decimal,
        last_price: Decimal,
        open_price: Decimal,
        high_price: Decimal,
        low_price: Decimal,
        volume: Decimal,
        last_id: int,
        ts_event: int,
        ts_init: int,
    ):
        """
        Initialize a new instance of the ``ZbTicker`` class.

        Parameters
        ----------
        instrument_id : InstrumentId
            The instrument ID.
        price_change : Decimal
            The price change.
        last_price : Decimal
            The last price.
        open_price : Decimal
            The open price.
        high_price : Decimal
            The high price.
        low_price : Decimal
            The low price.
        volume : Decimal
            The volume.
        last_id : int
            The last trade time
        ts_event : int64
            The UNIX timestamp (nanoseconds) when the ticker event occurred.
        ts_init : int64
            The UNIX timestamp (nanoseconds) when the object was initialized.

        """
        super().__init__(
            instrument_id=instrument_id,
            ts_event=ts_event,
            ts_init=ts_init,
        )

        self.price_change = price_change
        self.last_price = last_price
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.volume = volume
        self.last_id = last_id

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"instrument_id={self.instrument_id.value}, "
            f"price_change={self.price_change}, "
            f"last_price={self.last_price}, "
            f"open_price={self.open_price}, "
            f"high_price={self.high_price}, "
            f"low_price={self.low_price}, "
            f"volume={self.volume}, "
            f"last_id={self.last_id}, "
            f"ts_event={self.ts_event},"
            f"ts_init={self.ts_init})"
        )

    @staticmethod
    def from_dict(values: Dict[str, Any]) -> "ZbTicker":
        """
        Return a `Zb` ticker parsed from the given values.

        Parameters
        ----------
        values : dict[str, Any]
            The values for initialization.

        Returns
        -------
        ZbTicker

        """
        return ZbTicker(
            instrument_id=InstrumentId.from_str(values["instrument_id"]),
            price_change=Decimal(values["price_change"]),
            last_price=Decimal(values["last_price"]),
            open_price=Decimal(values["open_price"]),
            high_price=Decimal(values["high_price"]),
            low_price=Decimal(values["low_price"]),
            volume=Decimal(values["volume"]),
            last_id=values["last_id"],
            ts_event=values["ts_event"],
            ts_init=values["ts_init"],
        )

    @staticmethod
    def to_dict(obj: "ZbTicker") -> Dict[str, Any]:
        """
        Return a dictionary representation of this object.

        Returns
        -------
        dict[str, Any]

        """
        return {
            "type": type(obj).__name__,
            "instrument_id": obj.instrument_id.value,
            "price_change": str(obj.price_change),
            "last_price": str(obj.last_price),
            "open_price": str(obj.open_price),
            "high_price": str(obj.high_price),
            "low_price": str(obj.low_price),
            "volume": str(obj.volume),
            "last_id": obj.last_id,
            "ts_event": obj.ts_event,
            "ts_init": obj.ts_init,
        }


class ZbBar(Bar):
    def __init__(
        self,
        bar_type: BarType,
        open: Price,
        high: Price,
        low: Price,
        close: Price,
        volume: Quantity,
        ts_event: int,
        ts_init: int,
    ):
        """
        Initialize a new instance of the ``ZbBar`` class.

        Parameters
        ----------
        bar_type : BarType
            The bar type for this bar.
        open : Price
            The bars open price.
        high : Price
            The bars high price.
        low : Price
            The bars low price.
        close : Price
            The bars close price.
        volume : Quantity
            The bars volume.
        ts_event : int64
            The UNIX timestamp (nanoseconds) when the data event occurred.
        ts_init: int64
            The UNIX timestamp (nanoseconds) when the data object was initialized.

        """
        super().__init__(
            bar_type=bar_type,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume,
            ts_event=ts_event,
            ts_init=ts_init,
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"bar_type={self.type}, "
            f"open={self.open}, "
            f"high={self.high}, "
            f"low={self.low}, "
            f"close={self.close}, "
            f"volume={self.volume}, "
            f"ts_event={self.ts_event},"
            f"ts_init={self.ts_init})"
        )

    @staticmethod
    def from_dict(values: Dict[str, Any]) -> "ZbBar":
        """
        Return a `Zb` bar parsed from the given values.

        Parameters
        ----------
        values : dict[str, Any]
            The values for initialization.

        Returns
        -------
        ZbBar

        """
        return ZbBar(
            bar_type=BarType.from_str(values["bar_type"]),
            open=Price.from_str(values["open"]),
            high=Price.from_str(values["high"]),
            low=Price.from_str(values["low"]),
            close=Price.from_str(values["close"]),
            volume=Quantity.from_str(values["volume"]),
            ts_event=values["ts_event"],
            ts_init=values["ts_init"],
        )

    @staticmethod
    def to_dict(obj: "ZbBar") -> Dict[str, Any]:
        """
        Return a dictionary representation of this object.

        Returns
        -------
        dict[str, Any]

        """
        return {
            "type": type(obj).__name__,
            "bar_type": str(obj.type),
            "open": str(obj.open),
            "high": str(obj.high),
            "low": str(obj.low),
            "close": str(obj.close),
            "volume": str(obj.volume),
            "ts_event": obj.ts_event,
            "ts_init": obj.ts_init,
        }
