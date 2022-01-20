from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_quantity_units import ContainerQuantityUnits
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerQuantity")


@attr.s(auto_attribs=True, repr=False)
class ContainerQuantity:
    """ Quantity of a container, well, or transfer. Supports mass, volume, and other quantities. """

    _units: Union[Unset, None, ContainerQuantityUnits] = UNSET
    _value: Union[Unset, None, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("units={}".format(repr(self._units)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerQuantity({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        units: Union[Unset, None, int] = UNSET
        if not isinstance(self._units, Unset):
            units = self._units.value if self._units else None

        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if units is not UNSET:
            field_dict["units"] = units
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_units() -> Union[Unset, None, ContainerQuantityUnits]:
            units = None
            _units = d.pop("units")
            if _units is not None and _units is not UNSET:
                try:
                    units = ContainerQuantityUnits(_units)
                except ValueError:
                    units = ContainerQuantityUnits.of_unknown(_units)

            return units

        units = get_units() if "units" in d else cast(Union[Unset, None, ContainerQuantityUnits], UNSET)

        def get_value() -> Union[Unset, None, float]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Union[Unset, None, float], UNSET)

        container_quantity = cls(
            units=units,
            value=value,
        )

        container_quantity.additional_properties = d
        return container_quantity

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def units(self) -> Optional[ContainerQuantityUnits]:
        if isinstance(self._units, Unset):
            raise NotPresentError(self, "units")
        return self._units

    @units.setter
    def units(self, value: Optional[ContainerQuantityUnits]) -> None:
        self._units = value

    @units.deleter
    def units(self) -> None:
        self._units = UNSET

    @property
    def value(self) -> Optional[float]:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: Optional[float]) -> None:
        self._value = value

    @value.deleter
    def value(self) -> None:
        self._value = UNSET
