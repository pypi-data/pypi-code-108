from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="User")


@attr.s(auto_attribs=True)
class User:
    """ Information about a specific user  """

    id: int
    auth_id: str
    is_support: bool
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        auth_id = self.auth_id
        is_support = self.is_support

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "authId": auth_id,
                "isSupport": is_support,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        auth_id = d.pop("authId")

        is_support = d.pop("isSupport")

        user = cls(
            id=id,
            auth_id=auth_id,
            is_support=is_support,
        )

        user.additional_properties = d
        return user

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
