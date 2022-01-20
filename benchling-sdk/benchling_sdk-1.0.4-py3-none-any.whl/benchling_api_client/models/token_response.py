from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.token_response_token_type import TokenResponseTokenType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenResponse")


@attr.s(auto_attribs=True, repr=False)
class TokenResponse:
    """  """

    _access_token: Union[Unset, str] = UNSET
    _expires_in: Union[Unset, int] = UNSET
    _token_type: Union[Unset, TokenResponseTokenType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("access_token={}".format(repr(self._access_token)))
        fields.append("expires_in={}".format(repr(self._expires_in)))
        fields.append("token_type={}".format(repr(self._token_type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TokenResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        access_token = self._access_token
        expires_in = self._expires_in
        token_type: Union[Unset, int] = UNSET
        if not isinstance(self._token_type, Unset):
            token_type = self._token_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access_token is not UNSET:
            field_dict["access_token"] = access_token
        if expires_in is not UNSET:
            field_dict["expires_in"] = expires_in
        if token_type is not UNSET:
            field_dict["token_type"] = token_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_access_token() -> Union[Unset, str]:
            access_token = d.pop("access_token")
            return access_token

        access_token = get_access_token() if "access_token" in d else cast(Union[Unset, str], UNSET)

        def get_expires_in() -> Union[Unset, int]:
            expires_in = d.pop("expires_in")
            return expires_in

        expires_in = get_expires_in() if "expires_in" in d else cast(Union[Unset, int], UNSET)

        def get_token_type() -> Union[Unset, TokenResponseTokenType]:
            token_type = None
            _token_type = d.pop("token_type")
            if _token_type is not None and _token_type is not UNSET:
                try:
                    token_type = TokenResponseTokenType(_token_type)
                except ValueError:
                    token_type = TokenResponseTokenType.of_unknown(_token_type)

            return token_type

        token_type = (
            get_token_type() if "token_type" in d else cast(Union[Unset, TokenResponseTokenType], UNSET)
        )

        token_response = cls(
            access_token=access_token,
            expires_in=expires_in,
            token_type=token_type,
        )

        token_response.additional_properties = d
        return token_response

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
    def access_token(self) -> str:
        if isinstance(self._access_token, Unset):
            raise NotPresentError(self, "access_token")
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token = value

    @access_token.deleter
    def access_token(self) -> None:
        self._access_token = UNSET

    @property
    def expires_in(self) -> int:
        """ Number of seconds that token is valid for """
        if isinstance(self._expires_in, Unset):
            raise NotPresentError(self, "expires_in")
        return self._expires_in

    @expires_in.setter
    def expires_in(self, value: int) -> None:
        self._expires_in = value

    @expires_in.deleter
    def expires_in(self) -> None:
        self._expires_in = UNSET

    @property
    def token_type(self) -> TokenResponseTokenType:
        if isinstance(self._token_type, Unset):
            raise NotPresentError(self, "token_type")
        return self._token_type

    @token_type.setter
    def token_type(self, value: TokenResponseTokenType) -> None:
        self._token_type = value

    @token_type.deleter
    def token_type(self) -> None:
        self._token_type = UNSET
