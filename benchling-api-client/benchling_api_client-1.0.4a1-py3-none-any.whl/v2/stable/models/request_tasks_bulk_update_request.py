from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.request_task_base import RequestTaskBase
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestTasksBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class RequestTasksBulkUpdateRequest:
    """A request body for bulk updating request tasks."""

    _tasks: List[RequestTaskBase]

    def __repr__(self):
        fields = []
        fields.append("tasks={}".format(repr(self._tasks)))
        return "RequestTasksBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        tasks = []
        for tasks_item_data in self._tasks:
            tasks_item = tasks_item_data.to_dict()

            tasks.append(tasks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "tasks": tasks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_tasks() -> List[RequestTaskBase]:
            tasks = []
            _tasks = d.pop("tasks")
            for tasks_item_data in _tasks:
                tasks_item = RequestTaskBase.from_dict(tasks_item_data)

                tasks.append(tasks_item)

            return tasks

        tasks = get_tasks() if "tasks" in d else cast(List[RequestTaskBase], UNSET)

        request_tasks_bulk_update_request = cls(
            tasks=tasks,
        )

        return request_tasks_bulk_update_request

    @property
    def tasks(self) -> List[RequestTaskBase]:
        """ The tasks to update """
        if isinstance(self._tasks, Unset):
            raise NotPresentError(self, "tasks")
        return self._tasks

    @tasks.setter
    def tasks(self, value: List[RequestTaskBase]) -> None:
        self._tasks = value
