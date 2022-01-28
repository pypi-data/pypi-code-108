import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskWriteBase")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskWriteBase:
    """  """

    _assignee_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _scheduled_on: Union[Unset, datetime.date] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("assignee_id={}".format(repr(self._assignee_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("scheduled_on={}".format(repr(self._scheduled_on)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskWriteBase({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assignee_id = self._assignee_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        scheduled_on: Union[Unset, str] = UNSET
        if not isinstance(self._scheduled_on, Unset):
            scheduled_on = self._scheduled_on.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assignee_id is not UNSET:
            field_dict["assigneeId"] = assignee_id
        if fields is not UNSET:
            field_dict["fields"] = fields
        if scheduled_on is not UNSET:
            field_dict["scheduledOn"] = scheduled_on

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_assignee_id() -> Union[Unset, str]:
            assignee_id = d.pop("assigneeId")
            return assignee_id

        assignee_id = get_assignee_id() if "assigneeId" in d else cast(Union[Unset, str], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_scheduled_on() -> Union[Unset, datetime.date]:
            scheduled_on: Union[Unset, datetime.date] = UNSET
            _scheduled_on = d.pop("scheduledOn")
            if _scheduled_on is not None and not isinstance(_scheduled_on, Unset):
                scheduled_on = isoparse(cast(str, _scheduled_on)).date()

            return scheduled_on

        scheduled_on = get_scheduled_on() if "scheduledOn" in d else cast(Union[Unset, datetime.date], UNSET)

        workflow_task_write_base = cls(
            assignee_id=assignee_id,
            fields=fields,
            scheduled_on=scheduled_on,
        )

        workflow_task_write_base.additional_properties = d
        return workflow_task_write_base

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
    def assignee_id(self) -> str:
        """ The id of the user assigned to the task """
        if isinstance(self._assignee_id, Unset):
            raise NotPresentError(self, "assignee_id")
        return self._assignee_id

    @assignee_id.setter
    def assignee_id(self, value: str) -> None:
        self._assignee_id = value

    @assignee_id.deleter
    def assignee_id(self) -> None:
        self._assignee_id = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def scheduled_on(self) -> datetime.date:
        """ The date on which the task is scheduled to be executed """
        if isinstance(self._scheduled_on, Unset):
            raise NotPresentError(self, "scheduled_on")
        return self._scheduled_on

    @scheduled_on.setter
    def scheduled_on(self, value: datetime.date) -> None:
        self._scheduled_on = value

    @scheduled_on.deleter
    def scheduled_on(self) -> None:
        self._scheduled_on = UNSET
