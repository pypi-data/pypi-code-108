from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.token_create_grant_type import TokenCreateGrantType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenCreate")


@attr.s(auto_attribs=True, repr=False)
class TokenCreate:
    """  """

    _grant_type: TokenCreateGrantType
    _client_id: Union[Unset, str] = UNSET
    _client_secret: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("grant_type={}".format(repr(self._grant_type)))
        fields.append("client_id={}".format(repr(self._client_id)))
        fields.append("client_secret={}".format(repr(self._client_secret)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TokenCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        grant_type = self._grant_type.value

        client_id = self._client_id
        client_secret = self._client_secret

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "grant_type": grant_type,
            }
        )
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if client_secret is not UNSET:
            field_dict["client_secret"] = client_secret

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_grant_type() -> TokenCreateGrantType:
            _grant_type = d.pop("grant_type")
            try:
                grant_type = TokenCreateGrantType(_grant_type)
            except ValueError:
                grant_type = TokenCreateGrantType.of_unknown(_grant_type)

            return grant_type

        grant_type = get_grant_type() if "grant_type" in d else cast(TokenCreateGrantType, UNSET)

        def get_client_id() -> Union[Unset, str]:
            client_id = d.pop("client_id")
            return client_id

        client_id = get_client_id() if "client_id" in d else cast(Union[Unset, str], UNSET)

        def get_client_secret() -> Union[Unset, str]:
            client_secret = d.pop("client_secret")
            return client_secret

        client_secret = get_client_secret() if "client_secret" in d else cast(Union[Unset, str], UNSET)

        token_create = cls(
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
        )

        token_create.additional_properties = d
        return token_create

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
    def grant_type(self) -> TokenCreateGrantType:
        if isinstance(self._grant_type, Unset):
            raise NotPresentError(self, "grant_type")
        return self._grant_type

    @grant_type.setter
    def grant_type(self, value: TokenCreateGrantType) -> None:
        self._grant_type = value

    @property
    def client_id(self) -> str:
        """ID of client to request token for. Leave off if client ID and secret are being supplied through Authorization header."""
        if isinstance(self._client_id, Unset):
            raise NotPresentError(self, "client_id")
        return self._client_id

    @client_id.setter
    def client_id(self, value: str) -> None:
        self._client_id = value

    @client_id.deleter
    def client_id(self) -> None:
        self._client_id = UNSET

    @property
    def client_secret(self) -> str:
        """Leave off if client ID and secret are being supplied through Authorization header."""
        if isinstance(self._client_secret, Unset):
            raise NotPresentError(self, "client_secret")
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value: str) -> None:
        self._client_secret = value

    @client_secret.deleter
    def client_secret(self) -> None:
        self._client_secret = UNSET
