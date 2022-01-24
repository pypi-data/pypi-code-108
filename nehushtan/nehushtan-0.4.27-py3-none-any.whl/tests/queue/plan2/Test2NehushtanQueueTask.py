import time
from random import random

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.queue.NehushtanQueueTask import NehushtanQueueTask


class Test2NehushtanQueueTask(NehushtanQueueTask):
    def __init__(self, task_id: int):
        super().__init__()

        self._task_id = task_id
        self.logger = NehushtanFileLogger(
            f'task-{self._task_id}',
            '/Users/leqee/code/nehushtan/log/queue-plan2/task',
            categorize=False,
            date_rotate=False
        )

    def get_task_reference(self):
        return self._task_id

    def get_task_type(self):
        return 'TEST_TASK'

    def execute(self):
        time_cost = int(10 * random())
        self.logger.info(f'Task Execute Plan to spend {time_cost} seconds', {'task_id': self.get_task_reference()})
        time.sleep(time_cost)
        self.execute_result = random()
        if self.execute_result > 0.9:
            raise RuntimeError('Boom!')
        elif self.execute_result > 0.8:
            self.done = False
        else:
            self.done = True

        self.execute_feedback = f'Result is {self.execute_result}, and Done is {self.done}'
        self.logger.info(f'Task Executed', {'task_id': self.get_task_reference()})
