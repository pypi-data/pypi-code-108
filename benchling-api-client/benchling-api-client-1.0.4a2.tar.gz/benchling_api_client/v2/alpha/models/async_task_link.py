from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="AsyncTaskLink")


@attr.s(auto_attribs=True, repr=False)
class AsyncTaskLink:
    """  """

    _task_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("task_id={}".format(repr(self._task_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AsyncTaskLink({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        task_id = self._task_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if task_id is not UNSET:
            field_dict["taskId"] = task_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_task_id() -> Union[Unset, str]:
            task_id = d.pop("taskId")
            return task_id

        task_id = get_task_id() if "taskId" in d else cast(Union[Unset, str], UNSET)

        async_task_link = cls(
            task_id=task_id,
        )

        async_task_link.additional_properties = d
        return async_task_link

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
    def task_id(self) -> str:
        if isinstance(self._task_id, Unset):
            raise NotPresentError(self, "task_id")
        return self._task_id

    @task_id.setter
    def task_id(self, value: str) -> None:
        self._task_id = value

    @task_id.deleter
    def task_id(self) -> None:
        self._task_id = UNSET
