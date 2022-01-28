from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownOptionsArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class DropdownOptionsArchivalChange:
    """IDs of all items that were archived or unarchived."""

    _dropdown_option_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dropdown_option_ids={}".format(repr(self._dropdown_option_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DropdownOptionsArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dropdown_option_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dropdown_option_ids, Unset):
            dropdown_option_ids = self._dropdown_option_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dropdown_option_ids is not UNSET:
            field_dict["dropdownOptionIds"] = dropdown_option_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dropdown_option_ids() -> Union[Unset, List[str]]:
            dropdown_option_ids = cast(List[str], d.pop("dropdownOptionIds"))

            return dropdown_option_ids

        dropdown_option_ids = (
            get_dropdown_option_ids() if "dropdownOptionIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        dropdown_options_archival_change = cls(
            dropdown_option_ids=dropdown_option_ids,
        )

        dropdown_options_archival_change.additional_properties = d
        return dropdown_options_archival_change

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
    def dropdown_option_ids(self) -> List[str]:
        if isinstance(self._dropdown_option_ids, Unset):
            raise NotPresentError(self, "dropdown_option_ids")
        return self._dropdown_option_ids

    @dropdown_option_ids.setter
    def dropdown_option_ids(self, value: List[str]) -> None:
        self._dropdown_option_ids = value

    @dropdown_option_ids.deleter
    def dropdown_option_ids(self) -> None:
        self._dropdown_option_ids = UNSET
