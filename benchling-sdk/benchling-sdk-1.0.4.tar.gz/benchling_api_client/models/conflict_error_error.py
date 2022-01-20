from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.conflict_error_error_conflicts_item import ConflictErrorErrorConflictsItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConflictErrorError")


@attr.s(auto_attribs=True, repr=False)
class ConflictErrorError:
    """  """

    _conflicts: Union[Unset, List[ConflictErrorErrorConflictsItem]] = UNSET
    _message: Union[Unset, str] = UNSET
    _type: Union[Unset, str] = UNSET
    _user_message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("conflicts={}".format(repr(self._conflicts)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("user_message={}".format(repr(self._user_message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ConflictErrorError({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        conflicts: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._conflicts, Unset):
            conflicts = []
            for conflicts_item_data in self._conflicts:
                conflicts_item = conflicts_item_data.to_dict()

                conflicts.append(conflicts_item)

        message = self._message
        type = self._type
        user_message = self._user_message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if conflicts is not UNSET:
            field_dict["conflicts"] = conflicts
        if message is not UNSET:
            field_dict["message"] = message
        if type is not UNSET:
            field_dict["type"] = type
        if user_message is not UNSET:
            field_dict["userMessage"] = user_message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_conflicts() -> Union[Unset, List[ConflictErrorErrorConflictsItem]]:
            conflicts = []
            _conflicts = d.pop("conflicts")
            for conflicts_item_data in _conflicts or []:
                conflicts_item = ConflictErrorErrorConflictsItem.from_dict(conflicts_item_data)

                conflicts.append(conflicts_item)

            return conflicts

        conflicts = (
            get_conflicts()
            if "conflicts" in d
            else cast(Union[Unset, List[ConflictErrorErrorConflictsItem]], UNSET)
        )

        def get_message() -> Union[Unset, str]:
            message = d.pop("message")
            return message

        message = get_message() if "message" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, str]:
            type = d.pop("type")
            return type

        type = get_type() if "type" in d else cast(Union[Unset, str], UNSET)

        def get_user_message() -> Union[Unset, str]:
            user_message = d.pop("userMessage")
            return user_message

        user_message = get_user_message() if "userMessage" in d else cast(Union[Unset, str], UNSET)

        conflict_error_error = cls(
            conflicts=conflicts,
            message=message,
            type=type,
            user_message=user_message,
        )

        conflict_error_error.additional_properties = d
        return conflict_error_error

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
    def conflicts(self) -> List[ConflictErrorErrorConflictsItem]:
        if isinstance(self._conflicts, Unset):
            raise NotPresentError(self, "conflicts")
        return self._conflicts

    @conflicts.setter
    def conflicts(self, value: List[ConflictErrorErrorConflictsItem]) -> None:
        self._conflicts = value

    @conflicts.deleter
    def conflicts(self) -> None:
        self._conflicts = UNSET

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
    def type(self) -> str:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

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
