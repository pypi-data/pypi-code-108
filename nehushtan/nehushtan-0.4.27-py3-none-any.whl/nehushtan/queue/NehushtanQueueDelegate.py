import time
from abc import abstractmethod
from typing import List

from nehushtan.helper.CommonHelper import CommonHelper
from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.queue.NehushtanQueueTask import NehushtanQueueTask


class NehushtanQueueDelegate:
    QUEUE_RUNTIME_COMMAND_PAUSE = "PAUSE"
    QUEUE_RUNTIME_COMMAND_CONTINUE = "CONTINUE"
    QUEUE_RUNTIME_COMMAND_STOP = "STOP"
    # QUEUE_RUNTIME_COMMAND_FORCE_STOP = "FORCE-STOP"
    # QUEUE_RUNTIME_COMMAND_RESTART = "RESTART"
    # QUEUE_RUNTIME_COMMAND_FORCE_RESTART = "FORCE-RESTART"

    CONFIG_KEY_POOL_CAPACITY = 'POOL_CAPACITY'
    CONFIG_KEY_SLEEP_TIME_FOR_FREE = 'SLEEP_TIME_FOR_FREE'
    CONFIG_KEY_SLEEP_TIME_FOR_BUSY = 'SLEEP_TIME_FOR_BUSY'
    CONFIG_KEY_SLEEP_TIME_FOR_PAUSE = 'SLEEP_TIME_FOR_PAUSE'

    def __init__(self, config_dictionary: dict = None, logger: NehushtanFileLogger = None):
        """
        @since 0.1.25 logger changed to NehushtanFileLogger
        """
        if config_dictionary is None:
            config_dictionary = {}
        self.config_dictionary = config_dictionary

        if logger is None:
            logger = NehushtanFileLogger(f"{self.__class__.__name__}-Logger", )
        self.logger = logger

        self.latest_command = NehushtanQueueDelegate.QUEUE_RUNTIME_COMMAND_CONTINUE

    def read_config_of_delegate(self, keychain: tuple, default):
        return CommonHelper.read_dictionary(self.config_dictionary, keychain, default)

    def get_configured_pool_capacity(self) -> int:
        return self.read_config_of_delegate((NehushtanQueueDelegate.CONFIG_KEY_POOL_CAPACITY,), 1)

    def sleep_for_configured_time(self, config_key: str):
        """
        config_key might be amongst `CONFIG_KEY_SLEEP_TIME_FOR_*`
        """
        x = self.read_config_of_delegate((config_key,), 1)
        time.sleep(x)

    def read_latest_command(self) -> str:
        """
        Override this to fetch command from real pipe.
        This works in MASTER
        """
        self.latest_command = self.QUEUE_RUNTIME_COMMAND_CONTINUE
        return self.latest_command

    def when_loop_starts(self):
        """
        To be executed before loop cycle starts
        This works in MASTER
        """
        pass

    @abstractmethod
    def when_loop_reports_error(self, error_message: str, cause_exception: Exception = None):
        """
        This works in MASTER
        Since 0.4.4 Added cause_exception, could be expressed by NehushtanFileLogger
        """
        pass

    def is_runnable(self):
        """
        If not runnable, the daemon loop would sleep.
        This works in MASTER
        """
        return self.latest_command == self.QUEUE_RUNTIME_COMMAND_CONTINUE

    def should_terminate(self):
        """
        Tell daemon loop to exit.
        This works in MASTER
        """
        return (
            self.QUEUE_RUNTIME_COMMAND_STOP,
            # self.QUEUE_RUNTIME_COMMAND_FORCE_STOP,
            # self.QUEUE_RUNTIME_COMMAND_RESTART,
            # self.QUEUE_RUNTIME_COMMAND_FORCE_RESTART,
        ).__contains__(self.latest_command)

    @abstractmethod
    def when_loop_terminates(self):
        """
        When the loop gets ready to terminate by shouldTerminate instructed, execute this
        This works in MASTER
        """
        pass

    def when_loop_should_not_run(self):
        """
        Sleep for a certain while.
        This works in MASTER
        """
        self.sleep_for_configured_time(self.CONFIG_KEY_SLEEP_TIME_FOR_PAUSE)

    def before_seeking_next_tasks(self):
        """
        This works in MASTER
        It is a hook before `check_next_task`.
        A scnerio is, here delegate prepares a list of task candidates,
        And be consumed in `check_next_task` in order.
        Since 0.2.19
        """
        pass

    @abstractmethod
    def check_next_task_candidates(self) -> List[NehushtanQueueTask]:
        """
        This works in MASTER
        if none newly found... raise NoNextTaskSituation!
        Since 0.3.0
        """
        pass

    def when_no_task_to_do(self):
        """
        When the loop cannot check for a task to do next, execute this
        This works in MASTER
        """
        self.sleep_for_configured_time(self.CONFIG_KEY_SLEEP_TIME_FOR_FREE)

    @abstractmethod
    def when_task_not_executable(self, task: NehushtanQueueTask):
        """
        this is done before fork in pooled style
        This works in MASTER
        """
        pass

    def when_pool_is_full(self):
        """
        This works in MASTER
        """
        self.logger.warning('Pool is full, sleep for a while', {'size': self.get_configured_pool_capacity()})
        self.sleep_for_configured_time(self.CONFIG_KEY_SLEEP_TIME_FOR_BUSY)

    def when_worker_process_created(self, task_reference, note: str = ''):
        """
        This works in MASTER
        """
        pass

    def when_worker_process_confirmed_dead(self, task_reference, detail=None):
        """
        This works in MASTER
        """
        pass

    # def should_wait_when_pool_is_full(self):
    #     """
    #     This works in MASTER
    #     """
    #     return True

    def should_wait_for_all_workers_before_terminating(self):
        """
        This works in MASTER
        """
        return True

    @abstractmethod
    def should_kill_any_worker_processes(self) -> list:
        """
        This works in MASTER
        return a list of Task Reference
        """
        pass

    @abstractmethod
    def when_killed_worker_process(self, task_reference, not_found=False, worker_pid: int = None):
        """
        This works in MASTER
        """
        pass

    @abstractmethod
    def handle_command_queue(self) -> int:
        """
        This works in MASTER
        This may update the data for `should_kill_any_worker_processes` for loop,
        or do other jobs
        Since 0.2.18 should return an integer, as the count of commands handled; so, zero for no command to do.
        """
        pass

    def register_queue_news(self, title: str, content: str, running_worker_count: int, busy_rate: float):
        """
        Since 0.2.9
        This works in MASTER
        It provides a method to let delegate know what daemon happened, other than the `when_*` methods.
        By default, the news would be ignored.
        It could be used to write a message queue, print to heartbeat logs, etc.
        """
        pass
