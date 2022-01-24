from abc import abstractmethod

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.queue.NehushtanQueueTask import NehushtanQueueTask


class NehushtanQueueTaskDelegate:
    """
    Since 0.4.11
    """

    def __init__(self, config_dictionary: dict = None, logger: NehushtanFileLogger = None):
        if config_dictionary is None:
            config_dictionary = {}
        self.config_dictionary = config_dictionary

        if logger is None:
            logger = NehushtanFileLogger(f"{self.__class__.__name__}-Logger", )
        self.logger = logger

    @abstractmethod
    def when_to_execute_task(self, task: NehushtanQueueTask, pid: int):
        """
        SINCE 0.1.24 add parameter pid
        Note: Any exceptions should be caught inside.
        This works in WORKER - EMBEDED
        """
        pass

    @abstractmethod
    def when_task_raised_exception(self, task: NehushtanQueueTask, exception: Exception):
        """
        This works in WORKER - EMBEDED
        """
        pass

    @abstractmethod
    def when_task_executed(self, task: NehushtanQueueTask, pid: int):
        """
        SINCE 0.1.24 add parameter pid
        Note: Any exceptions should be caught inside.
        This works in WORKER - EMBEDED
        """
        try:
            if task.after_execute():
                self.logger.info('TASK FINISHED', {'task_id': task.get_task_reference(), 'pid': pid})
            else:
                self.logger.warning('TASK FINISHING UNWELL', {'task_id': task.get_task_reference(), 'pid': pid})
        except Exception as e:
            self.logger.exception(f'when_task_executed for task {task.get_task_reference()} on PID {pid}', e)
