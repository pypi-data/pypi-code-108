from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomField")


@attr.s(auto_attribs=True, repr=False)
class CustomField:
    """  """

    _value: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("value={}".format(repr(self._value)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CustomField({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_value() -> Union[Unset, str]:
            value = d.pop("value")
            return value

        value = get_value() if "value" in d else cast(Union[Unset, str], UNSET)

        custom_field = cls(
            value=value,
        )

        custom_field.additional_properties = d
        return custom_field

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
    def value(self) -> str:
        if isinstance(self._value, Unset):
            raise NotPresentError(self, "value")
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @value.deleter
    def value(self) -> None:
        self._value = UNSET
