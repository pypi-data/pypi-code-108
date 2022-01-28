import typing as tp
from threading import Lock as ThreadLock
from threading import Thread
from time import sleep

from ..basis.setup_logger import setup_logger


class Servant(object):
    def __init__(self, logging_folder: str, name: str = None):

        self._logging_folder = logging_folder
        self._name = self.__class__.__name__ if name is None else name

        self._logger = setup_logger(logging_folder, self._name)

        self._thread: tp.Optional[Thread] = None
        self._thread_keeps_running: bool = False
        self._thread_keeps_running_lock: ThreadLock = ThreadLock()

        self._time_unit = 0.01  # 0.01 second, used in sleep or queue.get

    def _start_setup(self):
        """
        Thread start setup. Will be called in self.start()
        :return:
        """
        pass

    def _stop_cascade(self):
        """
        Thread stop cascade. Set the self._keep_thread_running to false of any downstream ServantThreads
        Will be called in self.stop()
        :return:
        """
        pass

    def _join_cascade(self):
        """
        Thread join cascade.  For any downstream ServantThreads to join. Will be called in self.join()
        :return:
        """
        pass

    def _close_teardown(self):
        """
        Thread close teardown. Set variables that were set up in start_setup to None. Will be called in self.close()
        """
        pass

    def _run(self):
        """
        This will be called by _thread_loop and run in a thread. Any variables accessed by other Servant methods should
        be applied a lock. E.g. there is a variable self._count get incremented in self._run(), and accessed by
        self.get(). Then, self._count needs a lock.
        The _thread_loop calls this function every _time_unit seconds
        :return: None
        """
        raise NotImplementedError

    def _thread_loop(self):
        try:
            while True:
                sleep(self._time_unit)

                with self._thread_keeps_running_lock:
                    if not self._thread_keeps_running:
                        break

                self._run()

        except Exception as err:
            self._logger.error(f" {self._name} encountered error: {type(err)} {err}.")
            self.stop()

    def start(self, *args):
        with self._thread_keeps_running_lock:
            if self._thread_keeps_running:
                raise Exception(f"{self._name} already started.")
            self._thread_keeps_running = True

        self._logger.info(f"Starting {self._name}...")
        self._start_setup()
        self._thread = Thread(target=self._thread_loop, args=args, name=self._name)
        self._thread.start()
        self._logger.info(f"{self._name} started.")
        return self

    def stop(self):
        with self._thread_keeps_running_lock:
            if not self._thread_keeps_running:
                raise Exception(f"{self._name} has not started yet.")
            self._thread_keeps_running = False
        self._stop_cascade()
        self._logger.info(f"Stopping {self._name}...")
        return self

    def join(self):
        if self._thread is None:
            raise Exception(f"{self._name} has not started yet.")
        self._join_cascade()
        self._thread.join()
        return self

    def close(self):
        if self._thread is None:
            raise Exception(f"{self._name} has been closed already.")
        elif self._thread.is_alive():
            raise Exception(f"{self._name} must be joined before calling close.")

        self._close_teardown()
        self._thread = None
        self._logger.info(f"{self._name} stopped.")
        return self
