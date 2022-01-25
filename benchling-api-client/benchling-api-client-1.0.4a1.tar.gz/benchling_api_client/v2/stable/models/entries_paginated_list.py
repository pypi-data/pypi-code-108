from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry import Entry
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntriesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class EntriesPaginatedList:
    """  """

    _entries: Union[Unset, List[Entry]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entries={}".format(repr(self._entries)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntriesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entries: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._entries, Unset):
            entries = []
            for entries_item_data in self._entries:
                entries_item = entries_item_data.to_dict()

                entries.append(entries_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entries is not UNSET:
            field_dict["entries"] = entries
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entries() -> Union[Unset, List[Entry]]:
            entries = []
            _entries = d.pop("entries")
            for entries_item_data in _entries or []:
                entries_item = Entry.from_dict(entries_item_data)

                entries.append(entries_item)

            return entries

        entries = get_entries() if "entries" in d else cast(Union[Unset, List[Entry]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        entries_paginated_list = cls(
            entries=entries,
            next_token=next_token,
        )

        entries_paginated_list.additional_properties = d
        return entries_paginated_list

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
    def entries(self) -> List[Entry]:
        if isinstance(self._entries, Unset):
            raise NotPresentError(self, "entries")
        return self._entries

    @entries.setter
    def entries(self, value: List[Entry]) -> None:
        self._entries = value

    @entries.deleter
    def entries(self) -> None:
        self._entries = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
