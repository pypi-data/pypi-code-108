from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.o_auth_unauthorized_error_error_type import OAuthUnauthorizedErrorErrorType
from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthUnauthorizedErrorError")


@attr.s(auto_attribs=True, repr=False)
class OAuthUnauthorizedErrorError:
    """  """

    _type: Union[Unset, OAuthUnauthorizedErrorErrorType] = UNSET
    _message: Union[Unset, str] = UNSET
    _user_message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("type={}".format(repr(self._type)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("user_message={}".format(repr(self._user_message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "OAuthUnauthorizedErrorError({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        message = self._message
        user_message = self._user_message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type is not UNSET:
            field_dict["type"] = type
        if message is not UNSET:
            field_dict["message"] = message
        if user_message is not UNSET:
            field_dict["userMessage"] = user_message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_type() -> Union[Unset, OAuthUnauthorizedErrorErrorType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = OAuthUnauthorizedErrorErrorType(_type)
                except ValueError:
                    type = OAuthUnauthorizedErrorErrorType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, OAuthUnauthorizedErrorErrorType], UNSET)

        def get_message() -> Union[Unset, str]:
            message = d.pop("message")
            return message

        message = get_message() if "message" in d else cast(Union[Unset, str], UNSET)

        def get_user_message() -> Union[Unset, str]:
            user_message = d.pop("userMessage")
            return user_message

        user_message = get_user_message() if "userMessage" in d else cast(Union[Unset, str], UNSET)

        o_auth_unauthorized_error_error = cls(
            type=type,
            message=message,
            user_message=user_message,
        )

        o_auth_unauthorized_error_error.additional_properties = d
        return o_auth_unauthorized_error_error

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
    def type(self) -> OAuthUnauthorizedErrorErrorType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: OAuthUnauthorizedErrorErrorType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def message(self) -> str:
        if isinstance(self._message, Unset):
            raise NotPresentError(self, "message")
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        self._message = value

    @message.deleter
    def message(self) -> None:
        self._message = UNSET

    @property
    def user_message(self) -> str:
        if isinstance(self._user_message, Unset):
            raise NotPresentError(self, "user_message")
        return self._user_message

    @user_message.setter
    def user_message(self, value: str) -> None:
        self._user_message = value

    @user_message.deleter
    def user_message(self) -> None:
        self._user_message = UNSET
