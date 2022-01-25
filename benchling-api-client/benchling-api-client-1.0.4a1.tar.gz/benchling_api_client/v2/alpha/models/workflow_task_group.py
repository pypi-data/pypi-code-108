from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.creation_origin import CreationOrigin
from ..models.user_summary import UserSummary
from ..models.workflow_task_group_execution_type import WorkflowTaskGroupExecutionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskGroup")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskGroup:
    """  """

    _execution_type: Union[Unset, WorkflowTaskGroupExecutionType] = UNSET
    _creation_origin: Union[Unset, CreationOrigin] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("execution_type={}".format(repr(self._execution_type)))
        fields.append("creation_origin={}".format(repr(self._creation_origin)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskGroup({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        execution_type: Union[Unset, int] = UNSET
        if not isinstance(self._execution_type, Unset):
            execution_type = self._execution_type.value

        creation_origin: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creation_origin, Unset):
            creation_origin = self._creation_origin.to_dict()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if execution_type is not UNSET:
            field_dict["executionType"] = execution_type
        if creation_origin is not UNSET:
            field_dict["creationOrigin"] = creation_origin
        if creator is not UNSET:
            field_dict["creator"] = creator

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_execution_type() -> Union[Unset, WorkflowTaskGroupExecutionType]:
            execution_type = None
            _execution_type = d.pop("executionType")
            if _execution_type is not None and _execution_type is not UNSET:
                try:
                    execution_type = WorkflowTaskGroupExecutionType(_execution_type)
                except ValueError:
                    execution_type = WorkflowTaskGroupExecutionType.of_unknown(_execution_type)

            return execution_type

        execution_type = (
            get_execution_type()
            if "executionType" in d
            else cast(Union[Unset, WorkflowTaskGroupExecutionType], UNSET)
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

        workflow_task_group = cls(
            execution_type=execution_type,
            creation_origin=creation_origin,
            creator=creator,
        )

        workflow_task_group.additional_properties = d
        return workflow_task_group

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
    def execution_type(self) -> WorkflowTaskGroupExecutionType:
        """ The method by which the workflow is executed """
        if isinstance(self._execution_type, Unset):
            raise NotPresentError(self, "execution_type")
        return self._execution_type

    @execution_type.setter
    def execution_type(self, value: WorkflowTaskGroupExecutionType) -> None:
        self._execution_type = value

    @execution_type.deleter
    def execution_type(self) -> None:
        self._execution_type = UNSET

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
