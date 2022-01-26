from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.field_with_resolution import FieldWithResolution

T = TypeVar("T", bound="FieldsWithResolution")


@attr.s(auto_attribs=True, repr=False)
class FieldsWithResolution:
    """  """

    additional_properties: Dict[str, FieldWithResolution] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FieldsWithResolution({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        fields_with_resolution = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = FieldWithResolution.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        fields_with_resolution.additional_properties = additional_properties
        return fields_with_resolution

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> FieldWithResolution:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: FieldWithResolution) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[FieldWithResolution]:
        return self.additional_properties.get(key, default)
