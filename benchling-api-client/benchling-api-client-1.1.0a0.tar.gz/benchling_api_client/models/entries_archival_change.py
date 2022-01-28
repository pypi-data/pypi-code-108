from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntriesArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class EntriesArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type. This includes the IDs of entries that changed.."""

    _entry_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entry_ids={}".format(repr(self._entry_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntriesArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._entry_ids, Unset):
            entry_ids = self._entry_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entry_ids is not UNSET:
            field_dict["entryIds"] = entry_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entry_ids() -> Union[Unset, List[str]]:
            entry_ids = cast(List[str], d.pop("entryIds"))

            return entry_ids

        entry_ids = get_entry_ids() if "entryIds" in d else cast(Union[Unset, List[str]], UNSET)

        entries_archival_change = cls(
            entry_ids=entry_ids,
        )

        entries_archival_change.additional_properties = d
        return entries_archival_change

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
    def entry_ids(self) -> List[str]:
        if isinstance(self._entry_ids, Unset):
            raise NotPresentError(self, "entry_ids")
        return self._entry_ids

    @entry_ids.setter
    def entry_ids(self, value: List[str]) -> None:
        self._entry_ids = value

    @entry_ids.deleter
    def entry_ids(self) -> None:
        self._entry_ids = UNSET
