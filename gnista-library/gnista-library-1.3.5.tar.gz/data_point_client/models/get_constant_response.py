from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.gnista_unit_response import GnistaUnitResponse
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetConstantResponse")


@attr.s(auto_attribs=True)
class GetConstantResponse:
    """ """

    discriminator: str
    value: Union[Unset, float] = UNSET
    unit: Union[Unset, None, GnistaUnitResponse] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        value = self.value
        unit: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.unit, Unset):
            unit = self.unit.to_dict() if self.unit else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        value = d.pop("value", UNSET)

        _unit = d.pop("unit", UNSET)
        unit: Union[Unset, None, GnistaUnitResponse]
        if _unit is None:
            unit = None
        elif isinstance(_unit, Unset):
            unit = UNSET
        else:
            unit = GnistaUnitResponse.from_dict(_unit)

        get_constant_response = cls(
            discriminator=discriminator,
            value=value,
            unit=unit,
        )

        get_constant_response.additional_properties = d
        return get_constant_response

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
