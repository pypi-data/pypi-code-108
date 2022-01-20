from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.json_data_type import JsonDataType
from ..types import UNSET, Unset

T = TypeVar("T", bound="JsonDataDtype")


@attr.s(auto_attribs=True)
class JsonDataDtype:
    """  """

    name: str
    type: JsonDataType
    date_format: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        type = self.type.value

        date_format = self.date_format

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type,
            }
        )
        if date_format is not UNSET:
            field_dict["dateFormat"] = date_format

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        type = JsonDataType(d.pop("type"))

        date_format = d.pop("dateFormat", UNSET)

        json_data_dtype = cls(
            name=name,
            type=type,
            date_format=date_format,
        )

        json_data_dtype.additional_properties = d
        return json_data_dtype

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
