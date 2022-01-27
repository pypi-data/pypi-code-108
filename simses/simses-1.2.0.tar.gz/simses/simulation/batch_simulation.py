import multiprocessing
import os
from configparser import ConfigParser
from multiprocessing import Queue

from simses.commons.utils.utilities import remove_all_files_from, create_directory_for
from simses.main import SimSES


class BatchSimulation(multiprocessing.Process):

    """
    BatchSimulation wraps the SimSES simulation into a multiprocessing Process in order to allow to run simulation
    in parallel. In addition, it is possible to run multiple threaded simulations within this process but this is
    strongly not recommended.
    """

    BATCH_DIR: str = 'batch/'

    def __init__(self, config_set: dict, printer_queue: Queue, path: str, batch_size: int = 1,
                 do_simulation: bool = True, do_analysis: bool = True, analysis_config: ConfigParser = ConfigParser()):
        super().__init__()
        self.__batch_dir: str = os.path.join(path, self.BATCH_DIR)
        create_directory_for(self.__batch_dir)
        remove_all_files_from(self.__batch_dir)
        self.__path: str = os.path.join(path)
        self.__batch_size: int = batch_size
        self.__printer_queue: Queue = printer_queue
        self.__config_set: dict = config_set
        self.__analysis_config: ConfigParser = analysis_config
        self.__do_simulation: bool = do_simulation
        self.__do_analysis: bool = do_analysis

    def __setup(self) -> [SimSES]:
        simulations: [SimSES] = list()
        for name, config in self.__config_set.items():
            remove_all_files_from(os.path.join(self.__path, name))
            simulations.append(SimSES(self.__path, name, do_simulation=self.__do_simulation,
                                      do_analysis=self.__do_analysis, simulation_config=config,
                                      analysis_config=self.__analysis_config, queue=self.__printer_queue,
                                      batch_dir=self.BATCH_DIR))
        return simulations

    def run(self):
        started: [SimSES] = list()
        simulations: [SimSES] = self.__setup()
        self.__check_simulation_names(simulations)
        for simulation in simulations:
            # print('\rStarting ' + simulation.name)
            simulation.start()
            started.append(simulation)
            if len(started) >= self.__batch_size:
                self.__wait_for(started)
                started.clear()
        self.__wait_for(started)

    @staticmethod
    def __wait_for(simulations: [SimSES]):
        for simulation in simulations:
            simulation.join()

    @staticmethod
    def __check_simulation_names(simulations: [SimSES]) -> None:
        names: [str] = list()
        for simulation in simulations:
            name: str = simulation.name
            if name in names:
                raise Exception(name + ' is not unique. Please check your simulation setup!')
            names.append(name)
