import typing as tp
from io import StringIO
from multiprocessing.queues import Queue as ProcessQueue
from time import sleep

import dill

from ..basis.immutable import Immutable
from ..procedures.procedure import Procedure
from ..units.task import Task
from ..units.task_result import TaskResult


class Messenger(Immutable):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUBMIT = "SUBMIT"
    QUERY = "QUERY"

    RESULT = "RESULT"

    time_unit = 0.01

    def __init__(self, from_process_queue: ProcessQueue, to_process_queue: ProcessQueue):
        """
        Used in the Process started by the Worker to exchange information with the Worker monitoring thread.
        :param from_process_queue: the queue receives message from the Worker process and get by the Worker Thread
        :param to_process_queue: the queue receives message from the Worker thread and get by the Worker Process
        """
        self.from_process_queue = from_process_queue
        self.to_process_queue = to_process_queue
        self.followup_task_ids = []

    def debug(self, message: str):
        self.from_process_queue.put((self.DEBUG, message))

    def info(self, message: str):
        self.from_process_queue.put((self.INFO, message))

    def warning(self, message: str):
        self.from_process_queue.put((self.WARNING, message))

    def error(self, message: str):
        self.from_process_queue.put((self.ERROR, message))

    def print(self, *args, **kwargs):
        with StringIO() as buf:
            kwargs["file"] = buf
            kwargs["flush"] = True
            print(*args, **kwargs)
            self.info(buf.getvalue())

    def run_procedure(self, procedure: Procedure):
        """
        Run the procedure and return the result
        This method is blocking until result returns
        :param procedure: the procedure class
        :return:
        """

        task = Task(procedure, is_source_blocking=True)
        self.submit_tasks([task], need_followup=False)
        while True:
            sleep(self.time_unit)
            result = self.query_results([task.task_id])[0]
            if result is None:
                # no such task
                raise Exception(f"The submitted Task (ID: {task.task_id}) does not exist. This should not occur.")
            else:
                if result.is_successful is True:
                    # task successful
                    return result.data

                elif result.is_successful is False:
                    # task unsuccessful
                    if isinstance(result.data, Exception):
                        raise result.data
                    else:
                        raise Exception(str(result.data))
                else:
                    # task is still running
                    pass

    def submit_tasks(self, tasks: tp.List[Task], need_followup=False):
        """
        Submit sub Tasks to Server.
        If need_followup is True, the task_ids will be added to the followup_tasks_ids attribute of the TaskResult of
        the current Task.
        """

        self.from_process_queue.put((self.SUBMIT, dill.dumps(tasks)))
        # waiting for acknowledge to come back to confirm submission
        results = self.to_process_queue.get()
        number = dill.loads(results)
        if number != len(tasks):
            raise Exception(f"Expected to submitting {len(tasks)} Task(s), but {number} Task(s) are submitted")

        if need_followup:
            for task in tasks:
                self.followup_task_ids.append(task.task_id)

    def query_results(self, task_ids: tp.List[str]) -> tp.List[tp.Optional[TaskResult]]:
        """
        Query a list of task_ids with results
        This method blocks until results return
        """
        self.from_process_queue.put((self.QUERY, task_ids))
        results = self.to_process_queue.get()  # waiting for results coming back
        res = dill.loads(results)
        return res
