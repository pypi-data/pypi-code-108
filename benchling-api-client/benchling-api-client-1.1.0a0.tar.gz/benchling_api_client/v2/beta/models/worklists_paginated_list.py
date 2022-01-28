from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.worklist import Worklist
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorklistsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class WorklistsPaginatedList:
    """ An object containing an array of Worklists """

    _next_token: Union[Unset, str] = UNSET
    _worklists: Union[Unset, List[Worklist]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("worklists={}".format(repr(self._worklists)))
        return "WorklistsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        worklists: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._worklists, Unset):
            worklists = []
            for worklists_item_data in self._worklists:
                worklists_item = worklists_item_data.to_dict()

                worklists.append(worklists_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if worklists is not UNSET:
            field_dict["worklists"] = worklists

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_worklists() -> Union[Unset, List[Worklist]]:
            worklists = []
            _worklists = d.pop("worklists")
            for worklists_item_data in _worklists or []:
                worklists_item = Worklist.from_dict(worklists_item_data)

                worklists.append(worklists_item)

            return worklists

        worklists = get_worklists() if "worklists" in d else cast(Union[Unset, List[Worklist]], UNSET)

        worklists_paginated_list = cls(
            next_token=next_token,
            worklists=worklists,
        )

        return worklists_paginated_list

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

    @property
    def worklists(self) -> List[Worklist]:
        if isinstance(self._worklists, Unset):
            raise NotPresentError(self, "worklists")
        return self._worklists

    @worklists.setter
    def worklists(self, value: List[Worklist]) -> None:
        self._worklists = value

    @worklists.deleter
    def worklists(self) -> None:
        self._worklists = UNSET
