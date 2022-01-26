from typing import Any

from arrlio.models import Event, TaskInstance, TaskResult
from arrlio.serializer import base


class Nop(base.Serializer):
    def dumps_task_instance(self, task_instance: TaskInstance, **kwds) -> TaskInstance:
        return task_instance

    def loads_task_instance(self, data: TaskInstance) -> TaskInstance:
        return data

    def dumps_task_result(self, result: TaskResult, **kwds) -> TaskResult:
        return result

    def loads_task_result(self, data: TaskResult) -> TaskResult:
        return data

    def dumps_event(self, event: Event, **kwds) -> Event:
        return event

    def loads_event(self, data: Event) -> Event:
        return data

    def dumps(self, data: Any, **kwds) -> Any:
        return data

    def loads(self, data: Any) -> Any:
        return data
