import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WarehouseCredentials")


@attr.s(auto_attribs=True, repr=False)
class WarehouseCredentials:
    """  """

    _expires_at: Union[Unset, datetime.datetime] = UNSET
    _password: Union[Unset, str] = UNSET
    _username: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("expires_at={}".format(repr(self._expires_at)))
        fields.append("password={}".format(repr(self._password)))
        fields.append("username={}".format(repr(self._username)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WarehouseCredentials({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        expires_at: Union[Unset, str] = UNSET
        if not isinstance(self._expires_at, Unset):
            expires_at = self._expires_at.isoformat()

        password = self._password
        username = self._username

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at
        if password is not UNSET:
            field_dict["password"] = password
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_expires_at() -> Union[Unset, datetime.datetime]:
            expires_at: Union[Unset, datetime.datetime] = UNSET
            _expires_at = d.pop("expiresAt")
            if _expires_at is not None and not isinstance(_expires_at, Unset):
                expires_at = isoparse(cast(str, _expires_at))

            return expires_at

        expires_at = get_expires_at() if "expiresAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_password() -> Union[Unset, str]:
            password = d.pop("password")
            return password

        password = get_password() if "password" in d else cast(Union[Unset, str], UNSET)

        def get_username() -> Union[Unset, str]:
            username = d.pop("username")
            return username

        username = get_username() if "username" in d else cast(Union[Unset, str], UNSET)

        warehouse_credentials = cls(
            expires_at=expires_at,
            password=password,
            username=username,
        )

        warehouse_credentials.additional_properties = d
        return warehouse_credentials

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
    def expires_at(self) -> datetime.datetime:
        """The time after which new connections using the username/password will not be permitted. Upon expiration, currently open connections are not terminated."""
        if isinstance(self._expires_at, Unset):
            raise NotPresentError(self, "expires_at")
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: datetime.datetime) -> None:
        self._expires_at = value

    @expires_at.deleter
    def expires_at(self) -> None:
        self._expires_at = UNSET

    @property
    def password(self) -> str:
        """ The password to connect to the warehouse. """
        if isinstance(self._password, Unset):
            raise NotPresentError(self, "password")
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value

    @password.deleter
    def password(self) -> None:
        self._password = UNSET

    @property
    def username(self) -> str:
        """ The username to connect to the warehouse. """
        if isinstance(self._username, Unset):
            raise NotPresentError(self, "username")
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    @username.deleter
    def username(self) -> None:
        self._username = UNSET
