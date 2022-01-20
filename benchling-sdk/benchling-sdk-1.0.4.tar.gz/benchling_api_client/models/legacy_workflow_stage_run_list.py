from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.legacy_workflow_stage_run import LegacyWorkflowStageRun
from ..types import UNSET, Unset

T = TypeVar("T", bound="LegacyWorkflowStageRunList")


@attr.s(auto_attribs=True, repr=False)
class LegacyWorkflowStageRunList:
    """  """

    _workflow_stage_runs: Union[Unset, List[LegacyWorkflowStageRun]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_stage_runs={}".format(repr(self._workflow_stage_runs)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LegacyWorkflowStageRunList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_stage_runs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_stage_runs, Unset):
            workflow_stage_runs = []
            for workflow_stage_runs_item_data in self._workflow_stage_runs:
                workflow_stage_runs_item = workflow_stage_runs_item_data.to_dict()

                workflow_stage_runs.append(workflow_stage_runs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if workflow_stage_runs is not UNSET:
            field_dict["workflowStageRuns"] = workflow_stage_runs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_workflow_stage_runs() -> Union[Unset, List[LegacyWorkflowStageRun]]:
            workflow_stage_runs = []
            _workflow_stage_runs = d.pop("workflowStageRuns")
            for workflow_stage_runs_item_data in _workflow_stage_runs or []:
                workflow_stage_runs_item = LegacyWorkflowStageRun.from_dict(workflow_stage_runs_item_data)

                workflow_stage_runs.append(workflow_stage_runs_item)

            return workflow_stage_runs

        workflow_stage_runs = (
            get_workflow_stage_runs()
            if "workflowStageRuns" in d
            else cast(Union[Unset, List[LegacyWorkflowStageRun]], UNSET)
        )

        legacy_workflow_stage_run_list = cls(
            workflow_stage_runs=workflow_stage_runs,
        )

        legacy_workflow_stage_run_list.additional_properties = d
        return legacy_workflow_stage_run_list

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
    def workflow_stage_runs(self) -> List[LegacyWorkflowStageRun]:
        if isinstance(self._workflow_stage_runs, Unset):
            raise NotPresentError(self, "workflow_stage_runs")
        return self._workflow_stage_runs

    @workflow_stage_runs.setter
    def workflow_stage_runs(self, value: List[LegacyWorkflowStageRun]) -> None:
        self._workflow_stage_runs = value

    @workflow_stage_runs.deleter
    def workflow_stage_runs(self) -> None:
        self._workflow_stage_runs = UNSET
