# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Optional, List
from abc import ABC, abstractmethod
import os
import pandas as pd
import sys

from azureml.core import Run
from azureml.automl.core.console_writer import ConsoleWriter


class AutoMLPRSDriverBase(ABC):
    """Base class for AutoML PRS run."""
    def __init__(
            self,
            current_step_run: Run
    ):
        """
        Base class for AutoML PRS run.

        :param current_step_run: The current step run.
        """
        self.current_step_run = current_step_run
        self._console_writer = ConsoleWriter(sys.stdout)

    @abstractmethod
    def run(self, input_data_file: str, output_data_file: str) -> Any:
        """Run method."""
        pass

    @staticmethod
    def read_input_data(data_path: str, parse_date: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Read input data from the data path specified.

        :param data_path: The path to the data.
        :param parse_date: Parse date for date columns if read csv file.
        :return: A DataFrame contains the data of the data_path.
        """
        _, file_extension = os.path.splitext(os.path.basename(data_path))
        if file_extension.lower() == ".parquet":
            data = pd.read_parquet(data_path)
        else:
            data = pd.read_csv(data_path, parse_dates=parse_date)
        return data
