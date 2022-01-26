from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.request_task_schema import RequestTaskSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestTaskSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class RequestTaskSchemasPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _request_task_schemas: Union[Unset, List[RequestTaskSchema]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("request_task_schemas={}".format(repr(self._request_task_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestTaskSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        request_task_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._request_task_schemas, Unset):
            request_task_schemas = []
            for request_task_schemas_item_data in self._request_task_schemas:
                request_task_schemas_item = request_task_schemas_item_data.to_dict()

                request_task_schemas.append(request_task_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if request_task_schemas is not UNSET:
            field_dict["requestTaskSchemas"] = request_task_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_request_task_schemas() -> Union[Unset, List[RequestTaskSchema]]:
            request_task_schemas = []
            _request_task_schemas = d.pop("requestTaskSchemas")
            for request_task_schemas_item_data in _request_task_schemas or []:
                request_task_schemas_item = RequestTaskSchema.from_dict(request_task_schemas_item_data)

                request_task_schemas.append(request_task_schemas_item)

            return request_task_schemas

        request_task_schemas = (
            get_request_task_schemas()
            if "requestTaskSchemas" in d
            else cast(Union[Unset, List[RequestTaskSchema]], UNSET)
        )

        request_task_schemas_paginated_list = cls(
            next_token=next_token,
            request_task_schemas=request_task_schemas,
        )

        request_task_schemas_paginated_list.additional_properties = d
        return request_task_schemas_paginated_list

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
    def request_task_schemas(self) -> List[RequestTaskSchema]:
        if isinstance(self._request_task_schemas, Unset):
            raise NotPresentError(self, "request_task_schemas")
        return self._request_task_schemas

    @request_task_schemas.setter
    def request_task_schemas(self, value: List[RequestTaskSchema]) -> None:
        self._request_task_schemas = value

    @request_task_schemas.deleter
    def request_task_schemas(self) -> None:
        self._request_task_schemas = UNSET
