from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_relationship_relationship_type import WorkflowTaskRelationshipRelationshipType
from ..models.workflow_task_summary import WorkflowTaskSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskRelationship")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskRelationship:
    """Describes a relationship between two workflow tasks"""

    _from_task: Union[Unset, WorkflowTaskSummary] = UNSET
    _id: Union[Unset, str] = UNSET
    _relationship_type: Union[Unset, WorkflowTaskRelationshipRelationshipType] = UNSET
    _to_task: Union[Unset, WorkflowTaskSummary] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("from_task={}".format(repr(self._from_task)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("relationship_type={}".format(repr(self._relationship_type)))
        fields.append("to_task={}".format(repr(self._to_task)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskRelationship({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        from_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._from_task, Unset):
            from_task = self._from_task.to_dict()

        id = self._id
        relationship_type: Union[Unset, int] = UNSET
        if not isinstance(self._relationship_type, Unset):
            relationship_type = self._relationship_type.value

        to_task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._to_task, Unset):
            to_task = self._to_task.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_task is not UNSET:
            field_dict["fromTask"] = from_task
        if id is not UNSET:
            field_dict["id"] = id
        if relationship_type is not UNSET:
            field_dict["relationshipType"] = relationship_type
        if to_task is not UNSET:
            field_dict["toTask"] = to_task

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        from_task: Union[Unset, WorkflowTaskSummary] = UNSET
        _from_task = d.pop("fromTask", UNSET)
        if not isinstance(_from_task, Unset):
            from_task = WorkflowTaskSummary.from_dict(_from_task)

        id = d.pop("id", UNSET)

        relationship_type = None
        _relationship_type = d.pop("relationshipType", UNSET)
        if _relationship_type is not None and _relationship_type is not UNSET:
            try:
                relationship_type = WorkflowTaskRelationshipRelationshipType(_relationship_type)
            except ValueError:
                relationship_type = WorkflowTaskRelationshipRelationshipType.of_unknown(_relationship_type)

        to_task: Union[Unset, WorkflowTaskSummary] = UNSET
        _to_task = d.pop("toTask", UNSET)
        if not isinstance(_to_task, Unset):
            to_task = WorkflowTaskSummary.from_dict(_to_task)

        workflow_task_relationship = cls(
            from_task=from_task,
            id=id,
            relationship_type=relationship_type,
            to_task=to_task,
        )

        workflow_task_relationship.additional_properties = d
        return workflow_task_relationship

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
    def from_task(self) -> WorkflowTaskSummary:
        if isinstance(self._from_task, Unset):
            raise NotPresentError(self, "from_task")
        return self._from_task

    @from_task.setter
    def from_task(self, value: WorkflowTaskSummary) -> None:
        self._from_task = value

    @from_task.deleter
    def from_task(self) -> None:
        self._from_task = UNSET

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
    def relationship_type(self) -> WorkflowTaskRelationshipRelationshipType:
        if isinstance(self._relationship_type, Unset):
            raise NotPresentError(self, "relationship_type")
        return self._relationship_type

    @relationship_type.setter
    def relationship_type(self, value: WorkflowTaskRelationshipRelationshipType) -> None:
        self._relationship_type = value

    @relationship_type.deleter
    def relationship_type(self) -> None:
        self._relationship_type = UNSET

    @property
    def to_task(self) -> WorkflowTaskSummary:
        if isinstance(self._to_task, Unset):
            raise NotPresentError(self, "to_task")
        return self._to_task

    @to_task.setter
    def to_task(self, value: WorkflowTaskSummary) -> None:
        self._to_task = value

    @to_task.deleter
    def to_task(self) -> None:
        self._to_task = UNSET
