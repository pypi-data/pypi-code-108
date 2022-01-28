from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.collaboration import Collaboration
from ..types import UNSET, Unset

T = TypeVar("T", bound="CollaborationsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class CollaborationsPaginatedList:
    """  """

    _collaborations: Union[Unset, List[Collaboration]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("collaborations={}".format(repr(self._collaborations)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "CollaborationsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        collaborations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._collaborations, Unset):
            collaborations = []
            for collaborations_item_data in self._collaborations:
                collaborations_item = collaborations_item_data.to_dict()

                collaborations.append(collaborations_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if collaborations is not UNSET:
            field_dict["collaborations"] = collaborations
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_collaborations() -> Union[Unset, List[Collaboration]]:
            collaborations = []
            _collaborations = d.pop("collaborations")
            for collaborations_item_data in _collaborations or []:
                collaborations_item = Collaboration.from_dict(collaborations_item_data)

                collaborations.append(collaborations_item)

            return collaborations

        collaborations = (
            get_collaborations() if "collaborations" in d else cast(Union[Unset, List[Collaboration]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        collaborations_paginated_list = cls(
            collaborations=collaborations,
            next_token=next_token,
        )

        return collaborations_paginated_list

    @property
    def collaborations(self) -> List[Collaboration]:
        if isinstance(self._collaborations, Unset):
            raise NotPresentError(self, "collaborations")
        return self._collaborations

    @collaborations.setter
    def collaborations(self, value: List[Collaboration]) -> None:
        self._collaborations = value

    @collaborations.deleter
    def collaborations(self) -> None:
        self._collaborations = UNSET

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
