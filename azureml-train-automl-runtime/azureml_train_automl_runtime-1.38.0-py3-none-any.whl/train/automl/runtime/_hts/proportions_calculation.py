# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, Optional, List, cast
from functools import partial
import json
import logging
import math
import multiprocessing
import os
import pandas as pd
import sys

from azureml.core import Run
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.automl.core._logging.event_logger import EventLogger
from azureml.train.automl.constants import HTSConstants
import azureml.train.automl._hts.hts_client_utilities as cu
from azureml.train.automl.runtime._hts.hts_graph import Graph
import azureml.train.automl.runtime._hts.hts_events as hts_events
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.train.automl.runtime._hts.hts_runtime_json_serializer import HTSRuntimeDecoder
from azureml.train.automl.runtime._hts.node_columns_info import NodeColumnsInfo
from azureml.train.automl.runtime._many_models.automl_pipeline_step_wrapper import AutoMLPythonStepWrapper


logger = logging.getLogger(__name__)


class ProportionsCalculationWrapper(AutoMLPythonStepWrapper):
    """The wrapper code for proportions calculation runs."""
    def __init__(self, current_step_run: Optional[Run] = None):
        """
        The wrapper code for proportions calculation runs.

        :param current_step_run: The current step run.
        """
        super(ProportionsCalculationWrapper, self).__init__(
            HTSConstants.STEP_PROPORTIONS_CALCULATION, current_step_run
        )

    def _run(self) -> None:
        """Run code for the proportions calculation driver."""
        proportions_calculation(self.arguments_dict, self.event_logger, script_run=self.step_run)


def _get_files_batches_sqrt(files_list: List[str]) -> List[List[str]]:
    """
    Covert a list of files to a list of files batches which
    contains approximately sqrt(total_files) in each batch.

    :param files_list: A list of files.
    :return: List[List[str]]
    """
    n_files = len(files_list)
    n_batch = int(math.sqrt(n_files)) + 1
    files_batches = []
    for i in range(n_batch):
        if i * n_batch < n_files:
            end_idx = n_files if (i + 1) * n_batch > n_files else (i + 1) * n_batch
            files_batches.append(files_list[i * n_batch:end_idx])
    return files_batches


def _concat_and_sum_by_time_for_files(
        file_names: List[str], file_dir: str, time_column_name: str, label_column_name: str
) -> pd.DataFrame:
    """Concat all the df from the datafiles and return the time column absolute summation over label_column_name."""
    dfs = []
    for f in file_names:
        dfs.append(pd.read_csv(os.path.join(file_dir, f))[[time_column_name, label_column_name]])
    return hru.abs_sum_target_by_time(pd.concat(dfs), time_column_name, label_column_name)


def calculate_time_agg_sum_for_all_files(
        proportion_files_list: List[str], time_column_name: str, label_column_name: str) -> pd.DataFrame:
    """
    Calculate groupby time aggregation for all files using multi core processing.

    :param proportion_files_list: A list of proportion calculated csv files.
    :param time_column_name: The time column name.
    :param label_column_name: The label column name.
    :return: pd.DataFrame
    """
    files_batches = _get_files_batches_sqrt(proportion_files_list)

    n_cpus = multiprocessing.cpu_count()
    concat_func = partial(
        _concat_and_sum_by_time_for_files,
        file_dir=os.curdir, time_column_name=time_column_name, label_column_name=label_column_name)
    with multiprocessing.Pool(n_cpus) as pool:
        df = pd.concat(pool.map(concat_func, files_batches), ignore_index=True)
    return hru.abs_sum_target_by_time(df, time_column_name, label_column_name)


def get_proportions_metadata_json(metadata_df: pd.DataFrame, graph: Graph) -> Dict[str, Any]:
    """
    Convert a pd.DataFrame containing proportion information to a json dict.

    :param metadata_df: The input dataframe.
    :param graph: The hts graph.
    :return: Dict[str, Any]
    """
    metadata_json_dict = {HTSConstants.JSON_VERSION: "1.0"}  # type: Dict[str, Any]
    metadata = []
    for _, row in metadata_df.iterrows():
        node_metadata = {
            col: row[col] for col in [HTSConstants.PROPORTIONS_OF_HISTORICAL_AVERAGE,
                                      HTSConstants.AVERAGE_HISTORICAL_PROPORTIONS]}
        node_metadata[HTSConstants.NODE_ID] = graph.get_node_by_name_list_raise_none(
            graph.get_leaf_node_name_list(row)).node_id
        metadata.append(node_metadata)
    metadata_json_dict[HTSConstants.METADATA_JSON_METADATA] = metadata
    return metadata_json_dict


def proportions_calculation(
        arguments_dict: Dict[str, str],
        event_logger: EventLogger,
        script_run: Optional[Run] = None
) -> None:
    """
    Collect all the training metadata and calculate the proportions.

    :param arguments_dict: The arguments dict needed for the calculation.
    :param event_logger: The event logger.
    :param script_run: A run object that the script is running.
    :return: None
    """
    custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_PROPORTIONS_CALCULATION)
    hru.update_log_custom_dimension(custom_dim)
    console_writer = ConsoleWriter(sys.stdout)
    local_mode = script_run is not None

    logger.info("Retrieving graph now.")
    parent_run = hru.get_pipeline_run(script_run)

    event_logger_additional_fields = hru.get_event_logger_additional_fields(custom_dim, parent_run.id)
    event_logger.log_event(hts_events.HTSPropCalcStart(event_logger_additional_fields))
    input_data = arguments_dict[HTSConstants.METADATA_INPUT]
    graph = Graph.get_graph_from_file(arguments_dict[HTSConstants.HTS_GRAPH])

    settings = cu.get_settings_dict(".")
    forecasting_parameters = cu.get_forecasting_parameters(settings)

    run_status_records = []
    explanation_status_records = []
    column_vocabulary_data = []
    proportion_files_list = []
    event_logger.log_event(hts_events.HTSPropCalcProcessFile(event_logger_additional_fields))
    for data_file in os.listdir(input_data):
        file_type = hru.get_intermediate_file_postfix(data_file)
        console_writer.println("processing: {} with type {}.".format(data_file, file_type))
        if file_type == HTSConstants.HTS_FILE_POSTFIX_RUN_INFO_JSON:
            with open(os.path.join(input_data, data_file)) as f:
                run_status_records.append(json.load(f, cls=HTSRuntimeDecoder))
        if file_type == HTSConstants.HTS_FILE_POSTFIX_EXPLANATION_INFO_JSON:
            with open(os.path.join(input_data, data_file)) as f:
                explanation_status_records.append(json.load(f, cls=HTSRuntimeDecoder))
        if file_type == HTSConstants.HTS_FILE_POSTFIX_NODE_COLUMNS_INFO_JSON:
            with open(os.path.join(input_data, data_file)) as f:
                node_column_info = cast(NodeColumnsInfo, json.load(f, cls=HTSRuntimeDecoder))
                node = graph.get_node_by_id(node_column_info.node_id)
                column_vocabulary_data.append(node_column_info)
                if node is not None:
                    node.ignored_columns_types_dict = node_column_info.get_ignored_columns_dict(
                        graph.agg_exclude_columns)
        if file_type == HTSConstants.HTS_FILE_POSTFIX_METADATA_CSV:
            proportion_files_list.append(os.path.join(input_data, data_file))

    event_logger.log_event(hts_events.HTSPropCalcTimeSum(event_logger_additional_fields))
    df_cross_time_agg = calculate_time_agg_sum_for_all_files(
        proportion_files_list, forecasting_parameters.time_column_name, graph.label_column_name
    )

    n_points = hru.get_n_points(
        df_cross_time_agg,
        forecasting_parameters.time_column_name,
        graph.label_column_name,
        forecasting_parameters.freq)
    total_value = df_cross_time_agg[graph.label_column_name].sum()

    dfs = []
    for proportion_file in proportion_files_list:
        df = pd.read_csv(proportion_file)
        df_ahp = hru.calculate_average_historical_proportions(
            n_points, df, df_cross_time_agg, forecasting_parameters.time_column_name,
            graph.label_column_name, graph.hierarchy)
        df_pha = hru.calculate_proportions_of_historical_average(
            df, graph.label_column_name, graph.hierarchy, total_value)
        dfs.append(pd.merge(df_ahp, df_pha))

    proportions_data = pd.concat(dfs)

    event_logger.log_event(hts_events.HTSPropCalcUpload(event_logger_additional_fields))
    hru.upload_object_to_artifact_json_file(
        explanation_status_records, HTSConstants.HTS_FILE_EXPLANATION_INFO_JSON, parent_run, local_mode)
    hru.upload_object_to_artifact_json_file(
        run_status_records, HTSConstants.HTS_FILE_RUN_INFO_JSON, parent_run, local_mode)
    hru.check_parallel_runs_status(
        run_status_records, HTSConstants.STEP_AUTOML_TRAINING, HTSConstants.HTS_FILE_RUN_INFO_JSON)

    logger.info("Uploading graph file,")
    hru.upload_object_to_artifact_json_file(
        graph.serialize(), HTSConstants.GRAPH_JSON_FILE, parent_run, local_mode)
    logger.info("Uploading proportion data,")
    hru.upload_object_to_artifact_json_file(
        get_proportions_metadata_json(proportions_data, graph),
        HTSConstants.HTS_FILE_PROPORTIONS_METADATA_JSON, parent_run, local_mode)
    hru.upload_object_to_artifact_json_file(
        column_vocabulary_data, HTSConstants.HTS_FILE_NODE_COLUMNS_INFO_JSON, parent_run, local_mode)
    console_writer.println("Uploaded metadata files.")
    event_logger.log_event(hts_events.HTSPropCalcEnd(event_logger_additional_fields))
