from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.creation_origin import CreationOrigin
from ..models.user_summary import UserSummary
from ..models.workflow_task_execution_origin import WorkflowTaskExecutionOrigin
from ..models.workflow_task_execution_type import WorkflowTaskExecutionType
from ..models.workflow_task_summary import WorkflowTaskSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTask")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTask:
    """  """

    _execution_type: Union[Unset, WorkflowTaskExecutionType] = UNSET
    _assignee: Union[Unset, None, UserSummary] = UNSET
    _cloned_from: Union[Unset, None, WorkflowTaskSummary] = UNSET
    _creation_origin: Union[Unset, CreationOrigin] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _execution_origin: Union[Unset, None, WorkflowTaskExecutionOrigin] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("execution_type={}".format(repr(self._execution_type)))
        fields.append("assignee={}".format(repr(self._assignee)))
        fields.append("cloned_from={}".format(repr(self._cloned_from)))
        fields.append("creation_origin={}".format(repr(self._creation_origin)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("execution_origin={}".format(repr(self._execution_origin)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTask({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        execution_type: Union[Unset, int] = UNSET
        if not isinstance(self._execution_type, Unset):
            execution_type = self._execution_type.value

        assignee: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._assignee, Unset):
            assignee = self._assignee.to_dict() if self._assignee else None

        cloned_from: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._cloned_from, Unset):
            cloned_from = self._cloned_from.to_dict() if self._cloned_from else None

        creation_origin: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creation_origin, Unset):
            creation_origin = self._creation_origin.to_dict()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        execution_origin: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._execution_origin, Unset):
            execution_origin = self._execution_origin.to_dict() if self._execution_origin else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if execution_type is not UNSET:
            field_dict["executionType"] = execution_type
        if assignee is not UNSET:
            field_dict["assignee"] = assignee
        if cloned_from is not UNSET:
            field_dict["clonedFrom"] = cloned_from
        if creation_origin is not UNSET:
            field_dict["creationOrigin"] = creation_origin
        if creator is not UNSET:
            field_dict["creator"] = creator
        if execution_origin is not UNSET:
            field_dict["executionOrigin"] = execution_origin

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_execution_type() -> Union[Unset, WorkflowTaskExecutionType]:
            execution_type = None
            _execution_type = d.pop("executionType")
            if _execution_type is not None and _execution_type is not UNSET:
                try:
                    execution_type = WorkflowTaskExecutionType(_execution_type)
                except ValueError:
                    execution_type = WorkflowTaskExecutionType.of_unknown(_execution_type)

            return execution_type

        execution_type = (
            get_execution_type()
            if "executionType" in d
            else cast(Union[Unset, WorkflowTaskExecutionType], UNSET)
        )

        def get_assignee() -> Union[Unset, None, UserSummary]:
            assignee = None
            _assignee = d.pop("assignee")
            if _assignee is not None and not isinstance(_assignee, Unset):
                assignee = UserSummary.from_dict(_assignee)

            return assignee

        assignee = get_assignee() if "assignee" in d else cast(Union[Unset, None, UserSummary], UNSET)

        def get_cloned_from() -> Union[Unset, None, WorkflowTaskSummary]:
            cloned_from = None
            _cloned_from = d.pop("clonedFrom")
            if _cloned_from is not None and not isinstance(_cloned_from, Unset):
                cloned_from = WorkflowTaskSummary.from_dict(_cloned_from)

            return cloned_from

        cloned_from = (
            get_cloned_from() if "clonedFrom" in d else cast(Union[Unset, None, WorkflowTaskSummary], UNSET)
        )

        def get_creation_origin() -> Union[Unset, CreationOrigin]:
            creation_origin: Union[Unset, CreationOrigin] = UNSET
            _creation_origin = d.pop("creationOrigin")
            if not isinstance(_creation_origin, Unset):
                creation_origin = CreationOrigin.from_dict(_creation_origin)

            return creation_origin

        creation_origin = (
            get_creation_origin() if "creationOrigin" in d else cast(Union[Unset, CreationOrigin], UNSET)
        )

        def get_creator() -> Union[Unset, UserSummary]:
            creator: Union[Unset, UserSummary] = UNSET
            _creator = d.pop("creator")
            if not isinstance(_creator, Unset):
                creator = UserSummary.from_dict(_creator)

            return creator

        creator = get_creator() if "creator" in d else cast(Union[Unset, UserSummary], UNSET)

        def get_execution_origin() -> Union[Unset, None, WorkflowTaskExecutionOrigin]:
            execution_origin = None
            _execution_origin = d.pop("executionOrigin")
            if _execution_origin is not None and not isinstance(_execution_origin, Unset):
                execution_origin = WorkflowTaskExecutionOrigin.from_dict(_execution_origin)

            return execution_origin

        execution_origin = (
            get_execution_origin()
            if "executionOrigin" in d
            else cast(Union[Unset, None, WorkflowTaskExecutionOrigin], UNSET)
        )

        workflow_task = cls(
            execution_type=execution_type,
            assignee=assignee,
            cloned_from=cloned_from,
            creation_origin=creation_origin,
            creator=creator,
            execution_origin=execution_origin,
        )

        workflow_task.additional_properties = d
        return workflow_task

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
    def execution_type(self) -> WorkflowTaskExecutionType:
        """ The method by which the task of the workflow is executed """
        if isinstance(self._execution_type, Unset):
            raise NotPresentError(self, "execution_type")
        return self._execution_type

    @execution_type.setter
    def execution_type(self, value: WorkflowTaskExecutionType) -> None:
        self._execution_type = value

    @execution_type.deleter
    def execution_type(self) -> None:
        self._execution_type = UNSET

    @property
    def assignee(self) -> Optional[UserSummary]:
        if isinstance(self._assignee, Unset):
            raise NotPresentError(self, "assignee")
        return self._assignee

    @assignee.setter
    def assignee(self, value: Optional[UserSummary]) -> None:
        self._assignee = value

    @assignee.deleter
    def assignee(self) -> None:
        self._assignee = UNSET

    @property
    def cloned_from(self) -> Optional[WorkflowTaskSummary]:
        if isinstance(self._cloned_from, Unset):
            raise NotPresentError(self, "cloned_from")
        return self._cloned_from

    @cloned_from.setter
    def cloned_from(self, value: Optional[WorkflowTaskSummary]) -> None:
        self._cloned_from = value

    @cloned_from.deleter
    def cloned_from(self) -> None:
        self._cloned_from = UNSET

    @property
    def creation_origin(self) -> CreationOrigin:
        if isinstance(self._creation_origin, Unset):
            raise NotPresentError(self, "creation_origin")
        return self._creation_origin

    @creation_origin.setter
    def creation_origin(self, value: CreationOrigin) -> None:
        self._creation_origin = value

    @creation_origin.deleter
    def creation_origin(self) -> None:
        self._creation_origin = UNSET

    @property
    def creator(self) -> UserSummary:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

    @property
    def execution_origin(self) -> Optional[WorkflowTaskExecutionOrigin]:
        """ The context into which a task was executed """
        if isinstance(self._execution_origin, Unset):
            raise NotPresentError(self, "execution_origin")
        return self._execution_origin

    @execution_origin.setter
    def execution_origin(self, value: Optional[WorkflowTaskExecutionOrigin]) -> None:
        self._execution_origin = value

    @execution_origin.deleter
    def execution_origin(self) -> None:
        self._execution_origin = UNSET
