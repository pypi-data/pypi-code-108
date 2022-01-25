from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entity_schema import EntitySchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class EntitySchemasPaginatedList:
    """  """

    _entity_schemas: Union[Unset, List[EntitySchema]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entity_schemas={}".format(repr(self._entity_schemas)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntitySchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._entity_schemas, Unset):
            entity_schemas = []
            for entity_schemas_item_data in self._entity_schemas:
                entity_schemas_item = entity_schemas_item_data.to_dict()

                entity_schemas.append(entity_schemas_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entity_schemas is not UNSET:
            field_dict["entitySchemas"] = entity_schemas
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entity_schemas() -> Union[Unset, List[EntitySchema]]:
            entity_schemas = []
            _entity_schemas = d.pop("entitySchemas")
            for entity_schemas_item_data in _entity_schemas or []:
                entity_schemas_item = EntitySchema.from_dict(entity_schemas_item_data)

                entity_schemas.append(entity_schemas_item)

            return entity_schemas

        entity_schemas = (
            get_entity_schemas() if "entitySchemas" in d else cast(Union[Unset, List[EntitySchema]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        entity_schemas_paginated_list = cls(
            entity_schemas=entity_schemas,
            next_token=next_token,
        )

        entity_schemas_paginated_list.additional_properties = d
        return entity_schemas_paginated_list

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
    def entity_schemas(self) -> List[EntitySchema]:
        if isinstance(self._entity_schemas, Unset):
            raise NotPresentError(self, "entity_schemas")
        return self._entity_schemas

    @entity_schemas.setter
    def entity_schemas(self, value: List[EntitySchema]) -> None:
        self._entity_schemas = value

    @entity_schemas.deleter
    def entity_schemas(self) -> None:
        self._entity_schemas = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
