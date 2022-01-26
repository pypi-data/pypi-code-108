from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="Measurement")


@attr.s(auto_attribs=True, repr=False)
class Measurement:
    """  """

    _units: Optional[str]
    _value: Optional[float]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("units={}".format(repr(self._units)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Measurement({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        units = self._units
        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "units": units,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_units() -> Optional[str]:
            units = d.pop("units")
            return units

        units = get_units() if "units" in d else cast(Optional[str], UNSET)

        def get_value() -> Optional[float]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Optional[float], UNSET)

        measurement = cls(
            units=units,
            value=value,
        )

        measurement.additional_properties = d
        return measurement

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
    def units(self) -> Optional[str]:
        if isinstance(self._units, Unset):
            raise NotPresentError(self, "units")
        return self._units

    @units.setter
    def units(self, value: Optional[str]) -> None:
        self._units = value

    @property
    def value(self) -> Optional[float]:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: Optional[float]) -> None:
        self._value = value
