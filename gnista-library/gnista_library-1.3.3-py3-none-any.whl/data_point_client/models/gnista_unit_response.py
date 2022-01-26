from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="GnistaUnitResponse")


@attr.s(auto_attribs=True)
class GnistaUnitResponse:
    """ """

    name: Union[Unset, None, str] = UNSET
    physical_quantity: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        physical_quantity = self.physical_quantity

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if physical_quantity is not UNSET:
            field_dict["physicalQuantity"] = physical_quantity

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        physical_quantity = d.pop("physicalQuantity", UNSET)

        gnista_unit_response = cls(
            name=name,
            physical_quantity=physical_quantity,
        )

        return gnista_unit_response
