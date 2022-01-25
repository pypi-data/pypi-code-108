from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_status import WorkflowTaskStatus
from ..models.workflow_task_status_lifecycle_transition import WorkflowTaskStatusLifecycleTransition
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskStatusLifecycle")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskStatusLifecycle:
    """  """

    _id: Union[Unset, str] = UNSET
    _initial_status: Union[Unset, WorkflowTaskStatus] = UNSET
    _name: Union[Unset, str] = UNSET
    _statuses: Union[Unset, List[WorkflowTaskStatus]] = UNSET
    _transitions: Union[Unset, List[WorkflowTaskStatusLifecycleTransition]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("initial_status={}".format(repr(self._initial_status)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("statuses={}".format(repr(self._statuses)))
        fields.append("transitions={}".format(repr(self._transitions)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskStatusLifecycle({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        initial_status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._initial_status, Unset):
            initial_status = self._initial_status.to_dict()

        name = self._name
        statuses: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._statuses, Unset):
            statuses = []
            for statuses_item_data in self._statuses:
                statuses_item = statuses_item_data.to_dict()

                statuses.append(statuses_item)

        transitions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._transitions, Unset):
            transitions = []
            for transitions_item_data in self._transitions:
                transitions_item = transitions_item_data.to_dict()

                transitions.append(transitions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if initial_status is not UNSET:
            field_dict["initialStatus"] = initial_status
        if name is not UNSET:
            field_dict["name"] = name
        if statuses is not UNSET:
            field_dict["statuses"] = statuses
        if transitions is not UNSET:
            field_dict["transitions"] = transitions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_initial_status() -> Union[Unset, WorkflowTaskStatus]:
            initial_status: Union[Unset, WorkflowTaskStatus] = UNSET
            _initial_status = d.pop("initialStatus")
            if not isinstance(_initial_status, Unset):
                initial_status = WorkflowTaskStatus.from_dict(_initial_status)

            return initial_status

        initial_status = (
            get_initial_status() if "initialStatus" in d else cast(Union[Unset, WorkflowTaskStatus], UNSET)
        )

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_statuses() -> Union[Unset, List[WorkflowTaskStatus]]:
            statuses = []
            _statuses = d.pop("statuses")
            for statuses_item_data in _statuses or []:
                statuses_item = WorkflowTaskStatus.from_dict(statuses_item_data)

                statuses.append(statuses_item)

            return statuses

        statuses = get_statuses() if "statuses" in d else cast(Union[Unset, List[WorkflowTaskStatus]], UNSET)

        def get_transitions() -> Union[Unset, List[WorkflowTaskStatusLifecycleTransition]]:
            transitions = []
            _transitions = d.pop("transitions")
            for transitions_item_data in _transitions or []:
                transitions_item = WorkflowTaskStatusLifecycleTransition.from_dict(transitions_item_data)

                transitions.append(transitions_item)

            return transitions

        transitions = (
            get_transitions()
            if "transitions" in d
            else cast(Union[Unset, List[WorkflowTaskStatusLifecycleTransition]], UNSET)
        )

        workflow_task_status_lifecycle = cls(
            id=id,
            initial_status=initial_status,
            name=name,
            statuses=statuses,
            transitions=transitions,
        )

        workflow_task_status_lifecycle.additional_properties = d
        return workflow_task_status_lifecycle

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
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def initial_status(self) -> WorkflowTaskStatus:
        if isinstance(self._initial_status, Unset):
            raise NotPresentError(self, "initial_status")
        return self._initial_status

    @initial_status.setter
    def initial_status(self, value: WorkflowTaskStatus) -> None:
        self._initial_status = value

    @initial_status.deleter
    def initial_status(self) -> None:
        self._initial_status = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def statuses(self) -> List[WorkflowTaskStatus]:
        if isinstance(self._statuses, Unset):
            raise NotPresentError(self, "statuses")
        return self._statuses

    @statuses.setter
    def statuses(self, value: List[WorkflowTaskStatus]) -> None:
        self._statuses = value

    @statuses.deleter
    def statuses(self) -> None:
        self._statuses = UNSET

    @property
    def transitions(self) -> List[WorkflowTaskStatusLifecycleTransition]:
        if isinstance(self._transitions, Unset):
            raise NotPresentError(self, "transitions")
        return self._transitions

    @transitions.setter
    def transitions(self, value: List[WorkflowTaskStatusLifecycleTransition]) -> None:
        self._transitions = value

    @transitions.deleter
    def transitions(self) -> None:
        self._transitions = UNSET
