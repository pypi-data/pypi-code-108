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

from infima_client.core.models.prepayment.prepayment_actual import (
    PrepaymentPrepaymentActual,
)
from infima_client.core.types import UNSET, Unset

T = TypeVar("T", bound="PrepaymentPrepaymentActuals")


@define(auto_attribs=True)
class PrepaymentPrepaymentActuals:
    """
    Attributes:
        symbol (Union[Unset, str]):
        values (Union[Unset, List[PrepaymentPrepaymentActual]]):
    """

    symbol: Union[Unset, str] = UNSET
    values: Union[Unset, List[PrepaymentPrepaymentActual]] = UNSET
    additional_properties: Dict[str, Any] = field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        symbol = self.symbol
        values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.values, Unset):
            values = []
            for values_item_data in self.values:
                values_item = values_item_data.to_dict()

                values.append(values_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if symbol is not UNSET:
            field_dict["symbol"] = symbol
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        symbol = d.pop("symbol", UNSET)

        values = []
        _values = d.pop("values", UNSET)
        for values_item_data in _values or []:
            values_item = PrepaymentPrepaymentActual.from_dict(values_item_data)

            values.append(values_item)

        prepayment_prepayment_actuals = cls(
            symbol=symbol,
            values=values,
        )

        prepayment_prepayment_actuals.additional_properties = d
        return prepayment_prepayment_actuals

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
