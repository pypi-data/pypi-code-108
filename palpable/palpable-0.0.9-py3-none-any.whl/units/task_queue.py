import typing as tp

from sortedcontainers import SortedSet

from ..units.task import Task


class TaskQueue(object):
    def __init__(self):
        """
        A Task Queue to store Tasks in Timestamp order

        """
        self._queue: SortedSet[Task] = SortedSet(key=lambda t: (t.timestamp, t.task_id))
        self._source_pid_to_tasks: tp.Dict[str, SortedSet] = dict()

    def offer(self, tasks: tp.List[Task]):
        """
        Add Tasks into the cache
        :param tasks:
        :return: None
        """
        for task in tasks:
            self._queue.add(task)
            if task.source_pid in self._source_pid_to_tasks:
                cache = self._source_pid_to_tasks[task.source_pid]
            else:
                cache = SortedSet(key=lambda t: (t.timestamp, t.task_id))
                self._source_pid_to_tasks[task.source_pid] = cache

            cache.add(task)

    def poll(self, source_pid: tp.Optional[int]) -> tp.Optional[Task]:
        """
        If the source_pid is None, return the earliest Task from cache. The Task is then removed from the cache
        If the source_pid is not None, then find the earliest Task that haves the source_pid and the source process is
        waiting. This is to get the Task that
            - issued by a source process
            - the source process is blocking and is waiting for the result of this Task
        The Task is then removed from the cache.

        Return None if it does not exist.

        :param source_pid: the process id of the source
        """
        if source_pid is None:
            if len(self._queue) > 0:
                res: Task = self._queue.pop(0)
                self._source_pid_to_tasks[res.source_pid].remove(res)
                if len(self._source_pid_to_tasks[res.source_pid]) == 0:
                    self._source_pid_to_tasks.pop(res.source_pid)
                return res
        else:
            if source_pid in self._source_pid_to_tasks:
                res: Task = self._source_pid_to_tasks[source_pid][0]
                if res.is_source_blocking:
                    self._source_pid_to_tasks[source_pid].remove(res)
                    if len(self._source_pid_to_tasks[source_pid]) == 0:
                        self._source_pid_to_tasks.pop(source_pid)
                    self._queue.remove(res)
                    return res
        return None

    def __len__(self):
        return len(self._queue)
