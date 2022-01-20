from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.mixture import Mixture
from ..types import UNSET, Unset

T = TypeVar("T", bound="MixturesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class MixturesPaginatedList:
    """  """

    _mixtures: Union[Unset, List[Mixture]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("mixtures={}".format(repr(self._mixtures)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "MixturesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        mixtures: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._mixtures, Unset):
            mixtures = []
            for mixtures_item_data in self._mixtures:
                mixtures_item = mixtures_item_data.to_dict()

                mixtures.append(mixtures_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mixtures is not UNSET:
            field_dict["mixtures"] = mixtures
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_mixtures() -> Union[Unset, List[Mixture]]:
            mixtures = []
            _mixtures = d.pop("mixtures")
            for mixtures_item_data in _mixtures or []:
                mixtures_item = Mixture.from_dict(mixtures_item_data)

                mixtures.append(mixtures_item)

            return mixtures

        mixtures = get_mixtures() if "mixtures" in d else cast(Union[Unset, List[Mixture]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        mixtures_paginated_list = cls(
            mixtures=mixtures,
            next_token=next_token,
        )

        mixtures_paginated_list.additional_properties = d
        return mixtures_paginated_list

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
    def mixtures(self) -> List[Mixture]:
        if isinstance(self._mixtures, Unset):
            raise NotPresentError(self, "mixtures")
        return self._mixtures

    @mixtures.setter
    def mixtures(self, value: List[Mixture]) -> None:
        self._mixtures = value

    @mixtures.deleter
    def mixtures(self) -> None:
        self._mixtures = UNSET

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
