from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_output import WorkflowOutput
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutputsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutputsPaginatedList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _workflow_outputs: Union[Unset, List[WorkflowOutput]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("workflow_outputs={}".format(repr(self._workflow_outputs)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutputsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        workflow_outputs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._workflow_outputs, Unset):
            workflow_outputs = []
            for workflow_outputs_item_data in self._workflow_outputs:
                workflow_outputs_item = workflow_outputs_item_data.to_dict()

                workflow_outputs.append(workflow_outputs_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if workflow_outputs is not UNSET:
            field_dict["workflowOutputs"] = workflow_outputs

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_outputs() -> Union[Unset, List[WorkflowOutput]]:
            workflow_outputs = []
            _workflow_outputs = d.pop("workflowOutputs")
            for workflow_outputs_item_data in _workflow_outputs or []:
                workflow_outputs_item = WorkflowOutput.from_dict(workflow_outputs_item_data)

                workflow_outputs.append(workflow_outputs_item)

            return workflow_outputs

        workflow_outputs = (
            get_workflow_outputs()
            if "workflowOutputs" in d
            else cast(Union[Unset, List[WorkflowOutput]], UNSET)
        )

        workflow_outputs_paginated_list = cls(
            next_token=next_token,
            workflow_outputs=workflow_outputs,
        )

        workflow_outputs_paginated_list.additional_properties = d
        return workflow_outputs_paginated_list

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
    def workflow_outputs(self) -> List[WorkflowOutput]:
        if isinstance(self._workflow_outputs, Unset):
            raise NotPresentError(self, "workflow_outputs")
        return self._workflow_outputs

    @workflow_outputs.setter
    def workflow_outputs(self, value: List[WorkflowOutput]) -> None:
        self._workflow_outputs = value

    @workflow_outputs.deleter
    def workflow_outputs(self) -> None:
        self._workflow_outputs = UNSET
