from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.access_policy import AccessPolicy
from ..types import UNSET, Unset

T = TypeVar("T", bound="AccessPoliciesPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class AccessPoliciesPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _policies: Union[Unset, List[AccessPolicy]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("policies={}".format(repr(self._policies)))
        return "AccessPoliciesPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        policies: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._policies, Unset):
            policies = []
            for policies_item_data in self._policies:
                policies_item = policies_item_data.to_dict()

                policies.append(policies_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if policies is not UNSET:
            field_dict["policies"] = policies

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_policies() -> Union[Unset, List[AccessPolicy]]:
            policies = []
            _policies = d.pop("policies")
            for policies_item_data in _policies or []:
                policies_item = AccessPolicy.from_dict(policies_item_data)

                policies.append(policies_item)

            return policies

        policies = get_policies() if "policies" in d else cast(Union[Unset, List[AccessPolicy]], UNSET)

        access_policies_paginated_list = cls(
            next_token=next_token,
            policies=policies,
        )

        return access_policies_paginated_list

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
    def policies(self) -> List[AccessPolicy]:
        if isinstance(self._policies, Unset):
            raise NotPresentError(self, "policies")
        return self._policies

    @policies.setter
    def policies(self, value: List[AccessPolicy]) -> None:
        self._policies = value

    @policies.deleter
    def policies(self) -> None:
        self._policies = UNSET
