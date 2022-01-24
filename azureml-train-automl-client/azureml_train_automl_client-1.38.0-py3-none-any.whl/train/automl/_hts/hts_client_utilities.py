# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, cast
import copy
from datetime import datetime
import json
import logging
import os

from azureml.core import Run, Experiment, Dataset
from azureml.data import TabularDataset, FileDataset
from azureml._restclient.constants import RunStatus
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import NotSupported
from azureml.train.automl.automlconfig import AutoMLConfig
from azureml.train.automl import _azureautomlsettings
from azureml.train.automl.constants import HTSConstants, HTSSupportedInputType, AutoMLPipelineScenario
from azureml.automl.core.forecasting_parameters import ForecastingParameters
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared.exceptions import ConfigException, DataException
from azureml.automl.core.shared.constants import TimeSeries
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ConflictingValueForArguments,
    HierarchyNoTrainingRun,
    MissingColumnsInData,
    TrainingDataColumnsInconsistent,
)


logger = logging.getLogger(__name__)


def is_file_dataset(dataset: Dataset) -> bool:
    """
    Check if a dataset is a file dataset.

    :param dataset: The dataset.
    :return: True if is a file dataset, False otherwise.
    """
    return isinstance(dataset, FileDataset)


def is_tabular_dataset(dataset: Dataset) -> bool:
    """
    Check if a dataset is a tabular dataset.

    :param dataset: The dataset.
    :return: True if is a tabular dataset, False otherwise.
    """
    return isinstance(dataset, TabularDataset)


def is_hts_partitioned_tabular_dataset(dataset: Dataset, hierarchy: List[str]) -> bool:
    """
    Check if a tabular dataset is partitioned using hierarchy columns.

    :param dataset: The tabular dataset.
    :param hierarchy: The hierarchy of the hts jobs.
    :return: True if the dataset is partitioned using hts columns, False otherwise.
    """
    return is_tabular_dataset(dataset) and set(hierarchy).issubset(set(dataset.partition_keys))


def load_settings_dict_file(file_path: str) -> Dict[str, Any]:
    """
    Load settings dict from a local json file.

    :param file_path: The file path.
    :return: Dict[str, Any]
    """
    with open(file_path) as json_file:
        return cast(Dict[str, Any], json.load(json_file))


def remove_hierarchy_settings_from_settings_dict(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove the hierarchy related settings from a settings dict.

    :param settings: A settings dict.
    :return: Dict[str, Any]
    """
    new_settings = copy.deepcopy(settings)
    for param in HTSConstants.HIERARCHY_PARAMETERS:
        new_settings.pop(param, None)
    return new_settings


def get_forecasting_parameters(settings: Dict[str, Any]) -> ForecastingParameters:
    """
    Get forecasting_parameters from a settings dict.

    :param settings: A settings dict.
    :return: ForecastingParameters
    """
    return ForecastingParameters.from_parameters_dict(settings, validate_params=True)


def get_label_column_name(settings: Dict[str, Any]) -> str:
    """
    Get the label column name for an AutoML run.

    :param settings: A settings dict.
    :return:
    """
    return cast(str, settings.get("label_column_name"))


def get_hierarchy(settings: Dict[str, Any]) -> List[str]:
    """
    Get hierarchy columns from a settings dict.

    :param settings: A settings dict.
    :return: A list of hierarchy columns in user input order.
    """
    return cast(List[str], settings.get(HTSConstants.HIERARCHY))


def get_training_level(settings: Dict[str, Any]) -> str:
    """
    Get hierarchy training level column from a settings dict.

    :param settings: A settings dict.
    :return: The training level column name.
    """
    return cast(str, settings.get(HTSConstants.TRAINING_LEVEL))


def get_hierarchy_to_training_level(settings: Dict[str, Any]) -> List[str]:
    """
    Get hierarchy training level column from a settings dict.

    :param settings: A settings dict.
    :return: A list of hierarchy columns to the training level column.
    """
    hierarchy = get_hierarchy(settings)
    training_level = get_training_level(settings)
    if training_level == HTSConstants.HTS_ROOT_NODE_LEVEL:
        return []
    return hierarchy[:hierarchy.index(training_level) + 1]


def get_automl_settings(settings: Dict[str, Any]) -> AutoMLBaseSettings:
    """
    Get automl settings from a settings dict.

    :param settings: A settings dict.
    :return: AutoMLBaseSettings
    """
    automl_settings_dict = copy.deepcopy(settings)
    automl_settings_dict = remove_hierarchy_settings_from_settings_dict(automl_settings_dict)
    config = AutoMLConfig(**automl_settings_dict)
    settings_dict = {k: v for (k, v) in config.user_settings.items() if k not in config._get_fit_params()}
    return _azureautomlsettings.AzureAutoMLSettings(**settings_dict)


def validate_settings(settings: Dict[str, Any], input_columns: Optional[List[str]] = None) -> None:
    """
    Validate the input settings from settings dict.

    :param settings: The settings dict.
    :param input_columns: The input columns in the dataset.
    :return:
    """
    hierarchy = get_hierarchy(settings)
    training_level = get_training_level(settings)
    forecasting_parameters = get_forecasting_parameters(settings)
    label_column_name = get_label_column_name(settings)
    get_automl_settings(settings)
    validate_hierarchy_settings(hierarchy, training_level, forecasting_parameters, label_column_name, input_columns)
    validate_forecasting_settings(forecasting_parameters, label_column_name, input_columns)
    return


def validate_hierarchy_settings(
        hierarchy: List[str],
        training_level: str,
        forecasting_parameters: ForecastingParameters,
        label_column_name: str,
        input_columns: Optional[List[str]] = None
) -> None:
    """
    Validate hierarchy column related settings.

    :param hierarchy: The hierarchy columns.
    :param training_level: The hierarchy training level.
    :param forecasting_parameters: The forecasting paramters related to the AutoML tasks.
    :param label_column_name: The label column name.
    :param input_columns: The columns in the input dataset.
    :raises: ConfigException
    """
    if not hierarchy:
        raise ConfigException._with_error(
            AzureMLError.create(
                ArgumentBlankOrEmpty, target=HTSConstants.HIERARCHY, argument_name=HTSConstants.HIERARCHY,
                reference_code=ReferenceCodes._HTS_HIERARCHY_EMPTY
            )
        )
    if len(hierarchy) != len(set(hierarchy)):
        raise ConfigException._with_error(
            AzureMLError.create(
                ConflictingValueForArguments, target=HTSConstants.HIERARCHY,
                arguments=HTSConstants.HIERARCHY,
                reference_code=ReferenceCodes._HTS_HIERARCHY_DUPLICATED
            )
        )

    if training_level is None:
        raise ConfigException._with_error(
            AzureMLError.create(
                ArgumentBlankOrEmpty, target=HTSConstants.TRAINING_LEVEL, argument_name=HTSConstants.TRAINING_LEVEL,
                reference_code=ReferenceCodes._HTS_TRAINING_LEVEL_EMPTY))
    if training_level != HTSConstants.HTS_ROOT_NODE_LEVEL and training_level not in hierarchy:
        raise ConfigException._with_error(
            AzureMLError.create(
                MissingColumnsInData, target=HTSConstants.TRAINING_LEVEL, columns="training_level",
                data_object_name="{} or {}".format(hierarchy, HTSConstants.HTS_ROOT_NODE_LEVEL),
                reference_code=ReferenceCodes._HTS_TRAINING_LEVEL_NOT_FOUND))
    for col in hierarchy:
        if col == forecasting_parameters.time_column_name:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=HTSConstants.HIERARCHY,
                    arguments="{}, {}".format(TimeSeries.TIME_COLUMN_NAME, HTSConstants.HIERARCHY),
                    reference_code=ReferenceCodes._HTS_HIERARCHY_CONTAINS_TIME_COLUMN))
        if col == label_column_name:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=HTSConstants.HIERARCHY,
                    arguments="{}, {}".format("label_column_name", HTSConstants.HIERARCHY),
                    reference_code=ReferenceCodes._HTS_HIERARCHY_CONTAINS_LABEL_COLUMN))
        if forecasting_parameters.formatted_time_series_id_column_names:
            if col in forecasting_parameters.formatted_time_series_id_column_names:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ConflictingValueForArguments, target=HTSConstants.HIERARCHY,
                        arguments="{}, {}".format(TimeSeries.TIME_SERIES_ID_COLUMN_NAMES, HTSConstants.HIERARCHY),
                        reference_code=ReferenceCodes._HTS_HIERARCHY_CONTAINS_TIMESERIES_ID_COLUMN))
        if forecasting_parameters.formatted_drop_column_names:
            if col in forecasting_parameters.formatted_drop_column_names:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ConflictingValueForArguments, target=HTSConstants.HIERARCHY,
                        arguments="{}, {}".format(TimeSeries.DROP_COLUMN_NAMES, HTSConstants.HIERARCHY),
                        reference_code=ReferenceCodes._HTS_HIERARCHY_CONTAINS_DROP_COLUMN))
        if input_columns is not None:
            if col not in input_columns:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        MissingColumnsInData, target=HTSConstants.HIERARCHY, columns="hierarchy column {}".format(col),
                        data_object_name="input data",
                        reference_code=ReferenceCodes._HTS_HIERARCHY_NOT_FOUND))


def validate_forecasting_settings(
        forecasting_parameters: ForecastingParameters,
        label_column_name: str,
        input_columns: Optional[List[str]] = None
) -> None:
    """
    Validate forecasting related settings.

    :param forecasting_parameters: The forecasting parameters.
    :param label_column_name: The label column name.
    :param input_columns: The input column from input data.
    :raises: ConfigException
    """
    # This tests should be in automl but live here can fail the run earlier.
    if label_column_name == forecasting_parameters.time_column_name:
        raise ConfigException._with_error(
            AzureMLError.create(
                ConflictingValueForArguments, target=TimeSeries.TIME_COLUMN_NAME,
                arguments="{}, label_column_name".format(TimeSeries.TIME_COLUMN_NAME),
                reference_code=ReferenceCodes._HTS_TIME_COLUMN_IS_LABEL))
    if forecasting_parameters.formatted_time_series_id_column_names:
        if label_column_name in forecasting_parameters.formatted_time_series_id_column_names:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=TimeSeries.DROP_COLUMN_NAMES,
                    arguments="{}, label_column_name".format(TimeSeries.TIME_SERIES_ID_COLUMN_NAMES),
                    reference_code=ReferenceCodes._HTS_ID_COLUMNS_CONTAINS_LABEL))
    if forecasting_parameters.formatted_drop_column_names:
        if label_column_name in forecasting_parameters.formatted_drop_column_names:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=TimeSeries.DROP_COLUMN_NAMES,
                    arguments="{}, label_column_name".format(TimeSeries.DROP_COLUMN_NAMES),
                    reference_code=ReferenceCodes._HTS_DROP_COLUMNS_CONTAINS_LABEL))
    if input_columns is not None:
        if label_column_name not in input_columns:
            raise ConfigException._with_error(
                AzureMLError.create(
                    MissingColumnsInData, target="label_column_name", columns="label_column_name",
                    data_object_name="input_data", reference_code=ReferenceCodes._HTS_LABEL_NOT_FOUND))
        if forecasting_parameters.time_column_name not in input_columns:
            raise ConfigException._with_error(
                AzureMLError.create(
                    MissingColumnsInData, target=TimeSeries.TIME_COLUMN_NAME, columns=TimeSeries.TIME_COLUMN_NAME,
                    data_object_name="input data", reference_code=ReferenceCodes._HTS_TIME_COLUMN_NOT_FOUND))
        if forecasting_parameters.formatted_time_series_id_column_names is not None:
            if any([col not in input_columns for col in forecasting_parameters.formatted_time_series_id_column_names]):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        MissingColumnsInData, target=TimeSeries.TIME_SERIES_ID_COLUMN_NAMES,
                        columns=TimeSeries.TIME_SERIES_ID_COLUMN_NAMES, data_object_name="input data",
                        reference_code=ReferenceCodes._HTS_ID_COLUMNS_NOT_FOUND))


def validate_column_consistent(expect_cols: List[str], input_cols: List[str], prefix: str) -> None:
    """
    Validate the input column consistent among the partitions.

    :param expect_cols: The expected columns from earlier partition.
    :param input_cols: The columns in the current partition.
    :param prefix: The partition name or the file name.
    :raises: ConfigException
    """
    not_found_cols_str = "Col {} found in expected columns but not in input columns."
    not_expected_cols_str = "Col {} found in input columns but not in expected columns."
    not_found_cols = [col for col in expect_cols if col not in input_cols]
    not_expected_cols = [col for col in input_cols if col not in expect_cols]
    if not_found_cols or not_expected_cols:
        raise DataException._with_error(
            AzureMLError.create(
                TrainingDataColumnsInconsistent, target=HTSConstants.HIERARCHY,
                partition_name=prefix,
                col_in_expected_msg="\n".join([not_found_cols_str.format(col) for col in not_found_cols]),
                col_in_input_msg="\n".join([not_expected_cols_str.format(col) for col in not_expected_cols]),
                reference_code="ReferenceCodes._HTS_COLUMN_INCONSISTENT"
            )
        )


def get_latest_successful_training_run(experiment: Experiment) -> Run:
    """
    Get the latest successful HTS training run for the experiment.

    :param experiment: An AzureML experiment.
    :raises: ConfigException
    :return: The latest successful HTS training run.
    """
    training_runs = [
        r for r in Run.list(
            experiment, status=RunStatus.COMPLETED,
            properties={HTSConstants.HTS_PROPERTIES_RUN_TYPE: HTSConstants.HTS_PROPERTIES_TRAINING})]
    if not training_runs:
        raise ConfigException._with_error(
            AzureMLError.create(
                HierarchyNoTrainingRun, target="training_run_id",
                reference_code=ReferenceCodes._HTS_NO_TRAINING_RUN
            )
        )

    return sorted(
        training_runs, key=lambda r: _convert_iso_datetime_str(r.get_details().get('endTimeUtc')), reverse=True)[0]


def get_training_run(training_run_id: str, experiment: Experiment, parent_run: Optional[Run] = None) -> Run:
    """
    Get the run object based on run id.

    :param training_run_id: The training run id.
    :param experiment: The experiment that the method will look into.
    :param parent_run: The parent run id of the script run. If is provided, the property will be first looked into.
    :return: A run object associated with the training_run_id. If training_run_id is
        HTSConstants.DEFAULT_ARG_VALUE, then return latest successful HTS training run in the same experiment.
    """
    training_run = None
    if training_run_id != HTSConstants.DEFAULT_ARG_VALUE:
        training_run = Run(experiment, training_run_id)
        logger.info("Running on user input run id: {}".format(training_run.id))
        print("Running on user input run id: {}".format(training_run.id))
    elif parent_run is not None:
        training_run_id = parent_run.properties.get(HTSConstants.HTS_PROPERTIES_TRAINING_RUN_ID)
        if training_run_id is not None:
            training_run = Run(experiment, training_run_id)

    if training_run is None:
        training_run = get_latest_successful_training_run(experiment)
        print("Running on latest successful run id: {}".format(training_run.id))
        logger.info("Running on latest successful run id: {}".format(training_run.id))
    return training_run


def _convert_iso_datetime_str(iso_datetime_str: str) -> datetime:
    """
    Safely convert the ISO date time string to python date time.

    :param iso_datetime_str: The date time string.
    :return: The python date time.
    """
    try:
        return datetime.strptime(iso_datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        print(e)
        logger.warning("Met exception in converting datetime.")
        return datetime.fromtimestamp(0)


def get_settings_dict(
        working_dir: str,
        settings_file_path: Optional[str] = None,
        dataset_columns: Optional[List[str]] = None,
        pipeline_scenario: str = AutoMLPipelineScenario.HTS
) -> Dict[str, Any]:
    """
    Get the AutoML settings dict and validate it.

    :param working_dir: The working dir.
    :param settings_file_path: The path contains settings file.
    :param dataset_columns: The columns in the input dataset which will be used in the settings validation.
    :param pipeline_scenario: The scenario of the pipeline run. If it is HTS, then we will validate the settings.
    :return: A dict of the settings for HTS run.
    """
    if settings_file_path is None:
        settings_file_path = HTSConstants.SETTINGS_FILE
        local_settings_file = os.path.join(working_dir, settings_file_path)
        if not os.path.exists(local_settings_file):
            settings_file_path = "settings.json"  # fall back to use old settings file.
    local_settings_file = os.path.join(working_dir, settings_file_path)
    settings = load_settings_dict_file(local_settings_file)
    logger.info("Validate all the settings now.")
    if pipeline_scenario == AutoMLPipelineScenario.HTS:
        validate_settings(settings, dataset_columns)

    return settings


def get_input_dataset_type(dataset: Dataset, hierarchy: List[str]) -> HTSSupportedInputType:
    """
    Get the input dataset type. If not found, then raise NotSupported exception.

    :param dataset: The input dataset.
    :param hierarchy: The hierarchy columns.
    :raises: DataException
    :return: The supported dataset type.
    """
    if is_file_dataset(dataset):
        return HTSSupportedInputType.FILE_DATASET
    if is_hts_partitioned_tabular_dataset(dataset, hierarchy):
        return HTSSupportedInputType.PARTITIONED_TABULAR_INPUT
    if is_tabular_dataset(dataset):
        return HTSSupportedInputType.TABULAR_DATASET
    raise DataException._with_error(
        AzureMLError.create(
            NotSupported, target="input_dataset", scenario_name=type(dataset),
            reference_code=ReferenceCodes._HTS_DATASET_NOT_SUPPORTED
        )
    )
