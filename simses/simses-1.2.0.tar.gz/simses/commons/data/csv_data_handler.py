import csv
import gzip
import threading
import time
from datetime import datetime
from queue import Queue, Empty

import numpy
import pandas as pd

from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.data.data_handler import DataHandler
from simses.commons.log import Logger
from simses.commons.state.abstract_state import State
from simses.commons.utils.utilities import remove_all_files_from, copy_all_files, create_directory_for, \
    all_non_abstract_subclasses_of


class CSVDataHandler(threading.Thread, DataHandler):
    """
    Export for Battery data during the simulation into one CSV file_name.
    Batteries send their parameters for every timestamp to this class, which adds them to the CSV file_name.
    For Multiprocessing a queue is used.
    """

    USE_GZIP_COMPRESSION: bool = True
    EXT_CSV: str = '.csv'
    # Other compression formats: zip, bz2, xz
    COMP: str = 'gzip'
    EXT_COMP: str = '.gz'

    def __init__(self, result_dir: str, config: GeneralSimulationConfig, export_cls=State):
        super().__init__()
        self.__log: Logger = Logger(type(self).__name__)
        self.__queue = Queue()
        self.__append = True
        self.__simulation_running = True
        self.__result_folder: str = result_dir + 'EES_' + datetime.now().strftime('%Y%m%dT%H%M%SM%f')
        create_directory_for(self.__result_folder, warn=True)
        self.__working_directory = result_dir
        remove_all_files_from(self.__working_directory)
        self.__classes: list = all_non_abstract_subclasses_of(export_cls)
        # Deactivating export interval to prohibit wrong analysis results
        # self.__export_interval: float = config.export_interval
        self.__export_interval: float = 1
        self.__timestep: float = config.timestep

    def run(self) -> None:
        """
        Function to write data from queue to csv.

        Parameters
        ----------

        Returns
        -------

        """
        tstmps: dict = dict()
        file_writer: dict = dict()
        file_streams: list = list()
        # for cls in self.__classes:
        #     self.__register_writer(cls, file_writer, tstmps, file_streams)
        while self.__simulation_running or not self.__queue.empty():
            try:
                data: dict = self.__queue.get_nowait()
                self.__log.debug('Write data from queue to output file')
                for key in list(data.keys()):
                    # print(data[key])
                    if key not in file_writer.keys():
                        for cls in self.__classes:
                            if cls.__name__ == key:
                                self.__register_writer(cls, file_writer, tstmps, file_streams)
                    ts = data[key]['TIME']
                    id = data[key]['ID']
                    if id not in tstmps[key]:
                        tstmps[key][id] = 0
                    if ts >= tstmps[key][id] + self.__export_interval * self.__timestep:
                        values: list = data[key]['DATA']
                        if numpy.isnan(values).any():
                            self.__log.error('State ' + key + ' has NaN: ' + str(values))
                        file_writer[key].writerow(values)
                        tstmps[key][id] = ts
            except Empty:
                self.__log.debug("Empty Queue")
                time.sleep(0.01)
        self.__log.info('Write to output file finished')
        for stream in file_streams:
            stream.close()
        file_writer.clear()
        file_streams.clear()

    def __register_writer(self, cls, file_writer, tstmps, file_streams) -> None:
        self.__log.info('Registering ' + cls.__name__)
        file_name = self.__working_directory + cls.__name__ + self.EXT_CSV
        if self.USE_GZIP_COMPRESSION:
            file_stream = gzip.open(file_name + self.EXT_COMP, 'at' if self.__append else 'wt', newline='')
        else:
            file_stream = open(file_name, 'a' if self.__append else 'w', newline='')
        writer = csv.writer(file_stream)
        writer.writerow(cls.header())
        file_writer[cls.__name__] = writer
        tstmps[cls.__name__] = {}
        file_streams.append(file_stream)

    def transfer_data(self, data: dict) -> None:
        """
        Function to place data into the queue. This data is picked up by the run function and written into a CSV file_name.

        Parameters
        ----------
        data : list

        Returns
        -------

        """
        self.__queue.put(data)

    def simulation_done(self) -> None:
        """
        Function to let the DataExport Thread know that the simulation is done and stop after emptying the queue.

        Parameters
        ----------

        Returns
        -------

        """
        self.__simulation_running = False

    def copy_results_to_destination(self):
        """
        Transfer the resulting csv file_name as well as the configuration file_name to the destination folder defined in the
        class creation.

        Returns
        -------

        """
        copy_all_files(self.__working_directory, self.__result_folder)
        remove_all_files_from(self.__working_directory)

    def close(self) -> None:
        """
        Closing all open resources in data export

        Parameters
        ----------

        Returns
        -------

        """

        self.__log.debug('Simulation done')
        self.simulation_done()
        self.__log.debug('Waiting for export thread to finish')
        if self.is_alive():
            self.join()
        self.copy_results_to_destination()
        self.__log.close()

    @classmethod
    def get_data_from(cls, path: str, state_cls) -> pd.DataFrame:
        """
        Reads file for Class in path as pandas dataframe

        Parameters
        ----------
        path : Path of simulation results
        state_cls : State class

        Returns
        -------
        pandas.Dataframe:
            Data of file in path

        """
        filename: str = path + '/' + state_cls.__name__ + cls.EXT_CSV
        if cls.USE_GZIP_COMPRESSION:
            data: pd.DataFrame = pd.read_csv(filename + cls.EXT_COMP, compression=cls.COMP, header=0)
        else:
            data: pd.DataFrame = pd.read_csv(filename, header=0)
        # print('==== ' + state_cls.__name__ + ' ====')
        for key in data.keys():
            data[key] = pd.to_numeric(data[key], errors='coerce')
        # data = data.replace(np.nan, 0, regex=True)
        # print(data.dtypes)
        return data
