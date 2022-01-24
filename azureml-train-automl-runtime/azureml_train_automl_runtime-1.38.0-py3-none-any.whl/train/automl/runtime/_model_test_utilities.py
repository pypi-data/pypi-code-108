# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, Tuple, Union
import json
import logging
import os
import subprocess
import tempfile

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.core import Workspace
from azureml.automl.core import dataset_utilities
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal, MalformedJsonString
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import PredictionException, ConfigException
from azureml.automl.runtime import _data_splitting_utilities, training_utilities
from azureml.automl.runtime._data_definition import MaterializedTabularData
from azureml.automl.runtime._data_preparation import data_preparation_utilities
from azureml.automl.runtime.dataprep_utilities import dataprep_error_handler, materialize_dataflow
from azureml.automl.runtime.shared import metrics
from azureml.core import Run, Dataset, Datastore
from azureml.data.abstract_dataset import AbstractDataset
from azureml.data.constants import WORKSPACE_BLOB_DATASTORE
from azureml.dataprep import DataPrepException as DprepException
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl._model_download_utilities import _download_automl_model
from azureml.train.automl.exceptions import ClientException
from azureml.train.automl.model_proxy import RESULTS_PROPERTY
import mlflow.azureml
import mlflow.pyfunc
from mlflow.store.artifact.models_artifact_repo import ModelsArtifactRepository


OUTPUT_FILE_NAME_TEMPLATE = "predictions{}.csv"
ORIGINAL_COL_SUFFIX = "_orig"
PREDICTED_COL_SUFFIX = "_predicted"
PREDICTED_PROBA_COL_SUFFIX = "_predicted_proba"
Y_CONTEXT_COL = "TSI_SYSTEM_DEFINED_Y_CONTEXT"
Y_PRED_COL = "TSI_SYSTEM_DEFINED_Y_PRED"

logger = logging.getLogger(__name__)


def get_model_from_training_run(experiment, training_run_id):
    """
    Get the fitted model from the specified training run.

    :param experiment: The experiment which contains the training run.
    :param training_run_id: The id for the AutoML child run which contains the model.
    :return: The fitted model
    """
    logger.info("Fetching model from training run.")
    training_run = Run(experiment, training_run_id)

    if training_run.parent.type.lower() == "hyperdrive":
        model_path = constants.PT_MODEL_PATH
    else:
        model_path = constants.MODEL_PATH

    fitted_model = _download_automl_model(training_run, model_name=model_path)
    return fitted_model


def get_target_metrics(task, is_timeseries):
    """
    Get the types of metrics which should
    be computed for the specified task.

    :param task: The task type (see constants.py).
    :param is_timeseries: Whether this is a timeseries run or not
    :return: A list of metric types
    """
    # TODO: the metrics methods are deprecated.
    # Used here to mimic the behavior of pipeline_run_helper.run_pipeline()
    # Note, the default target metrics used in ClientRunner
    # (scoring_utilities.get_scalar_metrics(task))
    # do not return the metrics graphs.
    # Metrics.get_default_metrics(task) does return the graphs data.
    target_metrics = metrics.get_default_metrics(task)
    if is_timeseries:
        target_metrics += metrics.get_default_metrics(constants.Subtasks.FORECASTING)
    return target_metrics


def get_test_datasets_from_dataprep_json(
        workspace: Workspace,
        dataprep_json: str,
        automl_settings: AzureAutoMLSettings) -> Tuple[Optional[pd.DataFrame],
                                                       Optional[np.ndarray]]:
    """
    Get the materialized test dataset which is specified in the given dataprepjson.
    The dataprep_json format is the same as is passed in to Jasmine when creating a
    new AutoML run. If a train/test split was performed during the main AutoML run,
    then the dataprep_json must also contain a reference to the training_data.
    The expected root level keys in dataprep_json which correspond to the datasets are:
        "test_data" and "training_data" (the latter is only required when splitting).

    :param dataprep_json: The dataprep json which contains a reference to the test dataset.
    :param automl_settings: AzureAutoMLSettings for the parent run.
    :return: A Tuple containing (X_test, y_test)
    """
    X_test, y_test = None, None

    try:
        dataprep_json_obj = json.loads(dataprep_json)

        test_data = dataprep_json_obj.get('test_data')
        if test_data:
            test_dataset_id = test_data['datasetId']
            # Use AbstractDataset._get_by_id to get the dataset instead of
            # Dataset.get_by_id since the later adds unwanted lineage tracking
            # which causes duplicate input_datasets for the run because the
            # dataset lineage is already tracked in Jasmine when the test run starts.
            test_dataset = AbstractDataset._get_by_id(workspace, id=test_dataset_id)
            X_test, y_test, _, _ = training_utilities._extract_data_from_combined_dataflow(
                test_dataset._dataflow,
                automl_settings.label_column_name,
                automl_settings.weight_column_name,
                validate_columns_exist=False)

            X_test = materialize_dataflow(X_test)
            if y_test and y_test.row_count:
                y_test = materialize_dataflow(y_test, as_numpy=True)

        elif automl_settings.test_size > 0.0:
            training_data = dataprep_json_obj.get('training_data')
            training_dataset_id = training_data['datasetId']
            training_dataset = AbstractDataset._get_by_id(workspace, id=training_dataset_id)
            raw_data = data_preparation_utilities._get_raw_experiment_data_from_training_data(
                training_dataset, automl_settings, validation_data=None)

            tabular_data = MaterializedTabularData(raw_data.X, raw_data.y, raw_data.weights)
            _, test_data = _data_splitting_utilities.split_dataset(
                tabular_data, automl_settings.task_type, automl_settings.test_size)
            X_test = test_data.X
            y_test = test_data.y

    except json.JSONDecodeError as je:
        log_utils.log_traceback(je, logger)
        raise ConfigException._with_error(
            AzureMLError.create(MalformedJsonString, target="dataprep_json", json_decode_error=str(je)),
            inner_exception=je
        )
    except DprepException as de:
        log_utils.log_traceback(de, logger)
        dataprep_error_handler(de)

    Contract.assert_value(X_test, "X_test")
    return X_test, y_test


def get_X_y_from_dataset_label(dataset: AbstractDataset, label: str)\
        -> Tuple[Optional[pd.DataFrame], Optional[np.ndarray]]:
    data_pd = dataset.to_pandas_dataframe()
    Contract.assert_value(data_pd, "dataset")
    return data_pd.drop(columns=[label]), data_pd[label]


def _get_pandas(results):
    if results is None:
        raise Exception("Inferencing returned no results.")
    elif isinstance(results, pd.DataFrame):
        logger.info("Inference output as pandas.")
        return results
    elif isinstance(results, AbstractDataset):
        logger.info("Inference output as AbstractDataset, casting to pandas.")
        return results.to_pandas_dataframe()
    else:
        # if its not any of the above types, assume its some primitive array type that pandas can accept
        logger.info("Inference output is not pandas or AbstractDataset, casting to pandas.")
        return pd.DataFrame(results)


def _save_results(results, run):
    """
    Save the prediction(s) to the default datastore.
    """
    logger.info("Saving predicted results.")

    if isinstance(results, tuple) or isinstance(results, list):
        logger.info("Multiple inference outputs, casting to pandas.")
        results_pd = [_get_pandas(result) for result in results]
    else:
        logger.info("Single inference output, casting to pandas.")
        results_pd = [_get_pandas(results)]

    local_paths = []
    remote_paths = []

    with tempfile.TemporaryDirectory() as project_folder:
        if len(results_pd) > 1:
            max_chars = len(str(len(results_pd)))

            for i, df in enumerate(results_pd, start=1):
                suffix = "_" + str(i).zfill(max_chars)
                file_name = OUTPUT_FILE_NAME_TEMPLATE.format(suffix)
                local_path = os.path.join(project_folder, file_name)
                local_paths.append((file_name, local_path))

                df.to_csv(local_path, index=False)
        else:
            file_name = OUTPUT_FILE_NAME_TEMPLATE.format("")
            local_path = os.path.join(project_folder, file_name)
            local_paths.append((file_name, local_path))

            results_pd[0].to_csv(local_path, index=False)

        # Upload the local files as run artifacts
        for path in local_paths:
            target_path = os.path.join('predictions', path[0])
            upload_result = run.upload_file(name=target_path,
                                            path_or_stream=path[1],
                                            datastore_name=WORKSPACE_BLOB_DATASTORE)
            for item in upload_result.artifacts.values():
                remote_path = item.artifact_id
                remote_paths.append(remote_path)
                logger.info("Uploaded result to {}".format(remote_path))

        datastore = Datastore.get(run.experiment.workspace, WORKSPACE_BLOB_DATASTORE)

        for remote_path in remote_paths:
            # Mark the output files as "output datasets" for the run.
            # This happens in the ensure_saved method.
            dataset = Dataset.Tabular.from_delimited_files(datastore.path(remote_path))
            dataset_utilities.ensure_saved(run.experiment.workspace, output_data=dataset)

        run.add_properties({RESULTS_PROPERTY: str(remote_paths)})


def _wrap_model(
        local_model_path: str,
        model_dest: str,
        task: str,
        is_timeseries: bool) -> str:
    class PredictProbaWrapper(mlflow.pyfunc.PythonModel):

        def __init__(self, model_uri):
            self.model_uri = f"file:{model_uri}"

        def predict(self, context, model_input):
            model = mlflow.pyfunc.load_model(self.model_uri)
            if hasattr(model._model_impl, "predict_proba"):
                proba_obj = model._model_impl
            elif hasattr(model._model_impl, "python_model") \
                    and hasattr(model._model_impl.python_model, "predict_proba"):
                proba_obj = model._model_impl.python_model
            else:
                logger.warning("The model does not contain a predict_proba method. Some classification metrics"
                               "will not be able to be calculated for this run.")
                return model.predict(model_input)
            return proba_obj.predict_proba(model_input)

    class ForecastWrapper(mlflow.pyfunc.PythonModel):

        def __init__(self, model_uri):
            self.model_uri = f"file:{model_uri}"

        def predict(self, context, model_input):
            model = mlflow.pyfunc.load_model(self.model_uri)
            if Y_CONTEXT_COL in model_input.columns:
                x_test = model_input.drop(Y_CONTEXT_COL, axis=1)
                y_actual = model_input[Y_CONTEXT_COL].values
            else:
                x_test = model_input
                y_actual = None

            if hasattr(model._model_impl, "forecast"):
                y_pred, X_forecast_transformed = model._model_impl.forecast(x_test, y_actual)
            elif hasattr(model._model_impl, "python_model") and hasattr(model._model_impl.python_model, "forecast"):
                y_pred, X_forecast_transformed = model._model_impl.python_model.forecast(x_test, y_actual)
            else:
                logger.warning("The model does not contain a forecast method. No forecasting metrics will "
                               "be calculated for this run.")
                X_forecast_transformed = None
                y_pred = model.predict(x_test)
            X_forecast_transformed[Y_PRED_COL] = y_pred
            return X_forecast_transformed

    if task == "regression":
        if is_timeseries:
            wrapped_model = ForecastWrapper(local_model_path)
        else:
            return local_model_path
    else:
        wrapped_model = PredictProbaWrapper(local_model_path)
    src_cd = os.path.join(local_model_path, "conda.yaml")
    mlflow.pyfunc.save_model(path=model_dest, python_model=wrapped_model, conda_env=src_cd)
    return model_dest


def wrap_and_save_model_data(
        model_uri: str,
        model_dest: str,
        task: str,
        X_test: pd.DataFrame,
        y_context: Optional[Union[pd.DataFrame, np.ndarray]],
        is_timeseries: bool) -> Tuple[str, str]:
    """
    Route predict_proba or forecast to predict.

    This is achieved by downloading the MLFlow model, creating a new mlflow model that references the original model
    via the local file path, and calls predict_proba or forecast on the downloaded model via it's predict method.
    With this, we can call the mlflow cli predict on the wrapped model to get predict_proba/forecast results since the
    cli does not support those APIs.

    :return: File location of the X_test data.
    """
    # trying to fetch the model from inside the wrapped model env didn't seem to work
    # so we can download the model and use its local path
    download_path = ModelsArtifactRepository(model_uri).download_artifacts(artifact_path="")
    X_test_file = "X_test.csv"
    data = X_test.copy()
    model_path = _wrap_model(download_path, model_dest, task, is_timeseries)
    if is_timeseries and y_context:
        data[Y_CONTEXT_COL] = y_context
    data.to_csv(X_test_file, index=False)
    return X_test_file, model_path


def get_forecasting_data(data: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
    return data[Y_PRED_COL], data.drop(Y_PRED_COL, axis=1)


def inference(task: str,
              model: Any,
              X_test: pd.DataFrame,
              y_context: Optional[Union[pd.DataFrame, np.ndarray]] = None,
              is_timeseries: bool = False) -> Tuple[Union[pd.DataFrame, np.ndarray],
                                                    np.ndarray,
                                                    Optional[pd.DataFrame]]:
    """
    Return predictions from the given model with a provided task type.

    :param task: The task type (see constants.py).
    :param model: The model used to make predictions.
    :param X_test: The inputs on which to predict.
    :param y_context: Used for forecasting. The target value combining definite
                      values for y_past and missing values for Y_future.
                      If None the predictions will be made for every X_pred.
    :param is_timeseries: Whether or not this is a forecasting task.
    :return: The predictions of the model on X_test
        The shape of the array returned depends on the task type
        Classification will return probabilities for each class.
        If a forecasting prediction was performed then the third value
        in the tuple will be set to the X transformed by the forecast method
        which can be used for computing the metrics. Otherwise, the third
        value will be None.
    """
    with log_utils.log_activity(logger, activity_name=constants.TelemetryConstants.PREDICT_NAME):
        X_forecast_transformed = None
        if isinstance(model, str):
            # Inference using MLFlow, used in V2
            logger.info("Running TSI V2.")
            with tempfile.TemporaryDirectory() as wrapped_model_folder:
                wrapped_model_path = os.path.join(wrapped_model_folder, "wrapped_model")
                X_test_file, model_path = \
                    wrap_and_save_model_data(model, wrapped_model_path, task, X_test, y_context, is_timeseries)
                y_pred_file = "y_pred.json"
                out = subprocess.run(
                    ['mlflow', 'models', 'predict', '--model-uri', model_path,
                     '--input-path', X_test_file, '-t', 'csv', '-o', y_pred_file], stderr=subprocess.PIPE)
                if out.returncode:
                    # TODO: We need to classify these errors. 1444746
                    exception_error_msg = \
                        "mlflow model predict failed for model {}.\n{}.".format(model, str(out.stderr))
                    raise ClientException._with_error(
                        AzureMLError.create(AutoMLInternal, error_details=exception_error_msg))
                y_pred = pd.read_json(y_pred_file)
                if is_timeseries:
                    y_pred, X_forecast_transformed = get_forecasting_data(y_pred)
        else:
            # else use the in memory model, used by V1
            logger.info("Running TSI V1.")
            if task == constants.Tasks.CLASSIFICATION:
                y_pred = model.predict_proba(X_test)

                # If the predicted result is an ndarray and thus does
                # not contain column headers then convert the ndarray
                # to a pandas DataFrame using the correct headers.
                if isinstance(y_pred, np.ndarray):
                    Contract.assert_true(
                        hasattr(model, 'classes_') and len(model.classes_) > 0,
                        message="Model {} missing required attribute classes_".format(type(model).__name__),
                        target="inference",
                        log_safe=True
                    )

                    logger.info(f"Setting y_pred columns {model.classes_}.")
                    y_pred = pd.DataFrame(y_pred, columns=model.classes_)

            elif task == constants.Tasks.REGRESSION:
                if is_timeseries and hasattr(model, 'forecast'):
                    y_pred, X_forecast_transformed = model.forecast(X_test, y_context)

                else:
                    y_pred = model.predict(X_test)

            else:
                raise NotImplementedError

        y_pred_values = y_pred.values if isinstance(y_pred, pd.DataFrame) else y_pred

        # Some pipelines will fail silently by predicting NaNs
        # E.g. a pipeline with a preprocessor that does not normalize and a linear model
        #   Pipeline[SVD, SGD] will fail if the dataset contains features on vastly different scales
        # Task to fix for ID features: 550564
        if np.issubdtype(y_pred_values.dtype, np.number):
            if np.isnan(y_pred_values).all():
                error_message = ("Silent failure occurred during prediction. "
                                 "This could be a result of unusually large values in the dataset. "
                                 "Normalizing numeric features might resolve this.")
                raise PredictionException.create_without_pii(error_message)

        # The y_pred_values (np.ndarray) is returned along with y_pred
        # to avoid potential unnecessary copies of the data from
        # calls down the line to pandas.DataFrame.values.
        return (y_pred, y_pred_values, X_forecast_transformed)


def get_output_dataframe(y_pred: Union[pd.DataFrame, np.ndarray],
                         X_test: pd.DataFrame,
                         label_column_name: str,
                         task_type: str,
                         test_include_predictions_only: bool,
                         y_test: Optional[np.ndarray] = None) -> pd.DataFrame:
    """
    Creates the predictions output dataframe for model test runs.

    If the user has requested to only include predictions then the output
    dataframe format looks like (forecasting is the same as regression):

        ``Classification => [predicted values] [probabilities]``

        ``Regression     => [predicted values]``

    else (default):

        ``Classification => [original test data labels] [predicted values] [probabilities] [features]``

        ``Regression     => [original test data labels] [predicted values] [features]``

    The ``[original test data labels]`` column name = ``[label column name] + "_orig"``.

    The ``[predicted values]`` column name = ``[label column name] + "_predicted"``.

    The ``[probabilities]`` column names = ``[class name] + "_predicted_proba"``.

    The ``[features]`` column names = ``[feature column name] + "_orig"``.

    If y_test is None then ``[original test data labels]`` will not be in the output dataframe.

    :param y_pred: The computed predictions. For classification, this should
        be a DataFrame containing the probabilites with column names corresponding
        to the classes.
    :param X_test: The input features which were used to get the predictions.
    :param automl_settings: AzureAutoMLSettings for the parent run.
    :param y_test: The original expected target column.
    :return: The predictions output dataframe.
    """
    output_df = pd.DataFrame()

    label_column_name_original = label_column_name + ORIGINAL_COL_SUFFIX
    label_column_name_predicted = label_column_name + PREDICTED_COL_SUFFIX

    if y_test is not None:
        y_test = pd.DataFrame(y_test, columns=[label_column_name_original])

    if task_type == constants.Tasks.CLASSIFICATION:
        y_pred_probs = y_pred
        y_pred = y_pred.idxmax(axis="columns")

        if y_test is not None:
            # Make sure that the type of the
            # predictions is the same as y_test
            y_pred = y_pred.values.astype(y_test.values.dtype)

        y_pred = pd.DataFrame(y_pred, columns=[label_column_name_predicted])

        y_pred_probs = y_pred_probs.add_suffix(PREDICTED_PROBA_COL_SUFFIX)

        if test_include_predictions_only:
            output_df = pd.concat([output_df, y_pred.reset_index(drop=True)], axis=1)
            output_df = pd.concat([output_df, y_pred_probs.reset_index(drop=True)], axis=1)
        else:
            if y_test is not None:
                output_df = pd.concat([output_df, y_test.reset_index(drop=True)], axis=1)
            output_df = pd.concat([output_df, y_pred.reset_index(drop=True)], axis=1)
            output_df = pd.concat([output_df, y_pred_probs.reset_index(drop=True)], axis=1)

            X_test = X_test.add_suffix(ORIGINAL_COL_SUFFIX).reset_index(drop=True)
            output_df = pd.concat([output_df, X_test], axis=1)
    else:
        if isinstance(y_pred, np.ndarray):
            y_pred = pd.DataFrame(y_pred, columns=[label_column_name_predicted])
        else:
            y_pred = pd.DataFrame(y_pred.values, columns=[label_column_name_predicted])

        if test_include_predictions_only:
            output_df = pd.concat([output_df, y_pred.reset_index(drop=True)], axis=1)
        else:
            if y_test is not None:
                output_df = pd.concat([output_df, y_test.reset_index(drop=True)], axis=1)
            output_df = pd.concat([output_df, y_pred.reset_index(drop=True)], axis=1)

            X_test = X_test.add_suffix(ORIGINAL_COL_SUFFIX).reset_index(drop=True)
            output_df = pd.concat([output_df, X_test], axis=1)

    return output_df
