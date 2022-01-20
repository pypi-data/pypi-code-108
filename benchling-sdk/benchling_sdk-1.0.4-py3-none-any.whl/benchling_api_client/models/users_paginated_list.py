from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.user import User
from ..types import UNSET, Unset

T = TypeVar("T", bound="UsersPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class UsersPaginatedList:
    """  """

    _users: Union[Unset, List[User]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("users={}".format(repr(self._users)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "UsersPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        users: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._users, Unset):
            users = []
            for users_item_data in self._users:
                users_item = users_item_data.to_dict()

                users.append(users_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if users is not UNSET:
            field_dict["users"] = users
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_users() -> Union[Unset, List[User]]:
            users = []
            _users = d.pop("users")
            for users_item_data in _users or []:
                users_item = User.from_dict(users_item_data)

                users.append(users_item)

            return users

        users = get_users() if "users" in d else cast(Union[Unset, List[User]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        users_paginated_list = cls(
            users=users,
            next_token=next_token,
        )

        users_paginated_list.additional_properties = d
        return users_paginated_list

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
    def users(self) -> List[User]:
        if isinstance(self._users, Unset):
            raise NotPresentError(self, "users")
        return self._users

    @users.setter
    def users(self, value: List[User]) -> None:
        self._users = value

    @users.deleter
    def users(self) -> None:
        self._users = UNSET

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
