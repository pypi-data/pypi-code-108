import typing as tp

from .task_result import TaskResult
from ..basis.immutable import Immutable


class _Response_(dict):
    def __init__(self, task_id: tp.Optional[str], data: object, followup_task_ids: tp.Union[list, tuple] = ()):
        super(_Response_, self).__init__(
            task_id=task_id,
            status=self.__class__.__name__,
            data=data,
            followup_task_ids=followup_task_ids
        )

    def __eq__(self, other):
        if isinstance(other, _Response_):
            return self["status"] == other["status"]

        if issubclass(other, _Response_):
            return self["status"] == other.__name__

        raise Exception(f"Cannot compare with {other}")

    def __ne__(self, other):
        if isinstance(other, _Response_):
            return self["status"] != other["status"]

        if issubclass(other, _Response_):
            return self["status"] != other.__name__

        raise Exception(f"Cannot compare with {other}")


class TaskResponse(Immutable):
    RESPONSE = _Response_

    class ERROR(_Response_):
        """
        There is an exception thrown during process of the task
        The data is the exception message
        """
        pass

    class SUCCESS(_Response_):
        """
        Processing is successful. The data is the result
        """
        pass

    class NONE(_Response_):
        """
        There are no tasks related to the request can be found
        """
        pass

    class TBD(_Response_):
        """
        The process is still running. the data is the ajax_relay url
        """
        pass

    def __init__(self, tbd_message_getter: tp.Callable = None):
        self.tbd_message_getter = lambda task_id: task_id if tbd_message_getter is None else tbd_message_getter

    @staticmethod
    def of(task_result: tp.Optional[TaskResult]):
        if task_result is None:
            # no such task
            return TaskResponse.NONE(None, f"Task does not exist")
        else:
            task_id = task_result.task_id
            if task_result.is_successful is None:
                # still running
                return TaskResponse.TBD(task_id, task_result.data, task_result.followup_task_ids)
            elif task_result.is_successful is True:
                # task successful
                return TaskResponse.SUCCESS(task_id, task_result.data, task_result.followup_task_ids)
            else:
                # task unsuccessful. task_result.data is the Exception
                return TaskResponse.ERROR(task_id, str(task_result.data), task_result.followup_task_ids)
