from typing import Any, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="UserTaskStatus")


@attr.s(auto_attribs=True)
class UserTaskStatus:
    """  """

    num_fire_and_forget_tasks: int
    num_unfinished_run_tasks: int
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        num_fire_and_forget_tasks = self.num_fire_and_forget_tasks
        num_unfinished_run_tasks = self.num_unfinished_run_tasks

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "numFireAndForgetTasks": num_fire_and_forget_tasks,
                "numUnfinishedRunTasks": num_unfinished_run_tasks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        num_fire_and_forget_tasks = d.pop("numFireAndForgetTasks")

        num_unfinished_run_tasks = d.pop("numUnfinishedRunTasks")

        user_task_status = cls(
            num_fire_and_forget_tasks=num_fire_and_forget_tasks,
            num_unfinished_run_tasks=num_unfinished_run_tasks,
        )

        user_task_status.additional_properties = d
        return user_task_status

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
