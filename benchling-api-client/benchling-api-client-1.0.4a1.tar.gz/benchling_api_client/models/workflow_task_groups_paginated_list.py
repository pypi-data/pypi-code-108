from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_group import WorkflowTaskGroup
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskGroupsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskGroupsPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _workflow_task_groups: Union[Unset, List[WorkflowTaskGroup]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("workflow_task_groups={}".format(repr(self._workflow_task_groups)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskGroupsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        workflow_task_groups: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_task_groups, Unset):
            workflow_task_groups = []
            for workflow_task_groups_item_data in self._workflow_task_groups:
                workflow_task_groups_item = workflow_task_groups_item_data.to_dict()

                workflow_task_groups.append(workflow_task_groups_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if workflow_task_groups is not UNSET:
            field_dict["workflowTaskGroups"] = workflow_task_groups

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_task_groups() -> Union[Unset, List[WorkflowTaskGroup]]:
            workflow_task_groups = []
            _workflow_task_groups = d.pop("workflowTaskGroups")
            for workflow_task_groups_item_data in _workflow_task_groups or []:
                workflow_task_groups_item = WorkflowTaskGroup.from_dict(workflow_task_groups_item_data)

                workflow_task_groups.append(workflow_task_groups_item)

            return workflow_task_groups

        workflow_task_groups = (
            get_workflow_task_groups()
            if "workflowTaskGroups" in d
            else cast(Union[Unset, List[WorkflowTaskGroup]], UNSET)
        )

        workflow_task_groups_paginated_list = cls(
            next_token=next_token,
            workflow_task_groups=workflow_task_groups,
        )

        workflow_task_groups_paginated_list.additional_properties = d
        return workflow_task_groups_paginated_list

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
    def workflow_task_groups(self) -> List[WorkflowTaskGroup]:
        if isinstance(self._workflow_task_groups, Unset):
            raise NotPresentError(self, "workflow_task_groups")
        return self._workflow_task_groups

    @workflow_task_groups.setter
    def workflow_task_groups(self, value: List[WorkflowTaskGroup]) -> None:
        self._workflow_task_groups = value

    @workflow_task_groups.deleter
    def workflow_task_groups(self) -> None:
        self._workflow_task_groups = UNSET
