import abc
from typing import Any, Union

from arrlio.models import Event, TaskInstance, TaskResult


class Serializer(abc.ABC):
    @abc.abstractmethod
    def dumps_task_instance(self, task_instance: TaskInstance, **kwds) -> Union[bytes, TaskInstance]:
        pass

    @abc.abstractmethod
    def loads_task_instance(self, data: Union[bytes, TaskInstance]) -> TaskInstance:
        pass

    @abc.abstractmethod
    def dumps_task_result(self, result: TaskResult, **kwds) -> Union[bytes, TaskResult]:
        pass

    @abc.abstractmethod
    def loads_task_result(self, data: Union[bytes, TaskResult]) -> TaskResult:
        pass

    @abc.abstractmethod
    def dumps_event(self, event: Event, **kwds) -> Union[bytes, Event]:
        pass

    @abc.abstractmethod
    def loads_event(self, data: Union[bytes, Event]) -> Event:
        pass

    @abc.abstractmethod
    def dumps(self, data: Any, **kwds) -> Union[bytes, Any]:
        pass

    @abc.abstractmethod
    def loads(self, data: Union[bytes, Any]) -> Any:
        pass
