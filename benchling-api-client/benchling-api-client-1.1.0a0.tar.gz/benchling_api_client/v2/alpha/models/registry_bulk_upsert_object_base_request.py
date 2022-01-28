from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.fields_with_resolution import FieldsWithResolution
from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistryBulkUpsertObjectBaseRequest")


@attr.s(auto_attribs=True, repr=False)
class RegistryBulkUpsertObjectBaseRequest:
    """  """

    _entity_registry_id: str
    _name: str
    _schema_id: str
    _fields: Union[Unset, FieldsWithResolution] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_registry_id={}".format(repr(self._entity_registry_id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("schema_id={}".format(repr(self._schema_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RegistryBulkUpsertObjectBaseRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_registry_id = self._entity_registry_id
        name = self._name
        schema_id = self._schema_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entityRegistryId": entity_registry_id,
                "name": name,
                "schemaId": schema_id,
            }
        )
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_registry_id() -> str:
            entity_registry_id = d.pop("entityRegistryId")
            return entity_registry_id

        entity_registry_id = get_entity_registry_id() if "entityRegistryId" in d else cast(str, UNSET)

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_schema_id() -> str:
            schema_id = d.pop("schemaId")
            return schema_id

        schema_id = get_schema_id() if "schemaId" in d else cast(str, UNSET)

        def get_fields() -> Union[Unset, FieldsWithResolution]:
            fields: Union[Unset, FieldsWithResolution] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = FieldsWithResolution.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, FieldsWithResolution], UNSET)

        registry_bulk_upsert_object_base_request = cls(
            entity_registry_id=entity_registry_id,
            name=name,
            schema_id=schema_id,
            fields=fields,
        )

        registry_bulk_upsert_object_base_request.additional_properties = d
        return registry_bulk_upsert_object_base_request

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
    def entity_registry_id(self) -> str:
        if isinstance(self._entity_registry_id, Unset):
            raise NotPresentError(self, "entity_registry_id")
        return self._entity_registry_id

    @entity_registry_id.setter
    def entity_registry_id(self, value: str) -> None:
        self._entity_registry_id = value

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def schema_id(self) -> str:
        if isinstance(self._schema_id, Unset):
            raise NotPresentError(self, "schema_id")
        return self._schema_id

    @schema_id.setter
    def schema_id(self, value: str) -> None:
        self._schema_id = value

    @property
    def fields(self) -> FieldsWithResolution:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: FieldsWithResolution) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET
