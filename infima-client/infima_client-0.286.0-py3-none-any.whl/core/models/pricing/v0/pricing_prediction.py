from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from attr import define, field

from infima_client.core.models.core.date import CoreDate
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PricingV0PricingPrediction")


@define(auto_attribs=True)
class PricingV0PricingPrediction:
    """
    Attributes:
        as_of (Union[Unset, CoreDate]):
        payup (Union[Unset, float]):
        price (Union[Unset, float]):
        symbol (Union[Unset, str]):
    """

    as_of: Union[Unset, CoreDate] = UNSET
    payup: Union[Unset, float] = UNSET
    price: Union[Unset, float] = UNSET
    symbol: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        as_of: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.as_of, Unset):
            as_of = self.as_of.to_dict()

        payup = self.payup
        price = self.price
        symbol = self.symbol

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if as_of is not UNSET:
            field_dict["asOf"] = as_of
        if payup is not UNSET:
            field_dict["payup"] = payup
        if price is not UNSET:
            field_dict["price"] = price
        if symbol is not UNSET:
            field_dict["symbol"] = symbol

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _as_of = d.pop("asOf", UNSET)
        as_of: Union[Unset, CoreDate]
        if isinstance(_as_of, Unset):
            as_of = UNSET
        else:
            as_of = CoreDate.from_dict(_as_of)

        payup = d.pop("payup", UNSET)

        price = d.pop("price", UNSET)

        symbol = d.pop("symbol", UNSET)

        pricing_v0_pricing_prediction = cls(
            as_of=as_of,
            payup=payup,
            price=price,
            symbol=symbol,
        )

        pricing_v0_pricing_prediction.additional_properties = d
        return pricing_v0_pricing_prediction

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
