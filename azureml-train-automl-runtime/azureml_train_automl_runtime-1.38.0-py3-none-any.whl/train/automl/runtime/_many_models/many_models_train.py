# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import tempfile
from typing import Any, cast, Dict, List, Union

import pandas as pd
from azureml.core import Run
from azureml.train.automl.runtime._many_models.automl_prs_run_base import AutoMLPRSRunBase
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.train.automl.runtime._many_models.automl_prs_driver_factory import AutoMLPRSDriverFactory


class ManyModelsTrain(AutoMLPRSRunBase):
    """
    This class is used for training one or more AutoML runs.
    """
    # This is the requested pipeline batch size.
    PIPELINE_FETCH_MAX_BATCH_SIZE = 15

    def __init__(
            self,
            current_step_run: Run,
            automl_settings: Dict[str, Any],
            process_count_per_node: int,
            retrain_failed_models: bool
    ):
        """
        This class is used for training one or more AutoML runs.
        :param current_step_run: Current step run object, parent of AutoML run.
        :param automl_settings: AutoML settings dictionary.
        :process_count_per_node: Process count per node.
        :retrain_failed_models: Retrain failed models flag.
        """

        super(ManyModelsTrain, self).__init__(
            current_step_run, automl_settings, process_count_per_node=process_count_per_node)

        self.automl_settings = cast(Dict[str, Any], self.automl_settings)
        self.retrain_failed_models = retrain_failed_models
        self.timestamp_column = self.automl_settings.get('time_column_name', None)  # type: str
        self.grain_column_names = self.automl_settings.get('grain_column_names', [])  # type: List[str]
        self.partition_column_names = self.automl_settings.get('partition_column_names', [])  # type: List[str]
        self.max_horizon = self.automl_settings.get('max_horizon', 0)  # type: int
        self.target_column = self.automl_settings.get('label_column_name', None)  # type: str
        self.automl_settings['many_models'] = True
        self.automl_settings['many_models_process_count_per_node'] = process_count_per_node
        self.automl_settings['pipeline_fetch_max_batch_size'] = self.automl_settings.get(
            'pipeline_fetch_max_batch_size', self.PIPELINE_FETCH_MAX_BATCH_SIZE)

        self._console_writer.println("max_horizon: {}".format(self.max_horizon))
        self._console_writer.println("target_column: {}".format(self.target_column))
        self._console_writer.println("timestamp_column: {}".format(self.timestamp_column))
        self._console_writer.println("partition_column_names: {}".format(self.partition_column_names))
        self._console_writer.println("grain_column_names: {}".format(self.grain_column_names))
        self._console_writer.println("retrain_failed_models: {}".format(retrain_failed_models))

        debug_log = self.automl_settings.get('debug_log', None)
        if debug_log is not None:
            self.automl_settings['debug_log'] = os.path.join(self.log_dir, debug_log)
            self.automl_settings['path'] = tempfile.mkdtemp()
            self._console_writer.println("{}.AutoML debug log:{}".format(__file__, automl_settings['debug_log']))

    def run(self, input_data: Union[pd.DataFrame, str]) -> pd.DataFrame:
        """
        Train one or more partitions of data

        :param input_data: Input dataframe or file.
        """

        self._console_writer.println("Entering run for MM automl_training ()")
        return super(ManyModelsTrain, self).run(input_data)

    def read_from_json(self, snapshot_dir):
        """
        Read automl settings from snapshot directory.

        :param snapshot_dir: Snapshot directory.
        """
        with open(str(snapshot_dir) + "/automl_settings.json") as json_file:
            return json.load(json_file)

    def get_prs_run_arguments(self):
        """Get the argument for prs run."""
        return Arguments(self.process_count_per_node, retrain_failed_models=self.retrain_failed_models)

    def format_temp_parquet_name(self, input_data: pd.DataFrame) -> str:
        """Get the formatted temporary parquet file name."""
        group_columns_dict = {}
        for column_name in self.partition_column_names:
            group_columns_dict.update(
                {column_name: str(input_data.iat[0, input_data.columns.get_loc(column_name)])})
        model_string = '_'.join(str(v)
                                for k, v in sorted(group_columns_dict.items()))
        return "train_tabular_input_{}.parquet".format(model_string)

    def get_run_result(self, output_file_path: str) -> pd.DataFrame:
        """Get the result of the run."""
        self._console_writer.println(output_file_path)
        logs = self.metadata_file_handler.load_logs()
        self.metadata_file_handler.delete_logs_file_if_exists()
        self._console_writer.println(str(logs))
        return pd.DataFrame(data=[logs])

    def get_automl_run_prs_scenario(self) -> str:
        """Get the PRS run scenario."""
        return AutoMLPRSDriverFactory.MANY_MODELS_AUTOML_TRAIN
