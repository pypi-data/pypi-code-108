import multiprocessing
import os
import time
from abc import abstractmethod, ABC
from configparser import ConfigParser
from datetime import datetime
from multiprocessing import Queue

from simses.commons.console_printer import ConsolePrinter
from simses.commons.utils.utilities import format_float
from .batch_simulation import BatchSimulation


class BatchProcessing(ABC):

    """
    BatchProcessing delivers the necessary handling for running multiple parallel SimSES simulations and distributes
    the configuration to each process. It supervises all processes and starts as many processes as there are cores
    available. If you run more simulations than cores available, it waits until a simulation has finished and fills
    the gap with new simulation processes.
    """

    UPDATE: int = 1  # s

    def __init__(self, path: str = os.getcwd(),  do_simulation: bool = True, do_analysis: bool = True):
        self.__do_simulation: bool = do_simulation
        self.__do_analysis: bool = do_analysis
        self.__max_parallel_processes: int = max(1, multiprocessing.cpu_count() - 1)
        self.__path: str = os.path.join(path, 'results').replace('\\','/') + '/'
        print('Results will be stored in ' + self.__path)
        self.__result_paths: [str] = list()

    @abstractmethod
    def _setup_config(self) -> dict:
        """
        Setting up the necessary configuration for multiple simulations

        Returns
        -------
        dict:
            a dictionary of configs
        """
        pass

    def _analysis_config(self) -> ConfigParser:
        """
        Setting up the analysis configuration

        Returns
        -------
        ConfigParser:
            config for analysis
        """
        return ConfigParser()

    @abstractmethod
    def clean_up(self) -> None:
        pass

    def get_result_paths(self) -> [str]:
        out: [str] = list()
        for path in self.__result_paths:
            out.append(self.__get_latest_path_from(path))
        return out

    def __get_latest_path_from(self, path: str) -> str:
        result_dirs = list()
        tmp_dirs = os.listdir(path)
        for directory in tmp_dirs:
            if os.path.isdir(path + '/' + directory):
                result_dirs.append(path + '/' + directory + '/')
        return max(result_dirs, key=os.path.getmtime)

    def run(self):
        config_set: dict = self._setup_config()
        analysis_config: ConfigParser = self._analysis_config()
        print(str(len(config_set)) + ' simulations configured')
        printer_queue: Queue = Queue(maxsize=len(config_set) * 2)
        printer: ConsolePrinter = ConsolePrinter(printer_queue)
        jobs: [BatchSimulation] = list()
        for key, value in config_set.items():
            self.__result_paths.append(self.__path + key)
            jobs.append(BatchSimulation(config_set={key: value}, printer_queue=printer_queue, path=self.__path,
                                        do_simulation=self.__do_simulation, do_analysis=self.__do_analysis,
                                        analysis_config=analysis_config))
        printer.start()
        started: [BatchSimulation] = list()
        start = time.time()
        job_count: int = len(jobs)
        count: int = 0
        for job in jobs:
            job.start()
            started.append(job)
            count += 1
            print('\rStarting simulation ' + str(count) + '/' + str(job_count) + ' @ ' + str(datetime.now()))
            self.__check_running_process(started)
        for job in jobs:
            job.join()
        duration: float = (time.time() - start) / 60.0
        print('\r\n' + type(self).__name__ + ' finished ' + str(job_count) + ' simulations in ' + format_float(duration) + ' min '
              '(' + format_float(duration / job_count) + ' min per simulation)')
        printer.stop_immediately()

    def __check_running_process(self, processes: [multiprocessing.Process]) -> None:
        while True:
            running_jobs: int = 0
            for process in processes:
                if process.is_alive():
                    running_jobs += 1
            if running_jobs < self.__max_parallel_processes:
                break
            time.sleep(self.UPDATE)
