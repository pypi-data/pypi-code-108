# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
from typing import List, Optional, Union, Tuple, Generator, cast, Dict, Any
import argparse
import hashlib
import json
import logging
import os
import pandas as pd
from random import randint
from time import sleep
from types import ModuleType
import uuid

from azureml.core import Run
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame
from azureml.train.automl.constants import HTSConstants
from azureml.automl.core.shared import log_server, logging_utilities
from azureml.automl.core.shared._diagnostics.automl_events import AutoMLBaseEvent
from azureml.telemetry import INSTRUMENTATION_KEY
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import UserException
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import HierarchyAllParallelRunsFailedByUserError
from azureml.train.automl.runtime._hts.hts_runtime_json_serializer import HTSRuntimeEncoder, HTSRuntimeDecoder
from azureml.train.automl._hts.status_record import StatusRecord
from azureml.train.automl.runtime._hts.hts_node import Node
from azureml.train.automl.runtime._hts.node_columns_info import NodeColumnsInfo


def fill_na_with_space(df: pd.Series) -> pd.Series:
    """
    Fill na with space for a pandas columns

    :param df: The input dataframe.
    :return:  pd.DataFrame
    """
    if df.isna().any():
        return df.fillna(" ")
    else:
        return df


def concat_df_with_none(df: Optional[pd.DataFrame], update_df: pd.DataFrame) -> pd.DataFrame:
    """
    Concat two dataframes. If the first one is None, then return the second one. If not, return the concat result of
    these two dataframe.

    :param df: First pd.DataFrame that can be None.
    :param update_df: Second pd.DataFrame.
    :return: The concat pd.DataFrame of these two.
    """
    if df is None:
        return update_df
    else:
        return pd.concat([df, update_df], ignore_index=True)


def abs_sum_target_by_time(
        df: pd.DataFrame,
        time_column_name: str,
        label_column_name: str,
        other_column_names: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Calculate the absolute sum value of a dataframe by the time_column_name.

    :param df: The input df.
    :param time_column_name: The time column name.
    :param label_column_name: The column name contains the values that needs to be take summation.
    :param other_column_names: Other column name that won't need group by.
    :return: pd.DataFrame
    """
    group_by_columns = [time_column_name]
    if other_column_names is not None:
        group_by_columns.extend(other_column_names)
    all_keep_columns = [col for col in group_by_columns]
    all_keep_columns.append(label_column_name)
    return df[all_keep_columns].groupby(group_by_columns).apply(lambda c: c.abs().sum()).reset_index()


def get_cross_time_df(
        df_sum: Optional[pd.DataFrame],
        df: pd.DataFrame,
        time_column_name: str,
        label_column_name: str
) -> pd.DataFrame:
    """
    Calculate the absolute summation of a pd.DataFrame with another dataframe based on time_column_name.

    :param df_sum: First pd.DataFrame which can be None.
    :param df: Second pd.DataFrame.
    :param time_column_name: The time column name.
    :param label_column_name: The column name contains the values that needs to be take summation.
    :return: pd.DataFrame
    """
    group_df_sum = abs_sum_target_by_time(df, time_column_name, label_column_name)
    if df_sum is None:
        return group_df_sum
    else:
        return abs_sum_target_by_time(
            pd.concat([df_sum, group_df_sum]), time_column_name, label_column_name)


def get_input_data_generator(local_file_path: str) -> Generator[Tuple[pd.DataFrame, str], None, None]:
    """
    Generate pd.DataFrame from an input dataset or a local file path.

    :param local_file_path: The dir contains all the local data files.
    :return: None
    """
    for file in os.listdir(local_file_path):
        print("Processing collected {}.".format(file))
        yield pd.read_csv(os.path.join(local_file_path, file)), file


def get_n_points(
        input_data: pd.DataFrame, time_column_name: str, label_column_name: str, freq: Optional[str] = None
) -> int:
    """
    Get a number of points based on a TimeSeriesDataFrame.

    :param input_data: The input data.
    :param time_column_name: The time column name.
    :param label_column_name: The label column name.
    :param freq: The user input frequency.
    :return: int
    """
    tsdf = TimeSeriesDataFrame(
        input_data, time_colname=time_column_name, ts_value_colname=label_column_name
    )
    if freq is None:
        dataset_freq = tsdf.infer_freq()
    else:
        dataset_freq = freq
    return len(pd.date_range(start=tsdf.time_index.min(), end=tsdf.time_index.max(), freq=dataset_freq))


def calculate_average_historical_proportions(
        n_points: int,
        df: pd.DataFrame,
        df_total: pd.DataFrame,
        time_column_name: str,
        label_column_name: str,
        hierarchy: List[str]
) -> pd.DataFrame:
    """
    Calculate average historical proportions based on two pd.DataFrames containing values after summation.

    :param n_points: number of total points
    :param df: The pd.DataFrame which taking summation by grouping the time column and bottom hierarchy level.
    :param df_total: The pd.DataFrame which taking summation by grouping the time column.
    :param time_column_name: The time column name.
    :param label_column_name: The column that contains the summations.
    :param hierarchy: The hierarchy column names.
    :return: pd.DataFrame
    """
    # Convert the time column to same type to avoid joining error
    df[time_column_name] = df[time_column_name].astype('object')
    df_total[time_column_name] = df_total[time_column_name].astype('object')
    df_total.rename(columns={label_column_name: HTSConstants.HTS_CROSS_TIME_SUM}, inplace=True)

    merged_df = pd.merge(df, df_total, how='left', on=[time_column_name])
    merged_df[HTSConstants.AVERAGE_HISTORICAL_PROPORTIONS] = (
        merged_df[label_column_name] / merged_df[HTSConstants.HTS_CROSS_TIME_SUM] / n_points)
    all_final_column = [col for col in hierarchy]
    all_final_column.append(HTSConstants.AVERAGE_HISTORICAL_PROPORTIONS)
    return merged_df[all_final_column].groupby(hierarchy).apply(lambda c: c.abs().sum()).reset_index()


def calculate_proportions_of_historical_average(
        df: pd.DataFrame, label_column_name: str, hierarchy: List[str], total_value: Union[float, int]
) -> pd.DataFrame:
    """
    Calculate proportions of historical average based on hierarchical timeseries allocation.

    :param df: The input pd.DataFrame.
    :param label_column_name: The column that needs to calculate the proportions of historical average.
    :param hierarchy: The hierarchy columns list.
    :param total_value: The total value which pha will be normalized by.
    :return: pd.DataFrame
    """
    all_final_column = [col for col in hierarchy]
    all_final_column.append(label_column_name)
    aggregated_df = df[all_final_column].groupby(hierarchy).apply(lambda c: c.abs().sum()).reset_index()
    aggregated_df[label_column_name] = aggregated_df[label_column_name] / total_value
    aggregated_df.rename(
        columns={label_column_name: HTSConstants.PROPORTIONS_OF_HISTORICAL_AVERAGE}, inplace=True)
    return aggregated_df


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load a csv file or a parquet file into memory as pd.DataFrame

    :param file_path: The file path.
    :return: pd.DataFrame
    """
    file_name_with_extension = os.path.basename(file_path)
    file_name, file_extension = os.path.splitext(file_name_with_extension)
    if file_extension.lower() == ".parquet":
        data = pd.read_parquet(file_path)
    else:
        data = pd.read_csv(file_path)
    return data


def is_supported_data_file(file_path: str) -> bool:
    """
    Check whether a data file is supported by hts.

    :param file_path: The file path.
    :return: bool
    """
    return file_path.endswith(".parquet") or file_path.endswith(".csv")


def get_arguments_dict(script_scenario: str, is_parallel_run_step: bool = False) -> Dict[str, str]:
    """
    Get the arguements dict for the driver script.

    :param script_scenario: The different scenarios.
    :param is_parallel_run_step: If the driver scripts is a pipeline run. Pipeline run will add some arguments other
                                 the the default ones.
    :return: Dict[str, str]
    """
    print("Loading arguments for scenario {}".format(script_scenario))
    argument_dict = {}
    parser = argparse.ArgumentParser("Parsing input arguments.")
    for arg in HTSConstants.HTS_SCRIPTS_SCENARIO_ARG_DICT[script_scenario]:
        print("adding argument {}".format(arg))
        parser.add_argument(arg, dest=HTSConstants.HTS_OUTPUT_ARGUMENTS_DICT[arg], required=False)
    parser.add_argument(
        "--process_count_per_node", default=1, type=int, help="number of processes per node", required=False)

    args, _ = parser.parse_known_args()
    if is_parallel_run_step:
        # process_count_per_node and nodes_count can be used for help with concurrency
        argument_dict["process_count_per_node"] = args.process_count_per_node

    for arg in HTSConstants.HTS_SCRIPTS_SCENARIO_ARG_DICT[script_scenario]:
        argument_dict[arg] = getattr(args, HTSConstants.HTS_OUTPUT_ARGUMENTS_DICT[arg])
    print("Input arguments dict is {}".format(argument_dict))

    return argument_dict


def get_pipeline_run(run: Optional[Run] = None) -> Run:
    """
    Get the pipeline run.

    :param run: If run is passed in then use the property of that run,
    :return: Run
    """
    if run is None:
        run = Run.get_context()
    parent_run = Run(run.experiment, run.properties.get('azureml.pipelinerunid'))
    return parent_run


def get_parsed_metadata_from_artifacts(run: Run, output_dir: str) -> Dict[str, Any]:
    """
    Get the metadata parsed as a dict from artifacts.

    :param run: The pipeline run.
    :param output_dir: The temp output dir.
    :return: Dict[str, Any]
    """
    run.download_file(HTSConstants.HTS_FILE_PROPORTIONS_METADATA_JSON, output_dir)
    raw_metadata_file = os.path.join(output_dir, HTSConstants.HTS_FILE_PROPORTIONS_METADATA_JSON)
    with open(raw_metadata_file) as f:
        raw_metadata = json.load(f)

    parsed_metadata = {}
    for metadata_node in raw_metadata[HTSConstants.METADATA_JSON_METADATA]:
        node_id = metadata_node[HTSConstants.NODE_ID]
        parsed_metadata[node_id] = {
            HTSConstants.PROPORTIONS_OF_HISTORICAL_AVERAGE:
                metadata_node[HTSConstants.PROPORTIONS_OF_HISTORICAL_AVERAGE],
            HTSConstants.AVERAGE_HISTORICAL_PROPORTIONS:
                metadata_node[HTSConstants.AVERAGE_HISTORICAL_PROPORTIONS]
        }
    os.remove(raw_metadata_file)
    return parsed_metadata


def get_node_columns_info_from_artifacts(run: Run, output_dir: str) -> Dict[str, NodeColumnsInfo]:
    """
    Get the node-columns info from artifacts.

    :param run: The pipeline run.
    :param output_dir: The temp output dir.
    """
    run.download_file(HTSConstants.HTS_FILE_NODE_COLUMNS_INFO_JSON, output_dir)
    info_file = os.path.join(output_dir, HTSConstants.HTS_FILE_NODE_COLUMNS_INFO_JSON)
    with open(info_file) as f:
        node_columns_info = json.load(f, cls=HTSRuntimeDecoder)
    os.remove(info_file)

    return _parse_columns_info(node_columns_info)


def get_intermediate_file_postfix(filename: str) -> Optional[str]:
    """
    Getting the hts related file postfix from a file name.

    :param filename: A file name.
    :return: The postfix that HTS can process.
    """
    postfix = None
    if filename.endswith(HTSConstants.HTS_FILE_POSTFIX_RUN_INFO_JSON):
        postfix = HTSConstants.HTS_FILE_POSTFIX_RUN_INFO_JSON
    elif filename.endswith(HTSConstants.HTS_FILE_POSTFIX_NODE_COLUMNS_INFO_JSON):
        postfix = HTSConstants.HTS_FILE_POSTFIX_NODE_COLUMNS_INFO_JSON
    elif filename.endswith(HTSConstants.HTS_FILE_POSTFIX_METADATA_CSV):
        postfix = HTSConstants.HTS_FILE_POSTFIX_METADATA_CSV
    elif filename.endswith(HTSConstants.HTS_FILE_POSTFIX_EXPLANATION_INFO_JSON):
        postfix = HTSConstants.HTS_FILE_POSTFIX_EXPLANATION_INFO_JSON
    else:
        print("Unknown file to proceed {}".format(filename))
    return cast(Optional[str], postfix)


def get_json_dict_from_file(file_dir: str, filename: str) -> Dict[str, Any]:
    """
    Load a json file to a dict from the file_dir and file name.

    :param file_dir: The file dir.
    :param filename: The file name.
    :return: Dict[str, Any]
    """
    with open(os.path.join(file_dir, filename)) as f:
        result = json.load(f)
    return cast(Dict[str, Any], result)


def get_proportions_csv_filename(filename: str) -> str:
    """
    Get the file name of the intermediate proportions csv file.

    :param filename: The base file name.
    :return: str
    """
    return "{}{}".format(filename, HTSConstants.HTS_FILE_POSTFIX_METADATA_CSV)


def get_node_columns_info_filename(filename: str) -> str:
    """
    Get the file name of the intermediate column vocabulary file.

    :param filename: The base file name.
    :return: str
    """
    return "{}{}".format(filename, HTSConstants.HTS_FILE_POSTFIX_NODE_COLUMNS_INFO_JSON)


def get_explanation_info_file_name(filename: str) -> str:
    """
    Get the name of an intermediate explanation result file.

    :param filename: The base file name.
    :return: The name of a file.
    """
    return "{}{}".format(filename, HTSConstants.HTS_FILE_POSTFIX_EXPLANATION_INFO_JSON)


def get_run_info_filename(filename: str) -> str:
    """
    Get the file name of the intermediate run info file.

    :param filename: The base file name.
    :return: The run_info file name.
    """
    return "{}{}".format(filename, HTSConstants.HTS_FILE_POSTFIX_RUN_INFO_JSON)


def get_engineered_column_info_name(node_id: str) -> str:
    """
    Get the file name for the featurization info.

    :param node_id: The ID of the node for which the featurization info is being generated.
    :return: The file name.
    """
    return "{}{}".format(node_id, HTSConstants.HTS_FILE_POSTFIX_ENG_COL_INFO_JSON)


def dump_object_to_json(o: Any, path: str) -> None:
    """
    Dumps object to json with a readable format.

    :param o: Any object.
    :param path: The path to save the json.
    """
    with open(path, "w") as f:
        json.dump(o, f, ensure_ascii=False, indent=4, cls=HTSRuntimeEncoder)


def upload_object_to_artifact_json_file(
        input_object: Any, artifact_file_name: str, run: Run, local_mode: bool) -> None:
    """
    Upload object to artifact as a json file.

    :param input_object: An object that can be json serialized.
    :param artifact_file_name: The artifiact file name.
    :param run: The AzureML Run.
    :param local_mode: If the local mode is enabled.
    :return:
    """
    temp_file_path = os.path.join(os.getcwd(), artifact_file_name)
    # Save and upload run info data.
    dump_object_to_json(input_object, temp_file_path)
    run.upload_file(artifact_file_name, temp_file_path)
    if not local_mode:
        # Remove the temp file. If local_mode, the file cannot be removed as the offlineRun object is tracking this.
        os.remove(temp_file_path)


def get_model_hash(str_list: List[str]) -> str:
    """
    Get the model hash from a str list.

    :param str_list: The str list using for hast.
    :return: str
    """
    model_string = '_'.join(str(v) for v in str_list).lower()
    sha = hashlib.sha256()
    sha.update(model_string.encode())
    return sha.hexdigest()


def init_logger(
        module: Optional[ModuleType] = None,
        path: Optional[str] = None,
        handler_name: Optional[str] = None,
        run: Optional[Run] = None,
        custom_dimensions: Optional[Dict[str, str]] = None,
        verbosity: int = logging.INFO
) -> None:
    """
    Init logger for the pipeline run.

    :param module: The module name.
    :param path: The file path.
    :param handler_name: The name of the handler.
    :param run: an AzureML run.
    :param custom_dimensions: additional custom dimensions for logging.
    :param verbosity: The verbosity of the logs.
    :return:
    """
    if module is not None:
        logging_utilities.mark_package_exceptions_as_loggable(module)
    if path is not None:
        logging_utilities.mark_path_as_loggable(path)
    if handler_name is not None:
        log_server.install_sockethandler(handler_name)
    log_server.enable_telemetry(INSTRUMENTATION_KEY)
    if run is None:
        run = Run.get_context()
    current_custom_dim = {
        HTSConstants.LOGGING_RUN_ID: run.id,
        HTSConstants.LOGGING_PIPELINE_ID: run.properties.get('azureml.pipelinerunid'),
        HTSConstants.LOGGING_SUBSCRIPTION_ID: run.experiment.workspace.subscription_id,
        HTSConstants.LOGGING_REGION: run.experiment.workspace.location
    }
    if custom_dimensions:
        current_custom_dim.update(custom_dimensions)
    log_server.update_custom_dimensions(current_custom_dim)

    # Explicitly set verbosity
    log_server.set_verbosity(verbosity)


def get_additional_logging_custom_dim(sub_run_type: str) -> Dict[str, str]:
    """Get the additional properties for logging."""
    return {
        HTSConstants.LOGGING_SCRIPT_SESSION_ID: str(uuid.uuid4()),
        HTSConstants.LOGGING_RUN_SUBTYPE: sub_run_type,
        HTSConstants.LOGGING_RUN_TYPE: HTSConstants.RUN_TYPE
    }


def get_event_logger_additional_fields(
        custom_dim: Dict[str, str],
        pipeline_id: str,
        script_type: str = "run",
        should_emit: str = "True"
) -> Dict[str, str]:
    """Get the additional properties for event logger."""
    additional_fields = copy.deepcopy(custom_dim)
    additional_fields["hts_pipeline_id"] = pipeline_id
    additional_fields["hts_script_type"] = script_type
    additional_fields[AutoMLBaseEvent.SHOULD_EMIT] = should_emit
    return additional_fields


def update_log_custom_dimension(custom_dimension_dict: Dict[str, str]) -> None:
    """Update the custom dimension for log server."""
    log_server.update_custom_dimensions(custom_dimension_dict)


def check_parallel_runs_status(status_records: List[StatusRecord], parallel_step: str, uploaded_file: str) -> None:
    """Check the results of all parallel runs."""
    Contract.assert_true(
        status_records is not None and len(status_records) > 0, message="Status records should not be empty.",
        reference_code=ReferenceCodes._HTS_RUNTIME_EMPTY_STATUS_RECORDS, log_safe=True)
    if all([sr.status == StatusRecord.FAILED for sr in status_records]):
        Contract.assert_true(
            all([sr.error_type == StatusRecord.USER_ERROR for sr in status_records]),
            message="Status records should not contain system errors.", log_safe=True,
            reference_code=ReferenceCodes._HTS_RUNTIME_STATUS_RECORDS_SYSTEM_ERROR
        )
        raise UserException._with_error(
            AzureMLError.create(
                HierarchyAllParallelRunsFailedByUserError,
                target="status_record", parallel_step=parallel_step, file_name=uploaded_file,
                reference_code=ReferenceCodes._HTS_RUNTIME_STATUS_RECORDS_USER_ERROR
            )
        )


def _parse_columns_info(raw_node_columns_info_data: List[NodeColumnsInfo]) -> Dict[str, NodeColumnsInfo]:
    """
    Convert the json node columns info to node_id-columns info dict.

    :param raw_node_columns_info_data: The raw node column info.
    :return: A dict mapping the columns names to the NodeColumnInfo.
    """
    parsed_vocabulary = {}
    for node_columns_info in raw_node_columns_info_data:
        parsed_vocabulary[node_columns_info.node_id] = node_columns_info
    return parsed_vocabulary


def get_explanation_artifact_name(raw: bool, node_id: str) -> str:
    """
    Get the name of a JSON serialized dictionary with raw or engineered features explanations.

    :param raw: If true the name of a raw feature artifact will be returned.
    :param node_id: The node id in the graph.
    """
    return '{}_explanation_{}.json'.format(
        HTSConstants.EXPLANATIONS_RAW_FEATURES if raw else
        HTSConstants.EXPLANATIONS_ENGINEERED_FEATURES, node_id)


def str_or_bool_to_boolean(str_or_bool: Union[str, bool]) -> bool:
    """
    Convert the value which can be string or boolean to boolean.

    :param str_or_bool: the value, which can be string or boolean.
    :return: the corresponding boolean value.
    """
    return str_or_bool == 'True' or str_or_bool is True


def stagger_randomized_secs(arguments_dict: Dict[str, Any]) -> None:
    """
    Stagger the node for the a randomized seconds based on preocess_count_per_node and nodes_count.

    :param arguments_dict: The arguements_dict contains all the running arguemnts.
    """
    max_concurrent_runs = arguments_dict.get("process_count_per_node", 10)
    node_count = int(arguments_dict.get(HTSConstants.NODES_COUNT, 1))
    traffic_ramp_up_period_in_seconds = min(max_concurrent_runs * node_count, 600)
    worker_sleep_time_in_seconds = randint(1, traffic_ramp_up_period_in_seconds)
    print("Traffic ramp up period: {} seconds".format(traffic_ramp_up_period_in_seconds))
    print(
        "Sleeping this worker for {} seconds to stagger traffic "
        "ramp-up...".format(worker_sleep_time_in_seconds))
    sleep(worker_sleep_time_in_seconds)


def get_input_dataset_name(input_dataset_name: Optional[str]) -> str:
    """
    Get the input dataset name.

    :param input_dataset_name: The input dataset name.
    :return: return HTSConstants.HTS_INPUT is input_input_dataset_name is None or '' or
        HTSConstants.DEFAULT_ARG_VALUE.
    """
    if input_dataset_name is None or input_dataset_name == '' or input_dataset_name == HTSConstants.DEFAULT_ARG_VALUE:
        return cast(str, HTSConstants.HTS_INPUT)
    return input_dataset_name
