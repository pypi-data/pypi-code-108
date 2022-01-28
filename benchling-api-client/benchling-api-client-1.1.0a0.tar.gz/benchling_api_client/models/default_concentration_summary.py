from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="DefaultConcentrationSummary")


@attr.s(auto_attribs=True, repr=False)
class DefaultConcentrationSummary:
    """  """

    _units: Union[Unset, str] = UNSET
    _value: Union[Unset, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("units={}".format(repr(self._units)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DefaultConcentrationSummary({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        units = self._units
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

        def get_units() -> Union[Unset, str]:
            units = d.pop("units")
            return units

        units = get_units() if "units" in d else cast(Union[Unset, str], UNSET)

        def get_value() -> Union[Unset, float]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Union[Unset, float], UNSET)

        default_concentration_summary = cls(
            units=units,
            value=value,
        )

        default_concentration_summary.additional_properties = d
        return default_concentration_summary

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
    def units(self) -> str:
        """ Units of measurement. """
        if isinstance(self._units, Unset):
            raise NotPresentError(self, "units")
        return self._units

    @units.setter
    def units(self, value: str) -> None:
        self._units = value

    @units.deleter
    def units(self) -> None:
        self._units = UNSET

    @property
    def value(self) -> float:
        """ Amount of measurement. """
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    @value.deleter
    def value(self) -> None:
        self._value = UNSET
