# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional
import json
import logging
import os
import pandas as pd
import sys

from azureml.core import Run, Dataset
from azureml.automl.core.shared._diagnostics.automl_events import RunSucceeded, RunFailed
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.train.automl.constants import HTSConstants
import azureml.train.automl._hts.hts_client_utilities as cu
from azureml.automl.core._logging.event_logger import EventLogger
import azureml.train.automl.runtime._hts.hts_events as hts_events
from azureml.train.automl.runtime._hts.hts_graph import Graph
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    DataFromMultipleGroups,
    InputDatasetEmpty,
    InvalidInputDatatype
)
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException
from azureml.train.automl.runtime._many_models.automl_pipeline_step_wrapper import AutoMLPythonStepWrapper


logger = logging.getLogger(__name__)
console_writer = ConsoleWriter(sys.stdout)


class HierarchyBuilderWrapper(AutoMLPythonStepWrapper):
    """The wrapper code for hierarchy builder runs."""
    def __init__(self, current_step_run: Optional[Run] = None):
        """
        The wrapper code for hierarchy builder runs.

        :param current_step_run: The current step run.
        """
        super(HierarchyBuilderWrapper, self).__init__(
            HTSConstants.STEP_HIERARCHY_BUILDER, current_step_run
        )

    def _run(self) -> None:
        """Run code for the hierarchy builder driver."""
        hierarchy_builder(self.arguments_dict, self.event_logger, script_run=self.step_run)


def hierarchy_builder_runtime_wrapper():
    current_step_run = Run.get_context()
    try:
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_HIERARCHY_BUILDER)
        arguments_dict = hru.get_arguments_dict(HTSConstants.STEP_HIERARCHY_BUILDER)
        hru.init_logger(
            module=sys.modules[__name__], handler_name=__name__, custom_dimensions=custom_dim, run=current_step_run)
        logger.info("Pre proportion calculation wrapper started.")
        event_logger = EventLogger(current_step_run)
        hierarchy_builder(arguments_dict, event_logger, script_run=current_step_run)
        logger.info("Pre proportion calculation wrapper completed.")
        event_logger.log_event(RunSucceeded(
            current_step_run.id, hru.get_event_logger_additional_fields(custom_dim, current_step_run.parent.id)))
    except Exception as e:
        error_code, error_str = run_lifecycle_utilities._get_error_code_and_error_str(e)
        failure_event = RunFailed(
            run_id=current_step_run.id, error_code=error_code, error=error_str,
            additional_fields=hru.get_event_logger_additional_fields(custom_dim, current_step_run.parent.id))
        run_lifecycle_utilities.fail_run(current_step_run, e, failure_event=failure_event)
        raise


def _check_mounted_file_dataset(mounted_path: str) -> None:
    """
    Check if mounted FileDataset path point to a single file. If so, throw DataException.

    :param mounted_path: The mounted FileDataset path.
    """
    if os.path.isfile(mounted_path):
        raise DataException._with_error(
            AzureMLError.create(
                InvalidInputDatatype,
                target="input_data",
                input_type="FileDataset with single file",
                supported_types="FileDataset with multiple .csv or .parquet",
                reference_code=ReferenceCodes._HTS_INVALID_FILE_DATASET
            )
        )


def check_valid_file_type(files_list: List[str]) -> None:
    """
    Check whether data files used for training have valid type.

    :param files_list: A list of files.
    :raises: DataException
    """
    if all([not hru.is_supported_data_file(f) for f in files_list]):
        raise DataException._with_error(
            AzureMLError.create(
                InputDatasetEmpty, target="InputDataset",
                reference_code=ReferenceCodes._HTS_PRE_PROPORTIONS_EMPTY_DATA
            )
        )


def validate_df_node_uniqueness(df: pd.DataFrame, graph: Graph, file_name: str) -> None:
    """
    Validate the dataframe contains unique values for the training level of a graph.

    :param df: The input dataframe.
    :param graph: The graph.
    :param file_name: The file name associate with the input dataframe
    :return: None
    """
    unique_df = df.groupby(graph.hierarchy_to_training_level).size().reset_index(name='number_of_rows')
    if unique_df.shape[0] > 1:
        raise DataException._with_error(
            AzureMLError.create(
                DataFromMultipleGroups, target=file_name, file_name=file_name, unique_df_summary=unique_df.head(5),
                reference_code=ReferenceCodes._HTS_PRE_PROPORTIONS_DATA_FROM_MULTIPLE_GROUP
            )
        )


def get_training_level_node_file_dict(graph: Graph, file_path: str, settings: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Get a dict containing the information between training level node ids and related files.

    :param graph: The HTS graph.
    :param file_path: The dir contains all the data files.
    :param settings: The HTS settings dict used to validate each file.
    :return: Dict[str, List[str]]
    """
    node_files_dict = {}  # type: Dict[str, List[str]]
    expected_cols = None
    all_files = []
    for d, _, files in os.walk(file_path):
        console_writer.println("Found files {} in dir {}.".format(", ".join(files), d))
        for f in files:
            all_files.append(os.path.join(d, f))

    check_valid_file_type(all_files)
    total_files = len(all_files)
    logger.info("Found {} files in the input dataset.".format(total_files))
    file_count = 0
    for f in all_files:
        file_count += 1
        if hru.is_supported_data_file(f):
            console_writer.println(
                "Supported file {}, processing now.  completed {}/{} files".format(f, file_count, total_files))
            df = hru.load_data(os.path.join(file_path, f))
            logger.info("The input size is {} and data file size is {}".format(
                df.shape, os.path.getsize(os.path.join(file_path, f))
            ))

            if expected_cols is None:
                expected_cols = df.columns
                cu.validate_settings(settings, expected_cols)
            cu.validate_column_consistent(expected_cols, df.columns, "file {}".format(f))

            graph.make_or_update_hierarchy(df)

            if graph.training_level != HTSConstants.HTS_ROOT_NODE_LEVEL:
                validate_df_node_uniqueness(df, graph, f)
            node_id = graph.get_training_level_node_by_df_first_row_raise_none(df).node_id
            if node_files_dict.get(node_id) is None:
                node_files_dict[node_id] = [f]
            else:
                node_files_dict[node_id].append(f)
        else:
            console_writer.println("Unsupported file {}, ignoring it now.".format(f))
    return node_files_dict


def generate_collected_files(
        node_files_dict: Dict[str, List[str]],
        origin_file_path: str,
        target_file_path: str
) -> None:
    """
    Generate collected csv files for each node based on the node_files_list and remove the origin files.

    :param node_files_dict: A nodes-file lists dict.
    :param origin_file_path: The input file path.
    :param target_file_path: The output file path.
    :return:
    """
    os.makedirs(target_file_path, exist_ok=True)
    for node_id, file_list in node_files_dict.items():
        file_name = '{}.csv'.format(node_id)
        data_df = None
        for f in file_list:
            origin_file = os.path.join(origin_file_path, f)
            temp_df = pd.read_csv(origin_file)
            data_df = hru.concat_df_with_none(data_df, temp_df)
        if data_df is not None:
            data_df.to_csv(os.path.join(target_file_path, file_name), index=False)
        else:
            logger.warning("Data df for node_id {} is None.".format(node_id))


def get_data_collect_summary(node_files_dict: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Get the data collection summary json dict based on the node-files dict.

    :param node_files_dict: The dict contains node-file relation.
    :return: Dict[str, Any]
    """
    summary = {HTSConstants.JSON_VERSION: 1.0, HTSConstants.COLLECT_SUMMARY_JSON_SUMMARY: []}  # type: Dict[str, Any]
    for node_id, file_names in node_files_dict.items():
        summary[HTSConstants.COLLECT_SUMMARY_JSON_SUMMARY].append({
            HTSConstants.COLLECT_SUMMARY_JSON_AGG_FILE: "{}.csv".format(node_id),
            HTSConstants.COLLECT_SUMMARY_JSON_ORIGIN_FILE: file_names})
    return summary


def hierarchy_builder(
        arguments_dict: Dict[str, str],
        event_logger: EventLogger,
        script_run: Optional[Run] = None
) -> None:
    """
    The driver code for pre_proportions_calculation step.

    :param arguments_dict: The arguments dict.
    :param event_logger: The event logger.
    :param script_run: A run object that the script is running.
    :return: None
    """
    custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_HIERARCHY_BUILDER)
    hru.update_log_custom_dimension(custom_dim)
    local_mode = True
    if script_run is None:
        logger.info("Getting RunContext now.")
        script_run = Run.get_context()
        local_mode = False
    event_logger_additional_fields = hru.get_event_logger_additional_fields(custom_dim, script_run.parent.id)
    event_logger.log_event(hts_events.HierarchyBuilderDriverStart(event_logger_additional_fields))
    working_dir = os.curdir
    output_path = os.path.join(working_dir, arguments_dict[HTSConstants.OUTPUT_PATH])
    collected_data_path = arguments_dict[HTSConstants.BLOB_PATH]

    # retrieve automl settings
    logger.info("Retrieving all the settings now.")
    settings = cu.get_settings_dict(working_dir)
    forecasting_parameters = cu.get_forecasting_parameters(settings)
    hierarchy = cu.get_hierarchy(settings)

    parent_run = hru.get_pipeline_run(script_run)
    parent_run.add_properties({
        HTSConstants.HTS_PROPERTIES_RUN_TYPE: HTSConstants.HTS_PROPERTIES_TRAINING,
        HTSConstants.HTS_PROPERTIES_SETTINGS: json.dumps(settings),
    })

    graph = Graph(
        hierarchy=hierarchy,
        training_level=cu.get_training_level(settings),
        forecasting_parameters=forecasting_parameters,
        label_column_name=cu.get_label_column_name(settings)
    )

    input_dataset = script_run.input_datasets[
        hru.get_input_dataset_name(arguments_dict.get(HTSConstants.INPUT_DATA_NAME))]

    if cu.is_tabular_dataset(input_dataset):
        graph = _hierarchy_builder_partitioned_tabular_dataset(input_dataset, graph, hierarchy)
    else:
        graph = _hierarchy_builder_file_dataset(
            input_dataset, graph, collected_data_path, script_run, settings, output_path, local_mode,
            event_logger, event_logger_additional_fields
        )

    # dump graph and upload to artifact
    hru.dump_object_to_json(graph.serialize(), output_path)
    event_logger.log_event(hts_events.HierarchyBuilderEnd(event_logger_additional_fields))


def _hierarchy_builder_file_dataset(
        raw_input_data_path: str,
        graph: Graph,
        collected_data_path: str,
        script_run: Run,
        settings: Dict[str, Any],
        output_path: str,
        local_mode: bool,
        event_logger: EventLogger,
        custom_dim: Dict[str, str],
) -> Graph:
    """
    The driver code for hierarchy builder step for file dataset input.

    :param raw_input_data_path: The path to the raw input to build the hierarchy for.
    :param graph: The hierarchy graph.
    :param collected_data_path: The path, which will contain csv files, corresponding to
                                each of the nodes.
    :param script_run: The run of this step.
    :param settings: The dictionary with the settings.
    :param output_path: The path to save the graph to.
    :param local_mode: If true, the script run is offline run.
    :param event_logger: The event logger used for the run.
    :param custom_dim: The dictionary with the custom dimensions used for logging.
    :return: The hierarchy graph.
    """

    os.makedirs(collected_data_path, exist_ok=True)

    console_writer.println("Data path mounted at {}".format(raw_input_data_path))
    console_writer.println("Training level collected data will be written at {}".format(collected_data_path))
    _check_mounted_file_dataset(raw_input_data_path)

    event_logger.log_event(hts_events.HierarchyBuilderValidateData(custom_dim))
    node_file_dict = get_training_level_node_file_dict(graph, raw_input_data_path, settings)
    event_logger.log_event(hts_events.HierarchyBuilderCollectData(custom_dim))
    generate_collected_files(node_file_dict, raw_input_data_path, collected_data_path)

    logger.info("There are {} nodes in the graph, {} in training level and {} leaf nodes.".format(
        len(graph.get_all_nodes()), len(node_file_dict), len(graph.get_bottom_nodes())
    ))

    hru.dump_object_to_json(graph.serialize(), output_path)

    event_logger.log_event(hts_events.HierarchyBuilderEnd(custom_dim))
    parent_run = hru.get_pipeline_run(script_run)

    collect_summary = get_data_collect_summary(node_file_dict)
    console_writer.println(str(collect_summary))
    logger.info("Uploading the data collection summary now.")
    hru.upload_object_to_artifact_json_file(
        collect_summary, HTSConstants.HTS_FILE_DATASET_COLLECT_SUMMARY, parent_run, local_mode)

    return graph


def _hierarchy_builder_partitioned_tabular_dataset(
        input_dataset: Dataset,
        graph: Graph,
        hierarchy: List[str]
) -> Graph:
    """
    The driver code for hierarchy builder step for partitioned tabular dataset input.

    :param input_dataset: The input data set.
    :param graph: The hierarchy graph.
    :param hierarchy: The hierarchy.
    :return: modified graph.
    """
    # get all partition keys
    partition_key_values = input_dataset.get_partition_key_values(hierarchy)
    console_writer.println(str(partition_key_values))
    # build graph
    graph.make_or_update_hierarchy(pd.DataFrame(partition_key_values))
    return graph
