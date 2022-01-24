# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import argparse
import joblib
import json
import logging
import os
import pandas as pd
import pickle as pkl
from tempfile import TemporaryDirectory
from typing import Any, Dict, Optional, Union

from azureml._common._error_definition import AzureMLError
from azureml.core import Dataset, Datastore, Run, Workspace
from azureml.core.model import Model
from azureml.exceptions import AzureMLException

from azureml.responsibleai.common._errors.error_definitions import (
    DatasetTooLargeError,
    UnexpectedObjectType
)
from azureml.responsibleai.tools._common.constants import (
    AnalysisTypes,
    ModelAnalysisFileNames,
    ModelTypes,
    PropertyKeys
)
from azureml.responsibleai.tools.model_analysis._aml_init_dto import AMLInitDTO
from azureml.responsibleai.common.model_loader import ModelLoader
from azureml.responsibleai.common._constants import LoggingConstants
from azureml.responsibleai.common._loggerfactory import _LoggerFactory, track, collect_run_info, collect_model_info

_logger = _LoggerFactory.get_logger(__name__)


def _get_logger():
    return _logger


def _parse_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('--settings_filepath', type=str, required=True,
                        help="Path to the pickled settings")

    return parser.parse_args()


def _check_dataframe_size(df: pd.DataFrame,
                          maximum_size: int,
                          dataset_name: str,
                          arg_name: str):
    if len(df.index) > maximum_size:
        raise AzureMLException._with_error(
            AzureMLError.create(
                DatasetTooLargeError,
                dataset_name=dataset_name,
                actual_count=len(df.index),
                limit_count=maximum_size,
                length_arg_name=arg_name)
        )


def load_dataset(ws: Workspace, dataset_id, snapshot_id) -> pd.DataFrame:
    """Snapshot the dataset if needed and return DataFrame."""
    _logger.info("Checking for snapshot {0} of dataset {1}".format(
        snapshot_id, dataset_id))

    ds = Dataset.get_by_id(workspace=ws, id=dataset_id)

    return ds.to_pandas_dataframe()


def _save_df(
        df: pd.DataFrame,
        dir: str,
        datastore_prefix: Optional[str],
        snapshot_id: str,
        filename: str) -> str:
    if datastore_prefix is None:
        local_path = os.path.join(dir, snapshot_id, filename)
    else:
        local_path = os.path.join(dir, datastore_prefix, snapshot_id, filename)
    common_path = os.path.dirname(local_path)
    if not os.path.exists(common_path):
        os.makedirs(common_path)
    if filename.endswith("json"):
        with open(local_path, "w+") as json_file:
            # Pandas df.to_json does not maintain more than 15 digits of precision
            json.dump(df.to_dict(orient='split'), json_file)
    else:
        df.to_parquet(local_path)
    return local_path


def upload_to_datastore(settings: AMLInitDTO,
                        workspace: Workspace,
                        train_data: pd.DataFrame,
                        test_data: pd.DataFrame,
                        y_pred_train: Any,
                        y_pred_test: Any,
                        y_proba_train: Optional[Any],
                        y_proba_test: Optional[Any]
                        ) -> None:
    datastore = Datastore.get(workspace, settings.confidential_datastore_name)
    with TemporaryDirectory() as td:
        file_names = [
            _save_df(train_data, td, settings.datastore_prefix,
                     settings.train_snapshot_id, ModelAnalysisFileNames.TRAIN_DATA),
            _save_df(test_data, td, settings.datastore_prefix,
                     settings.test_snapshot_id, ModelAnalysisFileNames.TEST_DATA),
            _save_df(y_pred_train, td, settings.datastore_prefix,
                     settings.train_snapshot_id, ModelAnalysisFileNames.TRAIN_Y_PRED),
            _save_df(y_pred_test, td, settings.datastore_prefix,
                     settings.test_snapshot_id, ModelAnalysisFileNames.TEST_Y_PRED),
        ]
        if y_proba_train is not None:
            file_names.append(_save_df(y_proba_train, td, settings.datastore_prefix,
                                       settings.train_snapshot_id, ModelAnalysisFileNames.TRAIN_Y_PROBA))
        if y_proba_test is not None:
            file_names.append(_save_df(y_proba_test, td, settings.datastore_prefix,
                                       settings.test_snapshot_id, ModelAnalysisFileNames.TEST_Y_PROBA))
        datastore.upload_files(files=file_names, relative_root=td)


def upload_to_run(
        run: Run,
        datastore_name: str,
        settings: AMLInitDTO,
        test_data: pd.DataFrame,
        y_pred_test: pd.DataFrame,
        y_proba_test: Optional[pd.DataFrame],
        data_types: Union[Dict, pd.Series]) -> None:
    with TemporaryDirectory() as td:
        settings_path = os.path.join(td, ModelAnalysisFileNames.SETTINGS)
        with open(settings_path, 'wb+') as settings_file:
            pkl.dump(settings, settings_file)

        dtypes_path = os.path.join(td, ModelAnalysisFileNames.DATA_TYPES)
        with open(dtypes_path, 'wb+') as dtypes_file:
            pkl.dump(dict(data_types), dtypes_file)

        categorical_features_path = os.path.join(
            td, ModelAnalysisFileNames.CATEGORICAL_FEATURES)
        with open(categorical_features_path, 'w+') as categorical_features_file:
            json.dump(settings.categorical_column_names,
                      categorical_features_file)

        task_type_path = os.path.join(td, ModelAnalysisFileNames.TASK_TYPE)
        with open(task_type_path, 'w+') as task_type_file:
            json.dump(settings.model_type, task_type_file)

        names = [
            ModelAnalysisFileNames.SETTINGS,
            ModelAnalysisFileNames.DATA_TYPES,
            ModelAnalysisFileNames.CATEGORICAL_FEATURES,
            ModelAnalysisFileNames.TASK_TYPE,
            ModelAnalysisFileNames.TEST_DATA_JSON,
            ModelAnalysisFileNames.TEST_Y_PRED_JSON]
        file_paths = [
            settings_path,
            dtypes_path,
            categorical_features_path,
            task_type_path,
            _save_df(test_data, td, settings.datastore_prefix, settings.test_snapshot_id,
                     ModelAnalysisFileNames.TEST_DATA_JSON),
            _save_df(y_pred_test, td, settings.datastore_prefix, settings.test_snapshot_id,
                     ModelAnalysisFileNames.TEST_Y_PRED_JSON),
        ]

        if y_proba_test is not None:
            file_paths.append(
                _save_df(y_proba_test, td, settings.datastore_prefix, settings.test_snapshot_id,
                         ModelAnalysisFileNames.TEST_Y_PROBA_JSON))
            names.append(ModelAnalysisFileNames.TEST_Y_PROBA_JSON)

        # TODO error check the response
        run.upload_files(
            names=names,
            paths=file_paths,
            return_artifacts=True,
            timeout_seconds=1200,
            datastore_name=datastore_name)


def create_analysis_asset(run: Run,
                          estimator,
                          train_data: pd.DataFrame,
                          test_data: pd.DataFrame,
                          settings: AMLInitDTO):
    _logger.info("Generating predictions")
    y_pred_train = pd.DataFrame(estimator.predict(train_data[settings.X_column_names]),
                                columns=[settings.target_column_name])
    y_pred_test = pd.DataFrame(estimator.predict(test_data[settings.X_column_names]),
                               columns=[settings.target_column_name])
    y_proba_train = None
    y_proba_test = None
    if settings.model_type == ModelTypes.BINARY_CLASSIFICATION:
        y_proba_train = pd.DataFrame(estimator.predict_proba(train_data[settings.X_column_names]),
                                     columns=[settings.target_column_name])
        y_proba_test = pd.DataFrame(estimator.predict_proba(test_data[settings.X_column_names]),
                                    columns=[settings.target_column_name])

    upload_to_datastore(
        settings,
        run.experiment.workspace,
        train_data,
        test_data,
        y_pred_train,
        y_pred_test,
        y_proba_train,
        y_proba_test)
    upload_to_run(
        run=run,
        datastore_name=settings.confidential_datastore_name,
        settings=settings,
        test_data=test_data,
        y_pred_test=y_pred_test,
        y_proba_test=y_proba_test,
        data_types=train_data.dtypes)


@track(_get_logger, custom_dimensions={'app_name': 'ModelAnalysisRun'}, activity_type=LoggingConstants.REMOTE_JOB)
def init_wrapper():
    args = _parse_command_line()

    settings: AMLInitDTO = joblib.load(args.settings_filepath)
    if not isinstance(settings, AMLInitDTO):
        raise AzureMLException._with_error(
            AzureMLError.create(
                UnexpectedObjectType,
                expected='AMLInitDTO',
                actual=str(type(settings))
            )
        )

    _logger.info("Model analysis ID: {0}".format(settings.analysis_id))

    my_run = Run.get_context()
    my_run.add_properties({PropertyKeys.ANALYSIS_ID: settings.analysis_id,
                           PropertyKeys.MODEL_ID: settings.model_id,
                           PropertyKeys.MODEL_TYPE: settings.model_type,
                           PropertyKeys.TRAIN_DATASET_ID: settings.train_dataset_id,
                           PropertyKeys.TEST_DATASET_ID: settings.test_dataset_id,
                           PropertyKeys.ANALYSIS_TYPE: AnalysisTypes.MODEL_ANALYSIS_TYPE})

    _logger.info("Dealing with initialization dataset")
    train_df = load_dataset(my_run.experiment.workspace,
                            settings.train_dataset_id,
                            settings.train_snapshot_id)

    _logger.info("Dealing with evaluation dataset")
    test_df = load_dataset(my_run.experiment.workspace,
                           settings.test_dataset_id,
                           settings.test_snapshot_id)
    _check_dataframe_size(test_df,
                          settings.maximum_rows_for_test_dataset,
                          'test',
                          'maximum_rows_for_test_dataset')

    _logger.info("Loading model")
    model_estimator = ModelLoader.load_model_from_workspace(my_run.experiment.workspace,
                                                            settings.model_loader,
                                                            settings.model_id)

    try:
        collect_run_info(_logger, "Starting model analysis remote job at {}".format(__file__), [my_run])
        collect_model_info(_logger,
                           "Starting model analysis {} model container id collection".format(__file__),
                           [Model(my_run.experiment.workspace, id=settings.model_id)])
    except Exception:
        pass

    create_analysis_asset(my_run, model_estimator, train_df, test_df, settings)
