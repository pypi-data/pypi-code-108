import signal
import time
from multiprocessing.context import Process
from typing import List

from nehushtan.helper.SignalHandler import SignalHandler
from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger
from nehushtan.logger.NehushtanLogging import NehushtanLogging
from nehushtan.multiprocessing.NehushtanMPJob import NehushtanMPJob
from nehushtan.multiprocessing.NehushtanMPTerminatedSituation import NehushtanMPTerminatedSituation


class NehushtanMPQueue(SignalHandler):
    """
    Since 0.2.13

    Notice:
    The program entrance should be put into `if __name__ == '__main__':`;
    and need `set_start_method('spawn')` in the beginning.
    """

    def __init__(self):
        self._logger = None

        self.__max_workers = 1
        self.__waiting_queue = []
        self.__running_dict = {}
        self.__running_worker_dict = {}

        self.__received_terminate_signal = False

    def set_logger(self, logger: NehushtanFileLogger):
        self._logger = logger
        return self

    def get_logger(self) -> NehushtanFileLogger:
        if self._logger is None:
            self._logger = NehushtanFileLogger(log_level=NehushtanLogging.NOTICE)
        return self._logger

    def get_max_workers(self):
        return self.__max_workers

    def set_max_workers(self, max_workers: int):
        self.__max_workers = max_workers
        return self

    def get_target_signal_list(self) -> List[int]:
        return [signal.SIGTERM]

    def handle_signal(self, signal_number, frame):
        """
        Handle SIGNAL 15 (TERMINATE) as Callback
        Let all processes in multiprocessing receive SIGTERM signal
        """

        self.__received_terminate_signal = True

        self.get_logger().warning('NehushtanMPQueue::handle_signal received signal', signal_number)
        if signal_number == signal.SIGTERM:
            self.__waiting_queue = []
            self.get_logger().critical('NehushtanMPQueue::handle_signal cleaned the waiting queue')
            for pid, p in self.__running_dict.items():
                if p.is_alive():
                    self.get_logger().critical(
                        'NehushtanMPQueue::handle_signal terminate alive sub process',
                        {'pid': p.pid, 'is_alive': p.is_alive(), }
                    )
                    p.terminate()
                else:
                    self.get_logger().critical(
                        'NehushtanMPQueue::handle_signal terminate sub process exited already',
                        {'pid': p.pid, 'is_alive': p.is_alive(), 'exit_code': p.exitcode, }
                    )

    def enqueue_job(self, job: NehushtanMPJob):
        self.__waiting_queue.insert(0, job)
        self.get_logger().info('NehushtanMPQueue::enqueue_job', job.get_name())
        return self

    def __create_worker_for_job(self, job: NehushtanMPJob):
        p = Process(target=job.handle)
        p.start()
        job.set_pid(p.pid)
        self.__running_dict[p.pid] = p
        self.__running_worker_dict[p.pid] = job
        self.get_logger().info(
            'NehushtanMPQueue::__create_worker_for_job',
            {'job': job.get_name(), 'pid': job.get_pid()}
        )
        return p.pid

    def execute_all_jobs(self, rest_seconds=5, max_workers: int = None):
        """
        The NehushtanMPQueue starts after all jobs were enqueued.
        This method would clean
        """

        # register signal handler for SIGTERM
        self.apply()

        if max_workers is not None:
            self.set_max_workers(max_workers)

        self.get_logger().info('NehushtanMPQueue::execute_all_jobs', {'pool_size': self.get_max_workers()})
        while True:
            current_process_count = self.scan_workers()
            waiting_jobs = len(self.__waiting_queue)
            self.get_logger().info(
                'NehushtanMPQueue::execute_all_jobs report',
                {'running_jobs': current_process_count, 'waiting_jobs': waiting_jobs, 'workers': self.get_max_workers()}
            )

            if current_process_count <= 0:
                # multiprocessing empty, check waiting queue
                if waiting_jobs <= 0:
                    # if no waiting task, ends
                    break
                job = self.__waiting_queue.pop()
                self.__create_worker_for_job(job)

            elif current_process_count < self.get_max_workers():
                # multiprocessing has free space, check waiting queue
                if waiting_jobs <= 0:
                    # if no waiting task, sleep
                    time.sleep(rest_seconds)
                else:
                    job = self.__waiting_queue.pop()
                    self.__create_worker_for_job(job)

            else:
                # multiprocessing is full, sleep
                time.sleep(rest_seconds)

        self.get_logger().info('NehushtanMPQueue::execute_all_jobs all sub-processes ended')

        # unregister signal handler for SIGTERM, replaced by the default
        self.apply_default()

        if self.__received_terminate_signal:
            raise NehushtanMPTerminatedSituation(
                f'NehushtanMPQueue received SIGTERM during running execute_all_jobs.'
            )

    def when_worker_observed_exited(self, pid: int, exit_code: int):
        """
        When worker (sub process) is found as exited in `scan_workers`,
        this method would be called, normally in main process.
        """
        self.get_logger().info(
            'NehushtanMPQueue::when_worker_observed_exited',
            {'pid': pid, 'exit_code': exit_code}
        )
        worker = self.__running_worker_dict.get(pid)
        if worker:
            worker.when_exited(exit_code)

    def scan_workers(self) -> int:
        """
        Scan all workers in `__running_dict`,
        Clear the exited ones and report,
        Then return the count of the remaining.
        """
        if len(self.__running_dict.items()) <= 0:
            return 0

        finished_pid = []
        for pid, p in self.__running_dict.items():
            if not p.is_alive():
                self.get_logger().info(
                    'NehushtanMPQueue::refresh_running_sub_process_count a sub process is not alive now',
                    {'pid': p.pid, 'exit_code': p.exitcode}
                )
                finished_pid.append(pid)
                self.when_worker_observed_exited(p.pid, p.exitcode)

        for pid in finished_pid:
            del self.__running_dict[pid]

        self.get_logger().info(
            'NehushtanMPQueue::refresh_running_sub_process_count now still alive process',
            self.__running_dict.keys()
        )

        return len(self.__running_dict.items())
