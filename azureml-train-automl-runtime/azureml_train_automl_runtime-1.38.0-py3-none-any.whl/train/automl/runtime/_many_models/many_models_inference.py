# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Optional, Union

import pandas as pd
from azureml.core import Run
from pandas.core.frame import DataFrame

from azureml.train.automl.runtime._many_models.automl_prs_run_base import AutoMLPRSRunBase
from azureml.train.automl.runtime._many_models.automl_prs_driver_factory import AutoMLPRSDriverFactory
from azureml.train.automl.runtime._many_models.train_helper import Arguments


class ManyModelsInference(AutoMLPRSRunBase):
    """This class is used for doing batch inference."""

    def __init__(self,
                 current_step_run: Run,
                 partition_column_names: List[str],
                 target_column_name: Optional[str],
                 time_column_name: Optional[str],
                 train_run_id: Optional[str],
                 forecast_quantiles: Optional[List[float]] = None):
        """
        This class is used for doing batch inference.

        :param current_step_run: Current step run object, parent of AutoML run.
        :param partition_column_names: Partition column names.
        :param target_column_name: The target column name. Needs to be passed only if inference data contains target.
        :param time_column_name: The time column name, op
        :param train_run_id: The training pipeline run id.
        :param forecast_quantiles: Inference using forecast_quantiles.
        """
        super(ManyModelsInference, self).__init__(current_step_run)
        self.partition_column_names = partition_column_names
        self.target_column_name = target_column_name
        self.time_column_name = time_column_name
        self.train_run_id = train_run_id
        self.forecast_quantiles = forecast_quantiles
        self._console_writer.println("partition_column_names: {}".format(self.partition_column_names))
        self._console_writer.println("target_column_name: {}".format(self.target_column_name))
        self._console_writer.println("time_column_name: {}".format(self.time_column_name))
        self._console_writer.println("train_run_id: {}".format(self.train_run_id))
        self._console_writer.println("forecast_quantiles: {}".format(self.forecast_quantiles))

    def run(self, input_data: Union[List[str], DataFrame]) -> DataFrame:
        """
        Perform batch inference on specified partition(s) of data

        :param input_data: Input dataframe or file.
        :return: A dataframe that contains the results.
        """
        print('Making predictions')
        all_predictions = super(ManyModelsInference, self).run(input_data)
        self._console_writer.println(str(all_predictions.head()))
        return all_predictions

    def get_automl_run_prs_scenario(self):
        """Get the prs run scenario."""
        return AutoMLPRSDriverFactory.MANY_MODELS_INFERENCE

    def get_prs_run_arguments(self) -> Arguments:
        """Get the arguments for PRS run."""
        return Arguments(
            train_run_id=self.train_run_id,
            target_column_name=self.target_column_name,
            time_column_name=self.time_column_name,
            forecast_quantiles=self.forecast_quantiles,
            partition_column_names=self.partition_column_names
        )

    def get_run_result(self, output_file: str) -> pd.DataFrame:
        """
        Get the result of the run.

        :param output_file: The output data file the contains the results.
        :return: A dataframe that contains the result.
        """
        return pd.read_parquet(output_file)
