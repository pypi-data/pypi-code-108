from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_execution_origin_type import WorkflowTaskExecutionOriginType
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskExecutionOrigin")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskExecutionOrigin:
    """ The context into which a task was executed """

    _entry_id: Union[Unset, None, str] = UNSET
    _origin_modal_uuid: Union[Unset, None, str] = UNSET
    _type: Union[Unset, WorkflowTaskExecutionOriginType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("entry_id={}".format(repr(self._entry_id)))
        fields.append("origin_modal_uuid={}".format(repr(self._origin_modal_uuid)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskExecutionOrigin({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entry_id = self._entry_id
        origin_modal_uuid = self._origin_modal_uuid
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if entry_id is not UNSET:
            field_dict["entryId"] = entry_id
        if origin_modal_uuid is not UNSET:
            field_dict["originModalUuid"] = origin_modal_uuid
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_entry_id() -> Union[Unset, None, str]:
            entry_id = d.pop("entryId")
            return entry_id

        entry_id = get_entry_id() if "entryId" in d else cast(Union[Unset, None, str], UNSET)

        def get_origin_modal_uuid() -> Union[Unset, None, str]:
            origin_modal_uuid = d.pop("originModalUuid")
            return origin_modal_uuid

        origin_modal_uuid = (
            get_origin_modal_uuid() if "originModalUuid" in d else cast(Union[Unset, None, str], UNSET)
        )

        def get_type() -> Union[Unset, WorkflowTaskExecutionOriginType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = WorkflowTaskExecutionOriginType(_type)
                except ValueError:
                    type = WorkflowTaskExecutionOriginType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, WorkflowTaskExecutionOriginType], UNSET)

        workflow_task_execution_origin = cls(
            entry_id=entry_id,
            origin_modal_uuid=origin_modal_uuid,
            type=type,
        )

        workflow_task_execution_origin.additional_properties = d
        return workflow_task_execution_origin

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
    def entry_id(self) -> Optional[str]:
        if isinstance(self._entry_id, Unset):
            raise NotPresentError(self, "entry_id")
        return self._entry_id

    @entry_id.setter
    def entry_id(self, value: Optional[str]) -> None:
        self._entry_id = value

    @entry_id.deleter
    def entry_id(self) -> None:
        self._entry_id = UNSET

    @property
    def origin_modal_uuid(self) -> Optional[str]:
        if isinstance(self._origin_modal_uuid, Unset):
            raise NotPresentError(self, "origin_modal_uuid")
        return self._origin_modal_uuid

    @origin_modal_uuid.setter
    def origin_modal_uuid(self, value: Optional[str]) -> None:
        self._origin_modal_uuid = value

    @origin_modal_uuid.deleter
    def origin_modal_uuid(self) -> None:
        self._origin_modal_uuid = UNSET

    @property
    def type(self) -> WorkflowTaskExecutionOriginType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: WorkflowTaskExecutionOriginType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
