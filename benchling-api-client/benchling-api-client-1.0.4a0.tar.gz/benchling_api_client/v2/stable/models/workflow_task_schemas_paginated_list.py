from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_schema import WorkflowTaskSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskSchemasPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskSchemasPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _workflow_task_schemas: Union[Unset, List[WorkflowTaskSchema]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("workflow_task_schemas={}".format(repr(self._workflow_task_schemas)))
        return "WorkflowTaskSchemasPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        workflow_task_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_task_schemas, Unset):
            workflow_task_schemas = []
            for workflow_task_schemas_item_data in self._workflow_task_schemas:
                workflow_task_schemas_item = workflow_task_schemas_item_data.to_dict()

                workflow_task_schemas.append(workflow_task_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if workflow_task_schemas is not UNSET:
            field_dict["workflowTaskSchemas"] = workflow_task_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_task_schemas() -> Union[Unset, List[WorkflowTaskSchema]]:
            workflow_task_schemas = []
            _workflow_task_schemas = d.pop("workflowTaskSchemas")
            for workflow_task_schemas_item_data in _workflow_task_schemas or []:
                workflow_task_schemas_item = WorkflowTaskSchema.from_dict(workflow_task_schemas_item_data)

                workflow_task_schemas.append(workflow_task_schemas_item)

            return workflow_task_schemas

        workflow_task_schemas = (
            get_workflow_task_schemas()
            if "workflowTaskSchemas" in d
            else cast(Union[Unset, List[WorkflowTaskSchema]], UNSET)
        )

        workflow_task_schemas_paginated_list = cls(
            next_token=next_token,
            workflow_task_schemas=workflow_task_schemas,
        )

        return workflow_task_schemas_paginated_list

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
    def workflow_task_schemas(self) -> List[WorkflowTaskSchema]:
        if isinstance(self._workflow_task_schemas, Unset):
            raise NotPresentError(self, "workflow_task_schemas")
        return self._workflow_task_schemas

    @workflow_task_schemas.setter
    def workflow_task_schemas(self, value: List[WorkflowTaskSchema]) -> None:
        self._workflow_task_schemas = value

    @workflow_task_schemas.deleter
    def workflow_task_schemas(self) -> None:
        self._workflow_task_schemas = UNSET
