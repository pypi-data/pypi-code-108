# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Optional
import os
import pickle

from azureml.train.automl.runtime._hts.hts_graph import Graph
from azureml.train.automl.runtime._hts.node_columns_info import NodeColumnsInfo


class MetadataFileHandler:
    """ This class is used for writing and reading run metadata"""
    # Metadata file names
    ARGS_FILE_NAME = "args.pkl"
    AUTOML_SETTINGS_FILE_NAME = "automl_settings.pkl"
    LOGS_FILE_NAME = "logs.pkl"
    RUN_DTO_FILE_NAME = "run_dto.pkl"

    def __init__(self, data_dir: str):
        """ This class is used for writing and reading run metadata"""
        # Directory where metadata files live
        self.data_dir = data_dir

        # Full paths to metadata files
        self._args_file_path = os.path.join(self.data_dir, self.ARGS_FILE_NAME)
        self._automl_settings_file_path = os.path.join(self.data_dir, self.AUTOML_SETTINGS_FILE_NAME)
        self._logs_file_path = os.path.join(self.data_dir, self.LOGS_FILE_NAME)
        self._run_dto_file_name = os.path.join(self.data_dir, self.RUN_DTO_FILE_NAME)

    def delete_logs_file_if_exists(self):
        if not os.path.exists(self._logs_file_path):
            return
        os.remove(self._logs_file_path)

    def load_automl_settings(self):
        return self.load_obj_from_disk(self._automl_settings_file_path)

    def load_args(self):
        return self.load_obj_from_disk(self._args_file_path)

    def load_logs(self):
        return self.load_obj_from_disk(self._logs_file_path)

    def load_run_dto(self):
        return self.load_obj_from_disk(self._run_dto_file_name)

    def write_args_to_disk(self, args):
        self.serialize_obj_to_disk(args, self._args_file_path)

    def write_automl_settings_to_disk(self, automl_settings):
        self.serialize_obj_to_disk(automl_settings, self._automl_settings_file_path)

    def write_logs_to_disk(self, logs):
        self.serialize_obj_to_disk(logs, self._logs_file_path)

    def write_run_dto_to_disk(self, run_dto):
        self.serialize_obj_to_disk(run_dto, self._run_dto_file_name)

    @classmethod
    def load_obj_from_disk(cls, file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    @classmethod
    def serialize_obj_to_disk(cls, obj, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(obj, f)


class Arguments:
    """
    This class is used to hold the arguments that the AutoML PRS run needed.

    :param process_count_per_node: The number of processes per node.
    :param retrain_failed_models: Retrain the failed models.
    :param train_run_id: training run ID.
    :param target_column_name: The name of a target column.
    :param forecast_quantiles: The percentiles to be generated for the forecast.
    :param partition_column_names: The column names used to partition data set.
    :param hts_graph: hierarchical time series graph.
    :param output_path: The path to output files.
    :param target_path: The data store to be used to upload processed data.
    :param node_columns_info: the information about link between node id and columns in the data.
    :param input_metadata: The metadata on how the data set was aggregated to training level.
    :param engineered_explanation: If True, the engineering explanations will be generated.
    :param event_logger_dim: The dimensions to be logged.
    """

    def __init__(
            self,
            process_count_per_node: Optional[int] = None,
            retrain_failed_models: Optional[bool] = None,
            train_run_id: Optional[str] = None,
            target_column_name: Optional[str] = None,
            time_column_name: Optional[str] = None,
            forecast_quantiles: Optional[List[float]] = None,
            partition_column_names: Optional[List[str]] = None,
            hts_graph: Optional[Graph] = None,
            output_path: Optional[str] = None,
            target_path: Optional[str] = None,
            node_columns_info: Optional[Dict[str, NodeColumnsInfo]] = None,
            input_metadata: Optional[str] = None,
            engineered_explanation: Optional[bool] = None,
            event_logger_dim: Optional[Dict[str, str]] = None,
            enable_event_logger: Optional[bool] = False
    ) -> None:
        """
        This class is used to hold the arguments that the AutoML PRS run needed.

        :param process_count_per_node: The number of processes per node.
        :param retrain_failed_models: Retrain the failed models.
        :param train_run_id: training run ID.
        :param target_column_name: The name of a target column.
        :param forecast_quantiles: The percentiles to be generated for the forecast.
        :param partition_column_names: The column names used to partition data set.
        :param hts_graph: hierarchical time series graph.
        :param output_path: The path to output files.
        :param target_path: The data store to be used to upload processed data.
        :param node_columns_info: the information about link between node id and columns in the data.
        :param input_metadata: The metadata on how the data set was aggregated to training level.
        :param engineered_explanation: If True, the engineering explanations will be generated.
        :param event_logger_dim: The dimensions to be logged.
        """
        self.process_count_per_node = process_count_per_node
        self.retrain_failed_models = retrain_failed_models
        # used for MM inference.
        self.train_run_id = train_run_id
        self.target_column_name = target_column_name
        self.time_column_name = time_column_name
        self.forecast_quantiles = forecast_quantiles
        self.partition_column_names = partition_column_names
        # used for HTS
        self.hts_graph = hts_graph
        self.output_path = output_path
        self.target_path = target_path
        self.event_logger_dim = event_logger_dim
        self.node_columns_info = node_columns_info
        self.input_metadata = input_metadata
        self.engineered_explanation = engineered_explanation
        self.enable_event_logger = enable_event_logger
