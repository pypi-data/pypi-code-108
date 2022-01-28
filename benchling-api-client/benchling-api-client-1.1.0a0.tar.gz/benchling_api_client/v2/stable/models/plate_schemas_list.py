from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.plate_schema import PlateSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlateSchemasList")


@attr.s(auto_attribs=True, repr=False)
class PlateSchemasList:
    """  """

    _plate_schemas: Union[Unset, List[PlateSchema]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("plate_schemas={}".format(repr(self._plate_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PlateSchemasList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        plate_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._plate_schemas, Unset):
            plate_schemas = []
            for plate_schemas_item_data in self._plate_schemas:
                plate_schemas_item = plate_schemas_item_data.to_dict()

                plate_schemas.append(plate_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if plate_schemas is not UNSET:
            field_dict["plateSchemas"] = plate_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_plate_schemas() -> Union[Unset, List[PlateSchema]]:
            plate_schemas = []
            _plate_schemas = d.pop("plateSchemas")
            for plate_schemas_item_data in _plate_schemas or []:
                plate_schemas_item = PlateSchema.from_dict(plate_schemas_item_data)

                plate_schemas.append(plate_schemas_item)

            return plate_schemas

        plate_schemas = (
            get_plate_schemas() if "plateSchemas" in d else cast(Union[Unset, List[PlateSchema]], UNSET)
        )

        plate_schemas_list = cls(
            plate_schemas=plate_schemas,
        )

        plate_schemas_list.additional_properties = d
        return plate_schemas_list

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
    def plate_schemas(self) -> List[PlateSchema]:
        if isinstance(self._plate_schemas, Unset):
            raise NotPresentError(self, "plate_schemas")
        return self._plate_schemas

    @plate_schemas.setter
    def plate_schemas(self, value: List[PlateSchema]) -> None:
        self._plate_schemas = value

    @plate_schemas.deleter
    def plate_schemas(self) -> None:
        self._plate_schemas = UNSET
