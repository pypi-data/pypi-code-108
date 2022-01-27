from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="OHLCPointSchema")


@attr.s(auto_attribs=True)
class OHLCPointSchema:
    """  """

    open_: float
    close: float
    high: float
    low: float
    date: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        open_ = self.open_
        close = self.close
        high = self.high
        low = self.low
        date = self.date

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "open": open_,
                "close": close,
                "high": high,
                "low": low,
                "date": date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        open_ = d.pop("open")

        close = d.pop("close")

        high = d.pop("high")

        low = d.pop("low")

        date = d.pop("date")

        ohlc_point_schema = cls(
            open_=open_,
            close=close,
            high=high,
            low=low,
            date=date,
        )

        ohlc_point_schema.additional_properties = d
        return ohlc_point_schema

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
