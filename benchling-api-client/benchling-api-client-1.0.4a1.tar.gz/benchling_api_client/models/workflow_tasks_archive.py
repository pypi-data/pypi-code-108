from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_archive_reason import WorkflowTaskArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTasksArchive")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTasksArchive:
    """  """

    _reason: WorkflowTaskArchiveReason
    _workflow_task_ids: List[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("workflow_task_ids={}".format(repr(self._workflow_task_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTasksArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        reason = self._reason.value

        workflow_task_ids = self._workflow_task_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reason": reason,
                "workflowTaskIds": workflow_task_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_reason() -> WorkflowTaskArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = WorkflowTaskArchiveReason(_reason)
            except ValueError:
                reason = WorkflowTaskArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(WorkflowTaskArchiveReason, UNSET)

        def get_workflow_task_ids() -> List[str]:
            workflow_task_ids = cast(List[str], d.pop("workflowTaskIds"))

            return workflow_task_ids

        workflow_task_ids = get_workflow_task_ids() if "workflowTaskIds" in d else cast(List[str], UNSET)

        workflow_tasks_archive = cls(
            reason=reason,
            workflow_task_ids=workflow_task_ids,
        )

        workflow_tasks_archive.additional_properties = d
        return workflow_tasks_archive

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
    def reason(self) -> WorkflowTaskArchiveReason:
        """The reason for archiving the provided workflow tasks. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: WorkflowTaskArchiveReason) -> None:
        self._reason = value

    @property
    def workflow_task_ids(self) -> List[str]:
        if isinstance(self._workflow_task_ids, Unset):
            raise NotPresentError(self, "workflow_task_ids")
        return self._workflow_task_ids

    @workflow_task_ids.setter
    def workflow_task_ids(self, value: List[str]) -> None:
        self._workflow_task_ids = value
