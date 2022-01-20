from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.location_schema import LocationSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="LocationSchemasList")


@attr.s(auto_attribs=True, repr=False)
class LocationSchemasList:
    """  """

    _location_schemas: Union[Unset, List[LocationSchema]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("location_schemas={}".format(repr(self._location_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LocationSchemasList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        location_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._location_schemas, Unset):
            location_schemas = []
            for location_schemas_item_data in self._location_schemas:
                location_schemas_item = location_schemas_item_data.to_dict()

                location_schemas.append(location_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if location_schemas is not UNSET:
            field_dict["locationSchemas"] = location_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_location_schemas() -> Union[Unset, List[LocationSchema]]:
            location_schemas = []
            _location_schemas = d.pop("locationSchemas")
            for location_schemas_item_data in _location_schemas or []:
                location_schemas_item = LocationSchema.from_dict(location_schemas_item_data)

                location_schemas.append(location_schemas_item)

            return location_schemas

        location_schemas = (
            get_location_schemas()
            if "locationSchemas" in d
            else cast(Union[Unset, List[LocationSchema]], UNSET)
        )

        location_schemas_list = cls(
            location_schemas=location_schemas,
        )

        location_schemas_list.additional_properties = d
        return location_schemas_list

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
    def location_schemas(self) -> List[LocationSchema]:
        if isinstance(self._location_schemas, Unset):
            raise NotPresentError(self, "location_schemas")
        return self._location_schemas

    @location_schemas.setter
    def location_schemas(self, value: List[LocationSchema]) -> None:
        self._location_schemas = value

    @location_schemas.deleter
    def location_schemas(self) -> None:
        self._location_schemas = UNSET
