from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestWriteUserAssignee")


@attr.s(auto_attribs=True, repr=False)
class RequestWriteUserAssignee:
    """  """

    _user_id: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("user_id={}".format(repr(self._user_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestWriteUserAssignee({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        user_id = self._user_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "userId": user_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_user_id() -> str:
            user_id = d.pop("userId")
            return user_id

        user_id = get_user_id() if "userId" in d else cast(str, UNSET)

        request_write_user_assignee = cls(
            user_id=user_id,
        )

        request_write_user_assignee.additional_properties = d
        return request_write_user_assignee

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
    def user_id(self) -> str:
        if isinstance(self._user_id, Unset):
            raise NotPresentError(self, "user_id")
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        self._user_id = value
