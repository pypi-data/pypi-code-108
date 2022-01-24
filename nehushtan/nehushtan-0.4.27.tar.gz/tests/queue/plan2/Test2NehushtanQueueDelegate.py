import time
from random import random
from typing import List

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.queue.NehushtanQueueDelegate import NehushtanQueueDelegate
from nehushtan.queue.NehushtanQueueTask import NehushtanQueueTask
from nehushtan.queue.situation.NoNextTaskSituation import NoNextTaskSituation
from tests.queue.plan2.Test2NehushtanQueueTask import Test2NehushtanQueueTask


class Test2NehushtanQueueDelegate(NehushtanQueueDelegate):

    def should_kill_any_worker_processes(self) -> list:
        return []

    def when_killed_worker_process(self, task_reference, not_found=False, worker_pid: int = None):
        self.logger.notice(
            'when_killed_worker_process',
            {'task_reference': task_reference, 'not_found': not_found, 'worker_pid': worker_pid}
        )

    def handle_command_queue(self) -> int:
        self.logger.info('handle_command_queue, actually do nothing')
        return 0

    def __init__(self, config_dictionary: dict = None, logger: NehushtanFileLogger = None):
        super().__init__(config_dictionary, logger)
        self.last_task_id = 1000

    def when_loop_reports_error(self, error_message: str, cause_exception: Exception = None):
        if cause_exception:
            self.logger.exception(error_message, cause_exception)
        else:
            self.logger.error('Test2NehushtanQueueDelegate when_loop_reports_error', error_message)

    def when_loop_terminates(self):
        self.logger.critical('Test2NehushtanQueueDelegate when_loop_terminates')

    def when_loop_should_not_run(self):
        self.logger.warning('Test2NehushtanQueueDelegate when_loop_should_not_run sleep 10')
        time.sleep(10)

    def check_next_task_candidates(self) -> List[NehushtanQueueTask]:
        self.logger.info('Test2NehushtanQueueDelegate check_next_task')
        if random() > 0.7:
            self.last_task_id += 1
            self.logger.info('Test2NehushtanQueueDelegate check_next_task -> create new task')
            return [Test2NehushtanQueueTask(task_id=self.last_task_id)]
        else:
            raise NoNextTaskSituation('No task to execute')

    def when_no_task_to_do(self):
        self.logger.info('Test2NehushtanQueueDelegate when_no_task_to_do sleep 5')
        time.sleep(5)

    def when_task_not_executable(self, task: NehushtanQueueTask):
        self.logger.info('Test2NehushtanQueueDelegate when_task_not_executable', {'task_id': task.get_task_reference()})
