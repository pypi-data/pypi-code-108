import typing as tp

from ..basis.timestamped_immutable import TimestampedImmutable


class TaskResult(TimestampedImmutable):
    def __init__(self, task_id: str, is_successful: tp.Optional[bool], data,
                 followup_task_ids: tp.Tuple[str] = ()):
        """
        Create a task result
        :param task_id: task_id
        :param is_successful: is this task successful, if None indicating the task is running
        :param data: the task's result data
        :param followup_task_ids: Followup Tasks have been submitted by this task and the task_ids are listed here
        """

        super(TaskResult, self).__init__()
        self.task_id = task_id
        self.is_successful = is_successful
        self.data = data
        self.followup_task_ids = followup_task_ids

    def __eq__(self, other):
        return self.task_id == other.task_id

    def __hash__(self):
        return hash(self.task_id)
