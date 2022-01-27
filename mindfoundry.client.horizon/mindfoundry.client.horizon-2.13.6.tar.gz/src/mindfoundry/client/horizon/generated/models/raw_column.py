from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="RawColumn")


@attr.s(auto_attribs=True)
class RawColumn:
    """ Represents raw data, as defined in a dataset on upload  """

    id: int
    name: str
    is_text: Union[Unset, bool] = False
    is_binary: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        name = self.name
        is_text = self.is_text
        is_binary = self.is_binary

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )
        if is_text is not UNSET:
            field_dict["isText"] = is_text
        if is_binary is not UNSET:
            field_dict["isBinary"] = is_binary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        is_text = d.pop("isText", UNSET)

        is_binary = d.pop("isBinary", UNSET)

        raw_column = cls(
            id=id,
            name=name,
            is_text=is_text,
            is_binary=is_binary,
        )

        raw_column.additional_properties = d
        return raw_column

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
