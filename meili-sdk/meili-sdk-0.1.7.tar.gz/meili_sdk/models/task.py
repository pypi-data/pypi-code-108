import typing as t

from meili_sdk.exceptions import MissingAttributesException
from meili_sdk.models.base import BaseModel


class Subtask(BaseModel):
    uuid: t.Optional[str] = None
    location: str
    robot_executed_at: t.Optional[str] = None
    executed_at: t.Optional[str] = None
    index: t.Optional[int] = None
    location_point: t.Optional[dict] = None


class Task(BaseModel):
    uuid: t.Optional[str] = None
    number: t.Optional[str] = None
    user: t.Optional[str] = None
    vehicle: t.Optional[str] = None
    task_status: t.Optional[str] = None
    vehicle_category: t.Optional[str] = None
    priority: bool = False
    team: str = None
    subtasks: t.List[t.Union[Subtask, str]]

    def __init__(self, **kwargs) -> None:
        subtasks = kwargs.pop("subtasks", None)

        if not subtasks:
            raise MissingAttributesException(self.__class__, ["subtasks"])

        subtask_objs = []
        for subtask in subtasks:
            subtask_objs.append(Subtask(**subtask))

        kwargs["subtasks"] = subtask_objs
        super().__init__(**kwargs)
