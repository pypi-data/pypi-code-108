from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task import WorkflowTask
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTasksPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTasksPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _workflow_tasks: Union[Unset, List[WorkflowTask]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("workflow_tasks={}".format(repr(self._workflow_tasks)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTasksPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        workflow_tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_tasks, Unset):
            workflow_tasks = []
            for workflow_tasks_item_data in self._workflow_tasks:
                workflow_tasks_item = workflow_tasks_item_data.to_dict()

                workflow_tasks.append(workflow_tasks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if workflow_tasks is not UNSET:
            field_dict["workflowTasks"] = workflow_tasks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_tasks() -> Union[Unset, List[WorkflowTask]]:
            workflow_tasks = []
            _workflow_tasks = d.pop("workflowTasks")
            for workflow_tasks_item_data in _workflow_tasks or []:
                workflow_tasks_item = WorkflowTask.from_dict(workflow_tasks_item_data)

                workflow_tasks.append(workflow_tasks_item)

            return workflow_tasks

        workflow_tasks = (
            get_workflow_tasks() if "workflowTasks" in d else cast(Union[Unset, List[WorkflowTask]], UNSET)
        )

        workflow_tasks_paginated_list = cls(
            next_token=next_token,
            workflow_tasks=workflow_tasks,
        )

        workflow_tasks_paginated_list.additional_properties = d
        return workflow_tasks_paginated_list

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
    def workflow_tasks(self) -> List[WorkflowTask]:
        if isinstance(self._workflow_tasks, Unset):
            raise NotPresentError(self, "workflow_tasks")
        return self._workflow_tasks

    @workflow_tasks.setter
    def workflow_tasks(self, value: List[WorkflowTask]) -> None:
        self._workflow_tasks = value

    @workflow_tasks.deleter
    def workflow_tasks(self) -> None:
        self._workflow_tasks = UNSET
