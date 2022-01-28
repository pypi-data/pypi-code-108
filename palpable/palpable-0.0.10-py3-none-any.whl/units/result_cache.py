import typing as tp

from sortedcontainers import SortedSet

from ..units.task import Task
from ..units.task_result import TaskResult


class ResultCache(object):
    def __init__(self, result_retention_capacity: int, result_retention_seconds: float):
        """
        A cache to store Results.
        :param result_retention_capacity: the total number of results that can be stored
        :param result_retention_seconds: the maximum seconds for a result to stay in the cache. After this much seconds
            the result will be remove from the cache
        """
        self._result_retention_capacity = result_retention_capacity
        self._result_retention_seconds = result_retention_seconds
        self._task_id_waiting_for_results = set()

        self._task_id_to_result = dict()
        self._cache = SortedSet(key=lambda result: (result.timestamp, result.task_id))

    def reserve(self, tasks: tp.List[Task]):
        """
        Reserve places in the cache for future results
        :param tasks: A list of Request
        :return:
        """
        for task in tasks:
            self._task_id_waiting_for_results.add(task.task_id)

    def add(self, results: tp.List[TaskResult]):
        """
        Add Results to the cache
        :param results: a list of Results
        :return:
        """
        for result in results:
            if len(self._cache) == self._result_retention_capacity:
                # full
                to_delete: TaskResult = self._cache.pop(0)
                self._task_id_to_result.pop(to_delete.task_id)

            self._cache.add(result)
            self._task_id_to_result[result.task_id] = result
            self._task_id_waiting_for_results.remove(result.task_id)

    def get(self, task_ids: tp.List[str]) -> tp.List[tp.Optional[TaskResult]]:
        """
        Given task_ids return the results:
        - None, if no such request result exist in the cache
        - TaskResult(task_id, None, None) if the result is not ready
        - TaskResult if the result is ready, and the TaskResult will be removed from the cache

        :param task_ids: a list of task_ids
        :return: a list of Results in the order of the querying task_ids
        """
        res = []
        for task_id in task_ids:
            if task_id in self._task_id_to_result:
                result = self._task_id_to_result.pop(task_id)
                self._cache.remove(result)
            elif task_id in self._task_id_waiting_for_results:
                result = TaskResult(task_id, None, None)
            else:
                result = None
            res.append(result)
        return res

    def prune(self, current_timestamp: float):
        """
        prune the cache, to get rid of the results exceeds the retention seconds
        :param current_timestamp:
        :return:
        """
        timestamp_threshold = current_timestamp - self._result_retention_seconds
        # any result less than timestamp_threshold will be removed
        while len(self._cache) > 0:
            result: TaskResult = self._cache[0]
            if result.timestamp < timestamp_threshold:
                self._cache.remove(result)
                self._task_id_to_result.pop(result.task_id)
            else:
                break

    def __len__(self):
        return len(self._cache)
