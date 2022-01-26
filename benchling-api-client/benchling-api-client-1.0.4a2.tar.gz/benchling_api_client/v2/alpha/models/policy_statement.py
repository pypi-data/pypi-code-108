from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicyStatement")


@attr.s(auto_attribs=True, repr=False)
class PolicyStatement:
    """  """

    _access: Union[Unset, str] = UNSET
    _description: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("access={}".format(repr(self._access)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PolicyStatement({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        access = self._access
        description = self._description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access is not UNSET:
            field_dict["access"] = access
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_access() -> Union[Unset, str]:
            access = d.pop("access")
            return access

        access = get_access() if "access" in d else cast(Union[Unset, str], UNSET)

        def get_description() -> Union[Unset, str]:
            description = d.pop("description")
            return description

        description = get_description() if "description" in d else cast(Union[Unset, str], UNSET)

        policy_statement = cls(
            access=access,
            description=description,
        )

        policy_statement.additional_properties = d
        return policy_statement

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
    def access(self) -> str:
        if isinstance(self._access, Unset):
            raise NotPresentError(self, "access")
        return self._access

    @access.setter
    def access(self, value: str) -> None:
        self._access = value

    @access.deleter
    def access(self) -> None:
        self._access = UNSET

    @property
    def description(self) -> str:
        if isinstance(self._description, Unset):
            raise NotPresentError(self, "description")
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    @description.deleter
    def description(self) -> None:
        self._description = UNSET
