from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Quantity")


@attr.s(auto_attribs=True)
class Quantity:
    """ """

    amount: str
    unit: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        amount = self.amount
        unit = self.unit

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "amount": amount,
            }
        )
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        amount = d.pop("amount")

        unit = d.pop("unit", UNSET)

        quantity = cls(
            amount=amount,
            unit=unit,
        )

        return quantity
