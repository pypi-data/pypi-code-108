from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.custom_field import CustomField

T = TypeVar("T", bound="CustomFields")


@attr.s(auto_attribs=True, repr=False)
class CustomFields:
    """  """

    additional_properties: Dict[str, CustomField] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "CustomFields({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        custom_fields = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = CustomField.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        custom_fields.additional_properties = additional_properties
        return custom_fields

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> CustomField:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: CustomField) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[CustomField]:
        return self.additional_properties.get(key, default)
