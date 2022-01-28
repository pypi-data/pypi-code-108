import os
import typing as tp
from multiprocessing.connection import Client as ConnectionClient
from multiprocessing.connection import Listener
from threading import Lock as ThreadLock
from threading import Thread
from time import sleep

import dill

from ..servants.manager import Manager
from ..servants.servant import Servant


class Server(Servant):
    QUIT = "QUIT"
    GET_SERVER_STATUS = "GET_SERVER_STATUS"
    QUERY_RESULTS = "QUERY_RESULTS"
    SUBMIT_TASKS = "SUBMIT_TASKS"

    def __init__(self,
                 logging_folder: str,
                 address: tp.Union[tuple, str],
                 family: str,
                 authkey: bytes,
                 num_workers: int,
                 task_timeout_seconds: float = 3600 * 3,
                 result_retention_capacity: int = 100000,
                 result_retention_seconds: float = 60,
                 ):
        """
        Queue the incoming task request and run the jobs in <=num_nodes processes.
        The result will be saved for result_retention_seconds
        :param logging_folder: folder for logging. Cannot be None.
        :param address: address to connect
        :param family: connection family. It can be "AF_INET", "AF_UNIX", "AF_PIPE"
        :param authkey: authkey to authenticate connection
        :param num_workers: how many worker processes
        :param task_timeout_seconds: how many seconds is a task allow to run
        :param result_retention_capacity: max number of results to maintain in the result cache
        :param result_retention_seconds: how many seconds before the result gets removed
        """
        super(Server, self).__init__(logging_folder)
        self._address = address
        self._family = family
        self._authkey = authkey
        self._num_workers = num_workers
        self._task_timeout_seconds = task_timeout_seconds
        self._result_retention_capacity = result_retention_capacity
        self._result_retention_seconds = result_retention_seconds

        self._task_manager: tp.Optional[Manager] = None
        self._task_manager_lock = ThreadLock()

    def _start_setup(self):
        with self._task_manager_lock:
            self._task_manager = Manager(
                self._logging_folder,
                self._num_workers,
                self._task_timeout_seconds,
                self._result_retention_capacity,
                self._result_retention_seconds)
            self._task_manager.start()

    def _stop_cascade(self):
        with self._task_manager_lock:
            self._task_manager.stop()

    def _join_cascade(self):
        with self._task_manager_lock:
            self._task_manager.join()

    def _close_teardown(self):
        with self._task_manager_lock:
            self._task_manager.close()
            self._task_manager = None

    def _run(self):
        self._logger.info("start listener")
        if self._family == "AF_UNIX" and os.path.exists(self._address):
            os.remove(self._address)
        with Listener(self._address, family=self._family, authkey=self._authkey) as listener:
            self._logger.info(f'Listening at {self._address}')

            while True:
                with self._thread_keeps_running_lock:
                    if not self._thread_keeps_running:
                        break
                conn = listener.accept()
                Thread(target=self._handle_communication, args=(conn,), daemon=True).start()

    def _handle_communication(self, conn):
        package = conn.recv()
        command = package["command"]
        kwargs = dill.loads(package["kwargs"])
        if command == self.QUIT:
            response = True
            conn.send(dill.dumps(response))
            conn.close()
            self.stop()
            return
        elif command == self.GET_SERVER_STATUS:
            with self._task_manager_lock:
                response = self._task_manager.status
        elif command == self.QUERY_RESULTS:
            task_ids = kwargs["task_ids"]
            with self._task_manager_lock:
                response = self._task_manager.query_results(task_ids)
        elif command == self.SUBMIT_TASKS:
            tasks = kwargs["tasks"]
            with self._task_manager_lock:
                self._task_manager.submit_tasks(tasks)
            response = True
        else:
            # unknown command: echo kwargs
            response = kwargs

        conn.send(dill.dumps(response))
        conn.close()

    def start(self, timeout_seconds: tp.Optional[int] = 10):
        res = super(Server, self).start()

        if timeout_seconds is None or timeout_seconds == 0:
            return res

        for i in range(int(timeout_seconds / self._time_unit)):
            sleep(self._time_unit)
            if self.is_listening:
                return res

        raise Exception(f"{self.__class__.__name__} does not start in time")

    def stop(self):
        super(Server, self).stop()
        # send another empty connection to break the listener.accept() in case the thread is blocked there
        try:
            with ConnectionClient(address=self._address, family=self._family, authkey=self._authkey) as conn:
                item = {"command": None, "kwargs": dill.dumps(None)}
                conn.send(item)
                conn.recv()
        except ConnectionRefusedError:
            pass
        except FileNotFoundError:
            pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.join()
        self.close()

    @property
    def is_listening(self):
        try:
            with ConnectionClient(address=self._address, family=self._family, authkey=self._authkey) as conn:
                item = {"command": None, "kwargs": dill.dumps(True)}
                conn.send(item)
                result = conn.recv()
                return result
        except ConnectionRefusedError:
            pass
        except FileNotFoundError:
            pass

    @property
    def status(self):
        with self._task_manager_lock:
            return self._task_manager.status
