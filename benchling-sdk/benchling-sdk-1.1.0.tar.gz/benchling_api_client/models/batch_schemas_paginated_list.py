from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.batch_schema import BatchSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class BatchSchemasPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _batch_schemas: Union[Unset, List[BatchSchema]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("batch_schemas={}".format(repr(self._batch_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BatchSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        batch_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._batch_schemas, Unset):
            batch_schemas = []
            for batch_schemas_item_data in self._batch_schemas:
                batch_schemas_item = batch_schemas_item_data.to_dict()

                batch_schemas.append(batch_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if batch_schemas is not UNSET:
            field_dict["batchSchemas"] = batch_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_batch_schemas() -> Union[Unset, List[BatchSchema]]:
            batch_schemas = []
            _batch_schemas = d.pop("batchSchemas")
            for batch_schemas_item_data in _batch_schemas or []:
                batch_schemas_item = BatchSchema.from_dict(batch_schemas_item_data)

                batch_schemas.append(batch_schemas_item)

            return batch_schemas

        batch_schemas = (
            get_batch_schemas() if "batchSchemas" in d else cast(Union[Unset, List[BatchSchema]], UNSET)
        )

        batch_schemas_paginated_list = cls(
            next_token=next_token,
            batch_schemas=batch_schemas,
        )

        batch_schemas_paginated_list.additional_properties = d
        return batch_schemas_paginated_list

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

    @property
    def batch_schemas(self) -> List[BatchSchema]:
        if isinstance(self._batch_schemas, Unset):
            raise NotPresentError(self, "batch_schemas")
        return self._batch_schemas

    @batch_schemas.setter
    def batch_schemas(self, value: List[BatchSchema]) -> None:
        self._batch_schemas = value

    @batch_schemas.deleter
    def batch_schemas(self) -> None:
        self._batch_schemas = UNSET
