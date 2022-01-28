from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_status import WorkflowTaskStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskStatusLifecycleTransition")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskStatusLifecycleTransition:
    """  """

    _from_: Union[Unset, WorkflowTaskStatus] = UNSET
    _to: Union[Unset, WorkflowTaskStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("from_={}".format(repr(self._from_)))
        fields.append("to={}".format(repr(self._to)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskStatusLifecycleTransition({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        from_: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._from_, Unset):
            from_ = self._from_.to_dict()

        to: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._to, Unset):
            to = self._to.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_ is not UNSET:
            field_dict["from"] = from_
        if to is not UNSET:
            field_dict["to"] = to

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_from_() -> Union[Unset, WorkflowTaskStatus]:
            from_: Union[Unset, WorkflowTaskStatus] = UNSET
            _from_ = d.pop("from")
            if not isinstance(_from_, Unset):
                from_ = WorkflowTaskStatus.from_dict(_from_)

            return from_

        from_ = get_from_() if "from" in d else cast(Union[Unset, WorkflowTaskStatus], UNSET)

        def get_to() -> Union[Unset, WorkflowTaskStatus]:
            to: Union[Unset, WorkflowTaskStatus] = UNSET
            _to = d.pop("to")
            if not isinstance(_to, Unset):
                to = WorkflowTaskStatus.from_dict(_to)

            return to

        to = get_to() if "to" in d else cast(Union[Unset, WorkflowTaskStatus], UNSET)

        workflow_task_status_lifecycle_transition = cls(
            from_=from_,
            to=to,
        )

        workflow_task_status_lifecycle_transition.additional_properties = d
        return workflow_task_status_lifecycle_transition

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
    def from_(self) -> WorkflowTaskStatus:
        if isinstance(self._from_, Unset):
            raise NotPresentError(self, "from_")
        return self._from_

    @from_.setter
    def from_(self, value: WorkflowTaskStatus) -> None:
        self._from_ = value

    @from_.deleter
    def from_(self) -> None:
        self._from_ = UNSET

    @property
    def to(self) -> WorkflowTaskStatus:
        if isinstance(self._to, Unset):
            raise NotPresentError(self, "to")
        return self._to

    @to.setter
    def to(self, value: WorkflowTaskStatus) -> None:
        self._to = value

    @to.deleter
    def to(self) -> None:
        self._to = UNSET
