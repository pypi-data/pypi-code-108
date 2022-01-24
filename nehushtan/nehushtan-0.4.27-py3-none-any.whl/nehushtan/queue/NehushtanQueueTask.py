from abc import abstractmethod
from typing import List


class NehushtanQueueTask:
    def __init__(self):
        self.ready_to_execute: bool = False
        self.ready_to_finish: bool = False
        self.done: bool = False
        self.execute_feedback: str = 'Not Executed Yet'
        self.execute_result = None

    @abstractmethod
    def get_task_reference(self):
        pass

    @abstractmethod
    def get_task_type(self):
        pass

    def before_execute(self):
        """
        This works in MASTER
        """
        self.ready_to_execute = True
        return self.ready_to_execute

    @abstractmethod
    def execute(self):
        """
        This works in WORKER - EMBEDED

        Need to override and fulfill
        self.done: bool
        self.execute_feedback: str
        self.execute_result: Any
        """
        pass

    def after_execute(self):
        """
        This works in WORKER - EMBEDED
        """
        self.ready_to_finish = True
        return self.ready_to_finish

    def get_lock_list(self) -> List[str]:
        """
        Array of Lock Names
        """
        return []

    def is_exclusive(self) -> bool:
        """
        Determine if this task should be run in Exclusive Mode,
        which would wait for other all tasks stopped before starts,
        and never run other tasks until it ends.

        This works in MASTER
        """
        return False

    def check_if_locked(self) -> bool:
        """
        Locks should be checked here
        Should be called by Delegate::checkNextTaskImplement
        """
        return False
