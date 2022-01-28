import typing as tp
from multiprocessing.connection import Client as ConnectionClient
from time import sleep

import dill

from ..procedures.map_function import MapFunction
from ..procedures.procedure import Procedure
from ..procedures.run_function import RunFunction
from ..servants.server import Server
from ..units.task import Task
from ..units.task_response import TaskResponse
from ..units.task_result import TaskResult


class Client(object):
    """
    Used by HTTP threads to submit jobs to TaskServer
    """

    def __init__(self, address: tp.Union[tuple, str], family: str, authkey: bytes):
        """
        :param address: address to connect
        :param family: connection family. It can be "AF_INET", "AF_UNIX", "AF_PIPE"
        :param authkey: authkey for authenticate connection
        """
        self._address = address
        self._family = family
        self._authkey = authkey
        self._time_unit = 0.5

    def _communicate(self, command, **kwargs):
        """
        :param command:
        :param kwargs:
        :return:
        """

        with ConnectionClient(address=self._address, family=self._family, authkey=self._authkey) as conn:
            item = {"command": command, "kwargs": dill.dumps(kwargs)}
            conn.send(item)
            result = conn.recv()
            return dill.loads(result)

    def run_procedure(self, procedure: Procedure, waiting_seconds: float = 1) -> TaskResult:
        """
        Run procedure and wait for waiting_seconds.
        If waiting_seconds<0 then wait until results is ready
        :param procedure:
        :param waiting_seconds:
        :return:
        """
        task = Task(procedure, is_source_blocking=(waiting_seconds < 0))
        task_id = task.task_id
        self._communicate(Server.SUBMIT_TASKS, tasks=[task])
        accumulated_waiting_seconds = 0
        res = TaskResult(task_id, None, None)
        while waiting_seconds < 0 or waiting_seconds > accumulated_waiting_seconds:
            sleep(self._time_unit)
            accumulated_waiting_seconds += self._time_unit
            res = self.query_result(task_id)
            if res is None:
                raise Exception(f"Cannot find task with task_id: {task_id} in TaskServer. "
                                f"This should not occur.")
            if res.is_successful is not None:
                return res
        return res

    def query_result(self, task_id: str) -> tp.Optional[TaskResult]:
        """
        Query result of the Task with the given task_id
        :param task_id:
        :return:
        """

        return self._communicate(Server.QUERY_RESULTS, task_ids=[task_id])[0]

    def map(self, function, params) -> list:
        """
        Map params to function. i.e. calling [function(param) for param in params]
        This method is blocking until the result returns
        :param function: the function to map the params
        :param params: the params to run function one by one
        :return: a list of results. The result order is the same as the params order
        """
        result = self.run_procedure(MapFunction(function, params), waiting_seconds=-1)
        if result.is_successful:
            return result.data
        else:
            raise result.data

    def run(self, function, params):
        """
        Call the function with params. i.e. calling function(params)
        This method is blocking until the result returns
        :param function:
        :param params:
        :return: the result
        """
        result = self.run_procedure(RunFunction(function, params), waiting_seconds=-1)
        if result.is_successful:
            return result.data
        else:
            raise result.data

    # task server operations
    def quit(self) -> None:
        self._communicate(Server.QUIT)

    def get_status(self):
        return self._communicate(Server.GET_SERVER_STATUS)

    @classmethod
    def _run_with_response(cls, function, *args, **kwargs) -> TaskResponse.RESPONSE:
        try:
            result = function(*args, **kwargs)
            return TaskResponse.of(result)

        except ConnectionRefusedError:
            return TaskResponse.ERROR(None, "TaskServer OFFLINE")
        except Exception as err:
            return TaskResponse.ERROR(None, str(err))

    def ajax_run_procedure(self, procedure: Procedure, waiting_seconds: float = 1) -> TaskResponse.RESPONSE:
        return self._run_with_response(self.run_procedure, procedure, waiting_seconds)

    def ajax_query_result(self, task_id: str) -> TaskResponse.RESPONSE:
        return self._run_with_response(self.query_result, task_id)

