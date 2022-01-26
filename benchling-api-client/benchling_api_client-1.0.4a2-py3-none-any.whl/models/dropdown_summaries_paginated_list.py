from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dropdown_summary import DropdownSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="DropdownSummariesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class DropdownSummariesPaginatedList:
    """  """

    _dropdowns: Union[Unset, List[DropdownSummary]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("dropdowns={}".format(repr(self._dropdowns)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "DropdownSummariesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dropdowns: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dropdowns, Unset):
            dropdowns = []
            for dropdowns_item_data in self._dropdowns:
                dropdowns_item = dropdowns_item_data.to_dict()

                dropdowns.append(dropdowns_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dropdowns is not UNSET:
            field_dict["dropdowns"] = dropdowns
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dropdowns() -> Union[Unset, List[DropdownSummary]]:
            dropdowns = []
            _dropdowns = d.pop("dropdowns")
            for dropdowns_item_data in _dropdowns or []:
                dropdowns_item = DropdownSummary.from_dict(dropdowns_item_data)

                dropdowns.append(dropdowns_item)

            return dropdowns

        dropdowns = get_dropdowns() if "dropdowns" in d else cast(Union[Unset, List[DropdownSummary]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        dropdown_summaries_paginated_list = cls(
            dropdowns=dropdowns,
            next_token=next_token,
        )

        dropdown_summaries_paginated_list.additional_properties = d
        return dropdown_summaries_paginated_list

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
    def dropdowns(self) -> List[DropdownSummary]:
        if isinstance(self._dropdowns, Unset):
            raise NotPresentError(self, "dropdowns")
        return self._dropdowns

    @dropdowns.setter
    def dropdowns(self, value: List[DropdownSummary]) -> None:
        self._dropdowns = value

    @dropdowns.deleter
    def dropdowns(self) -> None:
        self._dropdowns = UNSET

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
