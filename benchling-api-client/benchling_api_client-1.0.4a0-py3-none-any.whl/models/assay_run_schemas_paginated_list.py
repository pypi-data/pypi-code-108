from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.assay_run_schema import AssayRunSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayRunSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class AssayRunSchemasPaginatedList:
    """  """

    _assay_run_schemas: Union[Unset, List[AssayRunSchema]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assay_run_schemas={}".format(repr(self._assay_run_schemas)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayRunSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_run_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._assay_run_schemas, Unset):
            assay_run_schemas = []
            for assay_run_schemas_item_data in self._assay_run_schemas:
                assay_run_schemas_item = assay_run_schemas_item_data.to_dict()

                assay_run_schemas.append(assay_run_schemas_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assay_run_schemas is not UNSET:
            field_dict["assayRunSchemas"] = assay_run_schemas
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assay_run_schemas() -> Union[Unset, List[AssayRunSchema]]:
            assay_run_schemas = []
            _assay_run_schemas = d.pop("assayRunSchemas")
            for assay_run_schemas_item_data in _assay_run_schemas or []:
                assay_run_schemas_item = AssayRunSchema.from_dict(assay_run_schemas_item_data)

                assay_run_schemas.append(assay_run_schemas_item)

            return assay_run_schemas

        assay_run_schemas = (
            get_assay_run_schemas()
            if "assayRunSchemas" in d
            else cast(Union[Unset, List[AssayRunSchema]], UNSET)
        )

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        assay_run_schemas_paginated_list = cls(
            assay_run_schemas=assay_run_schemas,
            next_token=next_token,
        )

        assay_run_schemas_paginated_list.additional_properties = d
        return assay_run_schemas_paginated_list

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
    def assay_run_schemas(self) -> List[AssayRunSchema]:
        if isinstance(self._assay_run_schemas, Unset):
            raise NotPresentError(self, "assay_run_schemas")
        return self._assay_run_schemas

    @assay_run_schemas.setter
    def assay_run_schemas(self, value: List[AssayRunSchema]) -> None:
        self._assay_run_schemas = value

    @assay_run_schemas.deleter
    def assay_run_schemas(self) -> None:
        self._assay_run_schemas = UNSET

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
