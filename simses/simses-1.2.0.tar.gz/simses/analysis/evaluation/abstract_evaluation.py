import csv
import os
from abc import ABC, abstractmethod
import numpy
import pandas
from simses.analysis.data.abstract_data import Data
from simses.analysis.evaluation.result import EvaluationResult
from simses.commons.config.analysis.general import GeneralAnalysisConfig
from simses.commons.log import Logger
from simses.commons.state.abstract_state import State
from simses.commons.utils.utilities import create_directory_for


class Evaluation(ABC):

    """
    Within the evaluation class the analysis of each system and storage technology is conducted. It provides results
    in form of figures and KPIs. The analysis calculations are done with the help of data object provided which accesses
    the simulation data.
    """

    EXT: str = '.csv'

    def __init__(self, data: Data, config: GeneralAnalysisConfig, do_evaluation: bool):
        self.__log: Logger = Logger(__name__)
        self.__data: Data = data
        self.__do_evaluation: bool = do_evaluation
        self.__do_plotting: bool = config.plotting and do_evaluation
        self._print_to_console: bool = config.print_result_to_console and do_evaluation
        self.__export_analysis_to_csv: bool = config.export_analysis_to_csv and do_evaluation
        self.__export_analysis_to_batch: bool = config.export_analysis_to_batch and do_evaluation
        self.__file_name: str = type(self).__name__ + self.__data.id + self.EXT
        self.__evaluation_results: [EvaluationResult] = list()
        self.__time_series: dict = dict()
        self.__files_to_transpose: [str] = list()
        self.__figures: list = list()

    @property
    def evaluation_results(self) -> [EvaluationResult]:
        return self.__evaluation_results

    def append_result(self, evaluation_result: EvaluationResult) -> None:
        self.__evaluation_results.append(evaluation_result)

    def extend_results(self, evaluation_results: [EvaluationResult]) -> None:
        self.__evaluation_results.extend(evaluation_results)

    def append_figure(self, figure) -> None:
        self.__figures.append(figure)

    def extend_figures(self, figures: list) -> None:
        self.__figures.extend(figures)

    def append_time_series(self, name: str, time_series: numpy.ndarray):
        self.__time_series.update({name: time_series})

    def get_files_to_transpose(self) -> [str]:
        return self.__files_to_transpose

    def get_data(self):
        return self.__data

    def get_figures(self) -> list:
        return self.__figures

    def get_file_name(self) -> str:
        return self.__file_name

    @property
    def get_name(self) -> str:
        return type(self.__data).__name__

    @property
    def should_be_considered(self) -> bool:
        return self.__do_evaluation

    def run(self) -> None:
        if self.__do_evaluation:
            self.evaluate()
            if self.__do_plotting:
                self.plot()

    @abstractmethod
    def evaluate(self) -> None:
        pass

    @abstractmethod
    def plot(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    def print_results(self):
        if not self._print_to_console:
            return
        print('\n[' + str(self.get_name).upper() + ' ANALYSIS]' + ' (System ' + self.__data.id + ')')
        for evaluation_result in self.evaluation_results:
            print(evaluation_result.to_console())

    def write_to_csv(self, path: str) -> None:
        if not self.__export_analysis_to_csv:
            return
        file = path + self.__file_name
        with open(file, 'w', newline='') as file:
            writer = csv.writer(file)
            for evaluation_result in self.evaluation_results:
                writer.writerow(evaluation_result.to_csv())

    def write_to_batch(self, path: str, name: str, run: str) -> None:
        if not self.__export_analysis_to_batch:
            return
        create_directory_for(path)
        for evaluation_result in self.evaluation_results:
            file_name = path + evaluation_result.description + self.EXT
            output: list = [name, run, self.get_name, self.__data.id, evaluation_result.value, evaluation_result.unit]
            self.__append_to_file(file_name, output)
        for ts_name, time_series in self.__time_series.items():
            file_name: str = path + ts_name + self.EXT
            if file_name not in self.__files_to_transpose:
                self.__files_to_transpose.append(file_name)
            if not os.path.exists(file_name):
                output: list = [State.TIME]
                output.extend(self.__data.time.tolist())
                self.__append_to_file(file_name, output)
            id: str = name + '_' + run + '_' + self.get_name + '_' + self.__data.id
            output: list = [id]
            output.extend(time_series.tolist())
            self.__append_to_file(file_name, output)
            # data_frame: pandas.DataFrame = pandas.read_csv(file_name, header=0, index=None)
            # data_frame[column_id] = time_series
            # data_frame.to_csv(file_name, index=None)

    def __append_to_file(self, file_name: str, data: list) -> None:
        try:
            with open(file_name, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data)
        except FileNotFoundError:
            self.__log.error(file_name + ' could not be found')

    @classmethod
    def transpose_files(cls, files: [str]) -> None:
        transposed: [str] = list()
        for file in files:
            if file not in transposed and os.path.exists(file):
                pandas.read_csv(file, header=None).T.to_csv(
                    file.replace(cls.EXT, '_T' + cls.EXT), header=False, index=False)
                transposed.append(file)
