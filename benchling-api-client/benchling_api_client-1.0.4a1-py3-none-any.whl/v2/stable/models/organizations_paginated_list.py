from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.organization import Organization
from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class OrganizationsPaginatedList:
    """  """

    _organizations: Union[Unset, List[Organization]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("organizations={}".format(repr(self._organizations)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "OrganizationsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        organizations: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._organizations, Unset):
            organizations = []
            for organizations_item_data in self._organizations:
                organizations_item = organizations_item_data.to_dict()

                organizations.append(organizations_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if organizations is not UNSET:
            field_dict["organizations"] = organizations
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_organizations() -> Union[Unset, List[Organization]]:
            organizations = []
            _organizations = d.pop("organizations")
            for organizations_item_data in _organizations or []:
                organizations_item = Organization.from_dict(organizations_item_data)

                organizations.append(organizations_item)

            return organizations

        organizations = (
            get_organizations() if "organizations" in d else cast(Union[Unset, List[Organization]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        organizations_paginated_list = cls(
            organizations=organizations,
            next_token=next_token,
        )

        organizations_paginated_list.additional_properties = d
        return organizations_paginated_list

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
    def organizations(self) -> List[Organization]:
        if isinstance(self._organizations, Unset):
            raise NotPresentError(self, "organizations")
        return self._organizations

    @organizations.setter
    def organizations(self, value: List[Organization]) -> None:
        self._organizations = value

    @organizations.deleter
    def organizations(self) -> None:
        self._organizations = UNSET

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
