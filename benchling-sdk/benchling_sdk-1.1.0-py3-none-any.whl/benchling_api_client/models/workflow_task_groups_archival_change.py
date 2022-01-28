from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskGroupsArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskGroupsArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type"""

    _workflow_task_group_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_task_group_ids={}".format(repr(self._workflow_task_group_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskGroupsArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_task_group_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_task_group_ids, Unset):
            workflow_task_group_ids = self._workflow_task_group_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if workflow_task_group_ids is not UNSET:
            field_dict["workflowTaskGroupIds"] = workflow_task_group_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_workflow_task_group_ids() -> Union[Unset, List[str]]:
            workflow_task_group_ids = cast(List[str], d.pop("workflowTaskGroupIds"))

            return workflow_task_group_ids

        workflow_task_group_ids = (
            get_workflow_task_group_ids()
            if "workflowTaskGroupIds" in d
            else cast(Union[Unset, List[str]], UNSET)
        )

        workflow_task_groups_archival_change = cls(
            workflow_task_group_ids=workflow_task_group_ids,
        )

        workflow_task_groups_archival_change.additional_properties = d
        return workflow_task_groups_archival_change

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
    def workflow_task_group_ids(self) -> List[str]:
        if isinstance(self._workflow_task_group_ids, Unset):
            raise NotPresentError(self, "workflow_task_group_ids")
        return self._workflow_task_group_ids

    @workflow_task_group_ids.setter
    def workflow_task_group_ids(self, value: List[str]) -> None:
        self._workflow_task_group_ids = value

    @workflow_task_group_ids.deleter
    def workflow_task_group_ids(self) -> None:
        self._workflow_task_group_ids = UNSET
