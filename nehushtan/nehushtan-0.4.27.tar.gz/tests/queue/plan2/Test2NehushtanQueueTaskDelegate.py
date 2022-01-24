from nehushtan.queue.NehushtanQueueTask import NehushtanQueueTask
from nehushtan.queue.NehushtanQueueTaskDelegate import NehushtanQueueTaskDelegate


class Test2NehushtanQueueTaskDelegate(NehushtanQueueTaskDelegate):

    def when_to_execute_task(self, task: NehushtanQueueTask, pid: int):
        self.logger.info(
            'Test2NehushtanQueueDelegate when_to_execute_task',
            {'task_id': task.get_task_reference(), 'pid': pid}
        )

    def when_task_executed(self, task: NehushtanQueueTask, pid: int):
        self.logger.info(
            'Test2NehushtanQueueDelegate when_task_executed',
            {'task_id': task.get_task_reference(), 'pid': pid}
        )

    def when_task_raised_exception(self, task: NehushtanQueueTask, exception: Exception):
        self.logger.exception(
            f'Test2NehushtanQueueDelegate when_task_raised_exception task_id={task.get_task_reference()}',
            exception
        )
