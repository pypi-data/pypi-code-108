import typing as tp
from datetime import datetime
from threading import Lock as ThreadLock

from ..units.result_cache import ResultCache
from ..units.task import Task
from ..units.task_queue import TaskQueue
from .servant import Servant
from .worker import Worker
from ..units.task_result import TaskResult


class Manager(Servant):
    def __init__(self, logging_folder: str,
                 num_workers: int,
                 task_timeout_seconds: float,
                 result_retention_capacity: int,
                 result_retention_seconds: float):
        """
        Manage workers
        :param logging_folder: the logging folder
        :param num_workers: number of workers to run tasks
        :param result_retention_capacity: the capacity of result stored
        :param result_retention_seconds: the seconds to store the result before it gets removed
        """
        super(Manager, self).__init__(logging_folder)
        self._num_workers = num_workers
        self._task_timeout_seconds = task_timeout_seconds
        # workers are only accessed in one thread, so no need to have a lock
        self._workers: tp.Optional[tp.List[Worker]] = None

        self._result_retention_capacity = result_retention_capacity
        self._result_retention_seconds = result_retention_seconds

        self._task_queue: tp.Optional[TaskQueue] = None
        self._task_queue_lock = ThreadLock()

        self._result_cache: tp.Optional[ResultCache] = None
        self._result_cache_lock = ThreadLock()

    def _start_setup(self):
        with self._task_queue_lock:
            self._task_queue = TaskQueue()

        with self._result_cache_lock:
            self._result_cache = ResultCache(self._result_retention_capacity,
                                             self._result_retention_seconds)

        self._workers = [
            Worker(self._logging_folder,
                   self._task_queue, self._task_queue_lock,
                   self._result_cache, self._result_cache_lock,
                   self._task_timeout_seconds).start()
            for _ in range(self._num_workers)
        ]

    def _stop_cascade(self):
        for worker in self._workers:
            worker.stop()

    def _join_cascade(self):
        for worker in self._workers:
            worker.join()

    def _close_teardown(self):
        for worker in self._workers:
            worker.close()
        self._workers = None

        with self._task_queue_lock:
            self._task_queue = None

        with self._result_cache_lock:
            self._result_cache = None

    def _run(self):
        """
        Prune the result cache every time_unit
        :return:
        """
        with self._result_cache_lock:
            self._result_cache.prune(datetime.utcnow().timestamp())

    def submit_tasks(self, tasks: tp.List[Task]):
        with self._thread_keeps_running_lock:
            if not self._thread_keeps_running:
                raise Exception(f"{self._name} has not started yet")

        with self._result_cache_lock:
            self._result_cache.reserve(tasks)
        with self._task_queue_lock:
            self._task_queue.offer(tasks)

    def query_results(self, task_ids: tp.List[str]) -> tp.List[tp.Optional[TaskResult]]:
        """
        Return
            - the TaskResult
            - None, if there is no such task
        :param task_ids: a list of task_ids
        :return:
        """
        with self._thread_keeps_running_lock:
            if not self._thread_keeps_running:
                raise Exception(f"{self._name} has not started yet")

        with self._result_cache_lock:
            return self._result_cache.get(task_ids)

    @property
    def status(self) -> dict:
        with self._thread_keeps_running_lock:
            if not self._thread_keeps_running:
                raise Exception(f"{self._name} has not started yet")

        worker_status = [worker.status for worker in self._workers]

        with self._task_queue_lock:
            task_queue_size = len(self._task_queue)

        with self._result_cache_lock:
            result_cache_size = len(self._result_cache)

        return {
            "worker_status": worker_status,
            "task_queue_size": task_queue_size,
            "result_cache_size": result_cache_size
        }
