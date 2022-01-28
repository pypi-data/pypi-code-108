from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_group_archive_reason import WorkflowTaskGroupArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskGroupsArchive")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskGroupsArchive:
    """  """

    _reason: WorkflowTaskGroupArchiveReason
    _workflow_task_group_ids: List[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("workflow_task_group_ids={}".format(repr(self._workflow_task_group_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskGroupsArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        reason = self._reason.value

        workflow_task_group_ids = self._workflow_task_group_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reason": reason,
                "workflowTaskGroupIds": workflow_task_group_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_reason() -> WorkflowTaskGroupArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = WorkflowTaskGroupArchiveReason(_reason)
            except ValueError:
                reason = WorkflowTaskGroupArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(WorkflowTaskGroupArchiveReason, UNSET)

        def get_workflow_task_group_ids() -> List[str]:
            workflow_task_group_ids = cast(List[str], d.pop("workflowTaskGroupIds"))

            return workflow_task_group_ids

        workflow_task_group_ids = (
            get_workflow_task_group_ids() if "workflowTaskGroupIds" in d else cast(List[str], UNSET)
        )

        workflow_task_groups_archive = cls(
            reason=reason,
            workflow_task_group_ids=workflow_task_group_ids,
        )

        workflow_task_groups_archive.additional_properties = d
        return workflow_task_groups_archive

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
    def reason(self) -> WorkflowTaskGroupArchiveReason:
        """The reason for archiving the provided workflow task groups. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: WorkflowTaskGroupArchiveReason) -> None:
        self._reason = value

    @property
    def workflow_task_group_ids(self) -> List[str]:
        if isinstance(self._workflow_task_group_ids, Unset):
            raise NotPresentError(self, "workflow_task_group_ids")
        return self._workflow_task_group_ids

    @workflow_task_group_ids.setter
    def workflow_task_group_ids(self, value: List[str]) -> None:
        self._workflow_task_group_ids = value
