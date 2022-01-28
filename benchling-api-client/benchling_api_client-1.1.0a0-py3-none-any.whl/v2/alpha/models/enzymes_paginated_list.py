from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.enzyme import Enzyme
from ..types import UNSET, Unset

T = TypeVar("T", bound="EnzymesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class EnzymesPaginatedList:
    """  """

    _enzymes: Union[Unset, List[Enzyme]] = UNSET
    _next_token: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("enzymes={}".format(repr(self._enzymes)))
        fields.append("next_token={}".format(repr(self._next_token)))
        return "EnzymesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        enzymes: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._enzymes, Unset):
            enzymes = []
            for enzymes_item_data in self._enzymes:
                enzymes_item = enzymes_item_data.to_dict()

                enzymes.append(enzymes_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if enzymes is not UNSET:
            field_dict["enzymes"] = enzymes
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_enzymes() -> Union[Unset, List[Enzyme]]:
            enzymes = []
            _enzymes = d.pop("enzymes")
            for enzymes_item_data in _enzymes or []:
                enzymes_item = Enzyme.from_dict(enzymes_item_data)

                enzymes.append(enzymes_item)

            return enzymes

        enzymes = get_enzymes() if "enzymes" in d else cast(Union[Unset, List[Enzyme]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        enzymes_paginated_list = cls(
            enzymes=enzymes,
            next_token=next_token,
        )

        return enzymes_paginated_list

    @property
    def enzymes(self) -> List[Enzyme]:
        if isinstance(self._enzymes, Unset):
            raise NotPresentError(self, "enzymes")
        return self._enzymes

    @enzymes.setter
    def enzymes(self, value: List[Enzyme]) -> None:
        self._enzymes = value

    @enzymes.deleter
    def enzymes(self) -> None:
        self._enzymes = UNSET

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
