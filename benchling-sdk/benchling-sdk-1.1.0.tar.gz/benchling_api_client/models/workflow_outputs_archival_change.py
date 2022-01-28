from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutputsArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutputsArchivalChange:
    """IDs of all items that were archived or unarchived, grouped by resource type"""

    _workflow_output_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_output_ids={}".format(repr(self._workflow_output_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutputsArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_output_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_output_ids, Unset):
            workflow_output_ids = self._workflow_output_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if workflow_output_ids is not UNSET:
            field_dict["workflowOutputIds"] = workflow_output_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_workflow_output_ids() -> Union[Unset, List[str]]:
            workflow_output_ids = cast(List[str], d.pop("workflowOutputIds"))

            return workflow_output_ids

        workflow_output_ids = (
            get_workflow_output_ids() if "workflowOutputIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        workflow_outputs_archival_change = cls(
            workflow_output_ids=workflow_output_ids,
        )

        workflow_outputs_archival_change.additional_properties = d
        return workflow_outputs_archival_change

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
    def workflow_output_ids(self) -> List[str]:
        if isinstance(self._workflow_output_ids, Unset):
            raise NotPresentError(self, "workflow_output_ids")
        return self._workflow_output_ids

    @workflow_output_ids.setter
    def workflow_output_ids(self, value: List[str]) -> None:
        self._workflow_output_ids = value

    @workflow_output_ids.deleter
    def workflow_output_ids(self) -> None:
        self._workflow_output_ids = UNSET
