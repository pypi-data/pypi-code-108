from abc import ABC, abstractmethod

import pandas as pd


class ToolAdapter(ABC):
    """An abstract class providing requirements for a ToolAdapter implementation

    """

    @abstractmethod
    def run(self) -> None:
        """ Abstract method running a tool adapter

        """
        raise NotImplementedError('This method is not implemented for this class')

    @staticmethod
    @abstractmethod
    def convert_figures_of_merit_to_dict(fom_df: pd.DataFrame) -> dict:
        """ Abstract method converting a dataframe with figures of merit into a dictionary

        :return: a dictionary mapping a figure of merit name to its value
        """
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def read_figures_of_merit_table(self) -> pd.DataFrame:
        """ Abstract method reading a dataframe with figures of merit

        :return: a dataframe with figures of merit
        """
        raise NotImplementedError('This method is not implemented for this class')