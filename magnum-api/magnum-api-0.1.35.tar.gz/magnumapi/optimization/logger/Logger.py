import os
from typing import Dict, List

import pandas as pd

from magnumapi.optimization.constants import SCORE_KEYWORD, PENALTY
from magnumapi.optimization.design_variable.Individual import Individual


class Logger:
    """ Class for logging of genetic optimization progress.

    """
    def __init__(self, logger_abs_path: str) -> None:
        """ A constructor of a Logger instance

        :param logger_abs_path: an absolute path to logger output
        """
        self.logs: List[pd.DataFrame, ...] = []
        self.logger_abs_path = logger_abs_path

    def append_to_logger(self, individual_dct: Dict) -> None:
        """ Abstract method updating model parameters

        :param individual_dct: a dictionary with a individual
        """
        self.logs.append(pd.DataFrame(individual_dct, index=[0]))

    def get_logger_df(self) -> pd.DataFrame:
        """ Method concatenating and returning a logger dataframe with values of the design variables and objective
        function results.

        :return: a logger dataframe
        """
        if self.logs:
            return pd.concat(self.logs).reset_index(drop=True)

    def save_logger(self) -> None:
        """ Method saving logger as a csv file

        """
        if self.logger_abs_path:
            self.get_logger_df().to_csv(self.logger_abs_path)

    def get_mean_fitness_per_generation(self, n_pop) -> pd.DataFrame:
        """ Method calculating the mean fitness per each generation and returning a dataframe with one row per each
        generation. Penalized objective values are excluded from the calculation.

        :param logger_df: full logger dataframe with each row containing information about an individual
        :return: dataframe with one row per each generation of average fitness
        """
        if not self.logs:
            return pd.DataFrame()

        logger_df = self.get_logger_df()
        return self.calculate_mean_of_rows_from_logger_df(logger_df, n_pop)

    @staticmethod
    def calculate_mean_of_rows_from_logger_df(logger_df, n_pop):
        mean_logger_dfs = []
        for index in range(0, len(logger_df), n_pop):
            sub_logger_df = logger_df[(logger_df.index >= index) & (logger_df.index < index + n_pop)]
            sub_logger_df = sub_logger_df[sub_logger_df[SCORE_KEYWORD] < PENALTY]
            mean_logger_dfs.append(sub_logger_df[SCORE_KEYWORD].mean())
        return pd.DataFrame(mean_logger_dfs, columns=[SCORE_KEYWORD])

    def get_min_fitness_per_generation(self, n_pop: int) -> pd.DataFrame:
        """ Method calculating the min fitness per each generation and returning a dataframe with one row per each
        generation.

        :param logger_df: full logger dataframe with each row containing information about an individual
        :return: dataframe with one row per each generation of minimum fitness
        """
        if not self.logs:
            return pd.DataFrame()

        logger_df = self.get_logger_df()
        return Logger.extract_min_rows_from_logger_df(logger_df, n_pop)

    @staticmethod
    def extract_min_rows_from_logger_df(logger_df: pd.DataFrame, n_pop: int) -> pd.DataFrame:
        min_logger_dfs = []
        for index in range(0, len(logger_df), n_pop):
            sub_logger_df = logger_df[(logger_df.index >= index) & (logger_df.index < index + n_pop)]
            idx_min = sub_logger_df[SCORE_KEYWORD].idxmin()
            min_logger_dfs.append(logger_df[logger_df.index == idx_min])
        return pd.concat(min_logger_dfs).reset_index()

    def append_individuals_to_logger(self, individuals: List[Individual]) -> None:
        for individual in individuals:
            self.append_to_logger(individual.to_dict())
