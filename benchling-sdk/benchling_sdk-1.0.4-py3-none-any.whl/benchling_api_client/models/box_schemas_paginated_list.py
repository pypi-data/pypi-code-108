from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.box_schema import BoxSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="BoxSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class BoxSchemasPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _box_schemas: Union[Unset, List[BoxSchema]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("box_schemas={}".format(repr(self._box_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BoxSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        box_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._box_schemas, Unset):
            box_schemas = []
            for box_schemas_item_data in self._box_schemas:
                box_schemas_item = box_schemas_item_data.to_dict()

                box_schemas.append(box_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if box_schemas is not UNSET:
            field_dict["boxSchemas"] = box_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_box_schemas() -> Union[Unset, List[BoxSchema]]:
            box_schemas = []
            _box_schemas = d.pop("boxSchemas")
            for box_schemas_item_data in _box_schemas or []:
                box_schemas_item = BoxSchema.from_dict(box_schemas_item_data)

                box_schemas.append(box_schemas_item)

            return box_schemas

        box_schemas = get_box_schemas() if "boxSchemas" in d else cast(Union[Unset, List[BoxSchema]], UNSET)

        box_schemas_paginated_list = cls(
            next_token=next_token,
            box_schemas=box_schemas,
        )

        box_schemas_paginated_list.additional_properties = d
        return box_schemas_paginated_list

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
    def box_schemas(self) -> List[BoxSchema]:
        if isinstance(self._box_schemas, Unset):
            raise NotPresentError(self, "box_schemas")
        return self._box_schemas

    @box_schemas.setter
    def box_schemas(self, value: List[BoxSchema]) -> None:
        self._box_schemas = value

    @box_schemas.deleter
    def box_schemas(self) -> None:
        self._box_schemas = UNSET
