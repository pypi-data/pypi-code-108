import traceback
import typing as tp
from datetime import datetime
from multiprocessing import Queue as ProcessQueue, Process
from queue import Empty
from threading import Lock as ThreadLock
from threading import Thread
from time import sleep

import dill
import psutil

from ..servants.servant import Servant
from ..units.messenger import Messenger
from ..units.result_cache import ResultCache
from ..units.task_exceptions import TaskFailed, TaskTimeout, TaskKilledByQuitSignal, \
    TaskKilledByMonitoringError
from ..units.task_queue import TaskQueue
from ..units.task_result import TaskResult


class Worker(Servant):
    _TOTAL_ = 0

    def __init__(self, logging_folder: str,
                 request_cache: TaskQueue, request_cache_lock: ThreadLock,
                 result_cache: ResultCache, result_cache_lock: ThreadLock,
                 task_timeout_seconds: float):
        Worker._TOTAL_ += 1
        self._name = f"{self.__class__.__name__}-{Worker._TOTAL_}"
        super(Worker, self).__init__(logging_folder, self._name)
        self._task_cache = request_cache
        self._task_cache_lock = request_cache_lock
        self._result_cache = result_cache
        self._result_cache_lock = result_cache_lock
        self._task_timeout_seconds = task_timeout_seconds

        self._pids: tp.Optional[list] = None
        self._pids_lock = ThreadLock()

    def _start_setup(self, *args):
        with self._pids_lock:
            self._pids = []

    def _close_teardown(self):
        with self._pids_lock:
            self._pids = None

    def _monitor_process(self, pid: int, process: Process, start_timestamp: float,
                         from_process_queue: ProcessQueue,
                         to_process_queue: ProcessQueue, task_id: str):
        """
        monitor the process
        """

        while True:
            try:
                msg_type, msg = from_process_queue.get(self._time_unit)
                if msg_type == Messenger.DEBUG:
                    self._logger.debug(msg)
                elif msg_type == Messenger.INFO:
                    self._logger.info(msg)
                elif msg_type == Messenger.WARNING:
                    self._logger.warning(msg)
                elif msg_type == Messenger.ERROR:
                    self._logger.error(msg)
                elif msg_type == Messenger.SUBMIT:
                    # submit new task
                    _tasks = dill.loads(msg)
                    with self._result_cache_lock:
                        self._result_cache.reserve(_tasks)
                    with self._task_cache_lock:
                        self._task_cache.offer(_tasks)
                    to_process_queue.put(dill.dumps(len(_tasks)))  # acknowledge the number of tasks submitted
                elif msg_type == Messenger.QUERY:
                    # query task result
                    _task_ids = msg
                    with self._result_cache_lock:
                        _results = self._result_cache.get(_task_ids)
                    to_process_queue.put(dill.dumps(_results))
                elif msg_type == Messenger.RESULT:
                    # result come back; worker process done
                    process.join()
                    with self._pids_lock:
                        if self._pids[-1] != pid:  # sanity check
                            # the pids should finish in a stack style
                            self._logger.error(f"Process (pid {pid}) finished normally, but earlier than expected. "
                                               f"This should not happen. Current pid stack: {self._pids}")
                            self._pids.remove(pid)
                        else:
                            self._pids.pop()

                    result_ = dill.loads(msg)
                    with self._result_cache_lock:
                        self._result_cache.add([result_])

                    break
                else:
                    self._logger.error(f"Unknown message type sent by the Task process {pid}: {msg}")

                with self._thread_keeps_running_lock:
                    if not self._thread_keeps_running:
                        # worker receives stop signal
                        process.kill()

                        message = f"{self._name} has received stop signal. " \
                                  f"The task process {pid} has been killed."
                        with self._result_cache_lock:
                            self._result_cache.add([TaskResult(task_id, False, TaskKilledByQuitSignal(message))])

                        self._logger.warning(message)
                        break

                # time out
                if datetime.utcnow().timestamp() - start_timestamp > self._task_timeout_seconds:
                    process.kill()
                    with self._pids_lock:
                        if self._pids[-1] != pid:  # sanity check
                            # the pids should finish in a stack style
                            self._logger.error(f"Process (pid {pid}) timeout, but its has child processes."
                                               f"Current pid stack: {self._pids}")
                            self._pids.remove(pid)
                        else:
                            self._pids.pop()

                    message = f"Task (task_id: {task_id}) time out. The task process {pid} has been killed."
                    with self._result_cache_lock:
                        self._result_cache.add(
                            [TaskResult(task_id, False, TaskTimeout(message))])
                    self._logger.error(message)
                    break
            except Empty:
                # no message
                if not process.is_alive():
                    with self._pids_lock:
                        if self._pids[-1] != pid:  # sanity check
                            # the pids should finish in a stack style
                            self._logger.error(f"Process (pid {pid}) seems to be dead, but its has child processes."
                                               f"Current pid stack: {self._pids}")
                            self._pids.remove(pid)
                        else:
                            self._pids.pop()

                    message = f"Task (task_id: {task_id}) seems to be dead. The task process {pid} has been removed."
                    with self._result_cache_lock:
                        self._result_cache.add(
                            [TaskResult(task_id, False, TaskTimeout(message))])
                    self._logger.error(message)
                    break

            except Exception as err:
                process.kill()
                with self._pids_lock:
                    if self._pids[-1] != pid:  # sanity check
                        # the pids should finish in a stack style
                        self._logger.error(f"Process (pid {pid}) encountered error and got killed. "
                                           f"Its has child processes. Current pid stack: {self._pids}")
                        self._pids.remove(pid)
                    else:
                        self._pids.pop()

                message = f"Error occurred while monitoring task (task_id: {task_id}): {err}. " \
                          f"The task process has been killed."
                self._result_cache.add([TaskResult(task_id, False, TaskKilledByMonitoringError(message))])
                self._logger.error(message)
                raise err

        del process

    @staticmethod
    def _run_task_process(task_id: str, task_bytes: bytes,
                          from_process_queue: ProcessQueue, to_process_queue: ProcessQueue):
        task = dill.loads(task_bytes)
        messenger = Messenger(from_process_queue, to_process_queue)
        try:
            messenger.info(f'Task started (task id: {task_id} task name: {task.__class__.__name__}).')
            result = task.run(messenger)
            messenger.info(f'Task done (task id: {task_id} task name: {task.__class__.__name__}).')
            from_process_queue.put((Messenger.RESULT, dill.dumps(TaskResult(task_id, True, result,
                                                                            messenger.followup_task_ids))))

        except TaskFailed as result:
            # a predefined known reason triggered the failure
            messenger.warning(f'Task failed (task id: {task_id} task name: {task.__class__.__name__}).')
            from_process_queue.put((Messenger.RESULT, dill.dumps(TaskResult(task_id, False, result,
                                                                            messenger.followup_task_ids))))

        except Exception as err:
            messenger.error(f'Task (task id: {task_id}, task name: {task.__class__.__name__}) '
                            f'encountered an exception of {err.__class__.__name__}: {err}.\n' +
                            traceback.format_exc())
            from_process_queue.put((Messenger.RESULT, dill.dumps(TaskResult(task_id, False, err,
                                                                            messenger.followup_task_ids))))

    def _run(self):
        process = None
        with self._pids_lock:
            current_pid = None if len(self._pids) == 0 else self._pids[-1]
            with self._task_cache_lock:
                task = self._task_cache.poll(current_pid)

            if task is not None:
                start_timestamp = datetime.utcnow().timestamp()
                from_process_queue = ProcessQueue()  # a message queue to get message from the process
                to_process_queue = ProcessQueue()  # a message queue to send message to the process
                process = Process(target=self._run_task_process,
                                  args=(task.task_id, dill.dumps(task.procedure),
                                        from_process_queue, to_process_queue))
                process.start()

                # wait for process to spawn and generate pid
                while process.pid is None:
                    sleep(self._time_unit)
                    if datetime.utcnow().timestamp() - start_timestamp > self._task_timeout_seconds:
                        # task process fail to start
                        self._logger.error(f"Process for task (task_id: {task.task_id}) fails to start")
                        break

                pid = process.pid
                self._pids.append(pid)

        if process is not None:
            Thread(target=self._monitor_process,
                   args=(pid, process, start_timestamp, from_process_queue, to_process_queue, task.task_id)).start()

    @property
    def status(self):
        with self._pids_lock:
            if self._pids is None:
                raise Exception(f"{self._name} has not started yet.")

            processes = []
            for pid in self._pids:
                p = psutil.Process(pid)
                processes.append({
                    "cpu_percent": p.cpu_percent(1),
                    "memory_info": p.memory_info()
                })

            res = {
                "name": self._name,
                "processes": processes
            }
        return res
