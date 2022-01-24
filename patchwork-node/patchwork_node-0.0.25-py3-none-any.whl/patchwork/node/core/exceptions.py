# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from typing import Union


class TaskControlException(Exception):
    """
    Set of control exceptions raised by processors to notify executor.
    """
    pass


class TaskRetry(TaskControlException):
    """
    Requests task processing retry. Waits optional countdown seconds until next attempt.
    All processed data and stored outputs will be dropped. If retry attempts is reached
    task is backoffed.
    """

    def __init__(self, *, countdown: float = None, progress: Union[float, str, bytes] = None):
        if countdown is not None:
            self.not_before = datetime.utcnow() + timedelta(seconds=countdown)
        else:
            self.not_before = None

        self.progress = progress


class TaskFatal(TaskControlException):
    """
    Processor ends with fatal exception and task is unprocessable now and in the future.
    No retry, output dropped. Log task on backoff queue.
    """

    def __init__(self, *, reason: str = None):
        self.reason = reason


class TaskDrop(TaskControlException):
    """
    Drop this task without logging it on backoff queue.
    """
    pass


class TaskNoHandler(TaskFatal):
    """
    There is no handler to process this task
    """
    pass
