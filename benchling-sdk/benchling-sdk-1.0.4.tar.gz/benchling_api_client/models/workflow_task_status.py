from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_status_status_type import WorkflowTaskStatusStatusType
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskStatus")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskStatus:
    """  """

    _display_name: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _status_type: Union[Unset, WorkflowTaskStatusStatusType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("display_name={}".format(repr(self._display_name)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("status_type={}".format(repr(self._status_type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskStatus({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        display_name = self._display_name
        id = self._id
        status_type: Union[Unset, int] = UNSET
        if not isinstance(self._status_type, Unset):
            status_type = self._status_type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if id is not UNSET:
            field_dict["id"] = id
        if status_type is not UNSET:
            field_dict["statusType"] = status_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_display_name() -> Union[Unset, str]:
            display_name = d.pop("displayName")
            return display_name

        display_name = get_display_name() if "displayName" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_status_type() -> Union[Unset, WorkflowTaskStatusStatusType]:
            status_type = None
            _status_type = d.pop("statusType")
            if _status_type is not None and _status_type is not UNSET:
                try:
                    status_type = WorkflowTaskStatusStatusType(_status_type)
                except ValueError:
                    status_type = WorkflowTaskStatusStatusType.of_unknown(_status_type)

            return status_type

        status_type = (
            get_status_type()
            if "statusType" in d
            else cast(Union[Unset, WorkflowTaskStatusStatusType], UNSET)
        )

        workflow_task_status = cls(
            display_name=display_name,
            id=id,
            status_type=status_type,
        )

        workflow_task_status.additional_properties = d
        return workflow_task_status

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
    def display_name(self) -> str:
        """ The status label """
        if isinstance(self._display_name, Unset):
            raise NotPresentError(self, "display_name")
        return self._display_name

    @display_name.setter
    def display_name(self, value: str) -> None:
        self._display_name = value

    @display_name.deleter
    def display_name(self) -> None:
        self._display_name = UNSET

    @property
    def id(self) -> str:
        """ The ID of the workflow task status """
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
    def status_type(self) -> WorkflowTaskStatusStatusType:
        """ The status type """
        if isinstance(self._status_type, Unset):
            raise NotPresentError(self, "status_type")
        return self._status_type

    @status_type.setter
    def status_type(self, value: WorkflowTaskStatusStatusType) -> None:
        self._status_type = value

    @status_type.deleter
    def status_type(self) -> None:
        self._status_type = UNSET
