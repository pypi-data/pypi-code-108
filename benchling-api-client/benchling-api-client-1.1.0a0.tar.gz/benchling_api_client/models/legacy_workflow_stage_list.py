from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.legacy_workflow_stage import LegacyWorkflowStage
from ..types import UNSET, Unset

T = TypeVar("T", bound="LegacyWorkflowStageList")


@attr.s(auto_attribs=True, repr=False)
class LegacyWorkflowStageList:
    """  """

    _workflow_stages: Union[Unset, List[LegacyWorkflowStage]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_stages={}".format(repr(self._workflow_stages)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LegacyWorkflowStageList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_stages: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_stages, Unset):
            workflow_stages = []
            for workflow_stages_item_data in self._workflow_stages:
                workflow_stages_item = workflow_stages_item_data.to_dict()

                workflow_stages.append(workflow_stages_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if workflow_stages is not UNSET:
            field_dict["workflowStages"] = workflow_stages

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_workflow_stages() -> Union[Unset, List[LegacyWorkflowStage]]:
            workflow_stages = []
            _workflow_stages = d.pop("workflowStages")
            for workflow_stages_item_data in _workflow_stages or []:
                workflow_stages_item = LegacyWorkflowStage.from_dict(workflow_stages_item_data)

                workflow_stages.append(workflow_stages_item)

            return workflow_stages

        workflow_stages = (
            get_workflow_stages()
            if "workflowStages" in d
            else cast(Union[Unset, List[LegacyWorkflowStage]], UNSET)
        )

        legacy_workflow_stage_list = cls(
            workflow_stages=workflow_stages,
        )

        legacy_workflow_stage_list.additional_properties = d
        return legacy_workflow_stage_list

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
    def workflow_stages(self) -> List[LegacyWorkflowStage]:
        if isinstance(self._workflow_stages, Unset):
            raise NotPresentError(self, "workflow_stages")
        return self._workflow_stages

    @workflow_stages.setter
    def workflow_stages(self, value: List[LegacyWorkflowStage]) -> None:
        self._workflow_stages = value

    @workflow_stages.deleter
    def workflow_stages(self) -> None:
        self._workflow_stages = UNSET
