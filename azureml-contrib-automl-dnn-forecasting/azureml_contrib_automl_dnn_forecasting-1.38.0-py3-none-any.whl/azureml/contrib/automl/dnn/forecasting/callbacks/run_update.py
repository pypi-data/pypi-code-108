# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Callbacks which computes and uploads metric to run."""
import json
import logging
import os
from typing import Union

import numpy as np
import pandas as pd
import pkg_resources
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.core import inference, package_utilities
from azureml.automl.core.shared import logging_utilities, constants as automl_core_constants
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.data_transformation import _get_data_snapshot
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.core.run import Run
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TCNModelNotConvergent
from forecast.callbacks import Callback


from ..constants import ForecastConstant
from ..datasets.timeseries_datasets import TimeSeriesDataset
from ..datasets.eval_timeseries_datasets import (  # noqa: F401
    AbstractValidationTimeSeriesDataset, ValidationTimeSeriesDatasetFromTrainValid
)
from ..metrics.metrics import compute_metrics_using_evalset, compute_metrics_using_pred_true,\
    get_target_values, save_metric, compute_aggregate_score
from ..wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams

logger = logging.getLogger(__name__)


class RunUpdateCallback(Callback):
    """Wraps AutoML metric computation and upload in a callback."""

    def __init__(self,
                 model_wrapper: DNNForecastWrapper,
                 run_context: Run,
                 params: DNNParams,
                 featurizer: TimeSeriesTransformer):
        """Initialize callback to compute and upload metric to the run context.

        :param model_wrapper: DNNForecastWrapper Model that is being trained
        :param run_context:AutoML run context to be used for uploading model/metrices
        :param X_valid: X validation data used for computing metrices
        :param y_valid: y validation data used for computing metrices
        :param params: DNNParams
        :param featurizer: Trained featurizer
        """
        super().__init__()
        self.model_wrapper = model_wrapper
        self.run_context = run_context
        self.ds_valid = None
        self.params = params
        self._scores = None
        self._samples = None
        self._exception_count = 0
        self.telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(interval=10)
        self.automl_run_context = AzureAutoMLRunContext(self.run_context)
        # Add properties required for automl UI.
        run_properties_for_ui = {"runTemplate": "automl_child",
                                 "run_preprocessor": "",
                                 "run_algorithm": self.model_wrapper.name,
                                 ForecastConstant.primary_metric: model_wrapper.primary_metric}
        self.run_context.add_properties(run_properties_for_ui)

        self.report_interval = params.get_value(ForecastConstant.report_interval)
        self.num_epochs = params.get_value(ForecastConstant.num_epochs)
        self.num_epochs_done = 0
        self.eval_datsets = None
        self._featurizer = featurizer
        self._last_epoch_scores = None

    def set_evaluation_dataset(self, ds_train: TimeSeriesDataset, ds_valid: TimeSeriesDataset) -> None:
        """Set the dataset to evaluate the metric.

        :param ds_train: dataset for training
        :param ds_valid: dataset for validation
        """
        self.ds_valid = ds_valid
        if isinstance(ds_valid, AbstractValidationTimeSeriesDataset):
            self.ds_valid = ds_valid
        else:
            self.ds_valid = ValidationTimeSeriesDatasetFromTrainValid(ds_train, ds_valid)

    def on_train_epoch_end(self, epoch, loss, metrics) -> None:
        """On each train epoch end set to compute metric and upload.

        :param epoch: Current epoch number
        :param loss: current loss
        :param metrics: metrics already computed
        """
        # TODO move this to different Telemetry callback
        self.telemetry_logger.send_usage_telemetry_log(
            prefix_message="[RunId:{}][After DNN Train epoch {} completed]".format(
                self.automl_run_context.run_id, epoch
            )
        )
        # set the current epoch for unit testing.
        self.params.set_parameter(ForecastConstant.CURRENT_EPOCH, epoch)
        if self._is_validation_data_available():
            scores = self._score_metrics(epoch=epoch, loss=loss)
            logger.info("Scores: '{0}'".format(scores))
            self._last_epoch_scores = scores
            if self._exception_count == 0:  # To avoid loading model with bad score for inference.
                save_metric(self.run_context, scores)
            else:
                logger.info("Skip logging score due to number of exceptions: '{0}'".format(self._exception_count))

    def _score_metrics(self, epoch: int, loss: float) -> None:
        """Compute metric using the validation set and the model in training.

        :param epoch: current epoch
        :param loss: current loss
        """
        rethrow = False
        exception_raised = False

        # Raise exception if the model training is not converging after the first epoch.
        # Metrics calculation error out due to nan or inf predictions from the model
        # due to training not converging. Giving a pass for the first epoch, to see
        # if second epoch succeeds. if second epoch or any later epoch has issue
        # model is saved after the latest epoch and that should not error out on prediction.
        if self._exception_count > 1 and epoch > 0:
            rethrow = True
        eval_list = np.arange(self.ds_valid.cross_validation) if self.ds_valid.cross_validation else [None]
        if self.ds_valid.cross_validation:
            cv_scores = []
            for i in eval_list:
                eval_set = self.ds_valid.get_eval_dataset(self._featurizer, i)
                data_loader = self.model_wrapper.create_data_loader(eval_set.val_dataset, False, num_workers=0)
                y_pred = self.model_wrapper._predict(data_loader=data_loader).reshape(-1)
                Contract.assert_true(y_pred.shape[0] == eval_set.y_valid.reshape(-1).shape[0],
                                     "invalid predict dimension, y shape {}, pred shape {}, len of reader {}".format
                                     (eval_set.y_valid.reshape(-1).shape[0], y_pred.shape[0],
                                      len(eval_set.val_dataset)),
                                     log_safe=True)

                exception_raised, slice_scores = compute_metrics_using_evalset(eval_set, y_pred, rethrow)
                cv_scores.append(slice_scores)
            exception_raised_agg, scores = compute_aggregate_score(cv_scores)
            exception_raised |= exception_raised_agg
        else:
            y_pred = self.model_wrapper._predict(self.ds_valid)
            horizon = self.model_wrapper.params.get_value(ForecastConstant.Horizon)
            assert horizon == y_pred.shape[-1], "h={0} y={1}".format(horizon, y_pred.shape)
            y_test = get_target_values(self.model_wrapper, self.ds_valid)

            exception_raised, scores = compute_metrics_using_pred_true(y_pred=y_pred, y_true_forecast=y_test,
                                                                       horizon=horizon, scalar_only=False)
        scores[ForecastConstant.Loss] = loss
        if exception_raised:
            self._exception_count += 1
        else:
            self._exception_count = 0
        return scores

    def upload_model_and_tabular_metrics(self):
        """Upload the model and compute and upload the tabular metrics."""
        if self._exception_count > 0:
            logger.error("model does not have any valid score")
            raise ClientException._with_error(AzureMLError.create(
                TCNModelNotConvergent, target="X",
                reference_code=ReferenceCodes._TCN_MODEL_NOT_CONVERGENT)
            )
        if self._is_validation_data_available():
            self.upload_properties_tabular_metrics()
        self.upload_model()

    def _is_validation_data_available(self):
        return self.ds_valid is not None or (self.X_valid is not None and self.y_valid is not None)

    def _get_primary_metric_score(self, scores) -> float:
        score = float('nan')
        primary_metric = self.model_wrapper.primary_metric
        if primary_metric in scores:
            score = scores[primary_metric]
        else:
            logger.warning("Primary metric '{0}' is missing from the scores".format(primary_metric))
        return score

    def upload_properties_tabular_metrics(self) -> None:
        """On train end set to upload tabular metrics.

        :param y_pred: predicted target values
        :param y_test: actual target values
        """
        # upload tabular metrics
        # Add the score that is mandatory for the ui to show the run in UI
        score = self._get_primary_metric_score(self._last_epoch_scores)
        self.run_context.add_properties({"score": float(score)})

    def upload_model(self) -> None:
        """Upload dnn model to run context."""
        model_id = self._get_model_id(self.run_context.id)
        self._save_model_for_automl_inference(model_id, self.model_wrapper)

    def _get_sample_data_json(self):
        # create input data json from the first row of sample data
        # this input_data is used by the swagger to infer the input data for aci inference.
        sample_str = "None"
        try:
            if self._samples is None:
                self._samples = self.model_wrapper._data_for_inference[-1:].copy()
                if ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN in self._samples:
                    self._samples.pop(ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN)

            sample_str = _get_data_snapshot(self._samples, is_forecasting=True)
        except Exception as e:
            logger.warning("Failed to create score inference file.")
            logging_utilities.log_traceback(e, logger, is_critical=False)

        return sample_str

    def _get_inference_file_content(self):
        # generate sample data for scoring file, by looking at first row fom sample data
        input_json = self._get_sample_data_json()
        return self._get_scoring_file(input_json)

    # this code has to be refactored in automl sdk where it can take the model and context and save
    # all inferencing related data
    def _save_model_for_automl_inference(self, model_id: str,
                                         model: DNNForecastWrapper):
        """Save model and runproperties needed for inference.

        :param model_id: the unique id for identifying the model with in the workspace.
        :param model: model to save in artifact.
        :return:
        """
        all_dependencies = package_utilities._all_dependencies()
        strs_to_save = {}

        # save versions to artifacts
        strs_to_save[ForecastConstant.automl_constants.DEPENDENCIES_PATH] = json.dumps(all_dependencies, indent=4)

        # save conda environment file into artifacts
        try:
            strs_to_save[ForecastConstant.automl_constants.CONDA_ENV_FILE_PATH] = self._create_conda_env_file_content()
        except Exception as e:
            logger.warning("Failed to create conda environment file.")
            logging_utilities.log_traceback(e, logger, is_critical=False)

        # save scoring file into artifacts
        try:
            scoring_file_str_v1, scoring_file_str_v2 = self._get_inference_file_content()
            strs_to_save[ForecastConstant.automl_constants.SCORING_FILE_PATH] = scoring_file_str_v1
            strs_to_save[ForecastConstant.automl_constants.SCORING_FILE_V2_PATH] = scoring_file_str_v2
        except Exception as e:
            logger.warning("Failed to create score inference file.")
            logging_utilities.log_traceback(e, logger, is_critical=False)

        # Upload files to artifact store
        models_to_upload = {automl_core_constants.PT_MODEL_PATH: model}

        try:
            # This code makes 3 network calls, we may want to optimize it away and consume save_mlflow some other way
            automl_settings = self.run_context.parent.parent.get_properties().get('AMLSettingsJsonString', "{}")
            save_as_mlflow = json.loads(automl_settings).get("save_mlflow", False)
        except Exception:
            logger.warning("Could not load AutoMLSettings from parent run.")
            save_as_mlflow = False
        self.automl_run_context.batch_save_artifacts(
            os.getcwd(),
            strs_to_save,
            models_to_upload,
            save_as_mlflow=save_as_mlflow)

        # save artifact ids as properties
        properties_to_add = {
            inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation:
                self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.CONDA_ENV_FILE_PATH),
            inference.AutoMLInferenceArtifactIDs.ModelDataLocation:
                self.automl_run_context._get_artifact_id(automl_core_constants.PT_MODEL_PATH)
        }

        properties_to_add.update({
            inference.AutoMLInferenceArtifactIDs.ScoringDataLocation:
                self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.SCORING_FILE_PATH),
            inference.AutoMLInferenceArtifactIDs.ScoringDataLocationV2:
                self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.SCORING_FILE_V2_PATH),
            inference.AutoMLInferenceArtifactIDs.ModelName: model_id
        })

        # automl code saves the graph json for the pipeline. Todo add code to save the model graph.

        self.automl_run_context._run.add_properties(properties_to_add)

    def _get_model_id(self, runid: str):
        """Generate a model name from runid.

        :param runid:  runid string of the hyperdrive child run.
        :return: the id produced by taking run number and last 12 chars from hyperdrive runid.
        """
        name = 'DNN'
        parent_num_part = ''
        child_num = ''
        if runid:
            parts = runid.split("_")
            if len(parts) > 0:
                child_num = parts[-1]
            if len(parts) > 1:
                parent_num_part = parts[-2][-12:]

        return name + parent_num_part + child_num

    def _get_scoring_file(self, input_sample_str: str = "pd.DataFrame()") -> str:
        """
        Return scoring file to be used at the inference time.

        If there are any changes to the scoring file, the version of the scoring file should
        be updated in the vendor.

        :return: Scoring python file as a string
        """
        inference_data_type = inference.inference.PandasParameterType

        content_v1 = self._format_scoring_file('score_forecasting_dnn.txt', inference_data_type, input_sample_str)
        content_v2 = self._format_scoring_file('score_forecasting_dnn_v2.txt', inference_data_type, input_sample_str)

        return content_v1, content_v2

    def _format_scoring_file(self, filename: str, inference_data_type: str, input_sample_str: str) -> str:
        scoring_file_path = pkg_resources.resource_filename(
            inference.inference.PACKAGE_NAME, os.path.join('inference', filename))
        content = None
        with open(scoring_file_path, 'r') as scoring_file_ptr:
            content = scoring_file_ptr.read()
            content = content.replace('<<ParameterType>>', inference_data_type)
            content = content.replace('<<input_sample>>', input_sample_str)
            content = content.replace('<<model_filename>>', automl_core_constants.PT_MODEL_FILENAME)

        return content

    def _create_conda_env_file_content(self):
        """
        Return conda/pip dependencies for the current AutoML run.

        If there are any changes to the conda environment file, the version of the conda environment
        file should be updated in the vendor.

        :return: Conda dependencies as string
        """
        from azureml.core.conda_dependencies import CondaDependencies
        sdk_dependencies = package_utilities._all_dependencies()
        pip_package_list_with_version = []
        automl_forecast_dnn_package = ['azureml-contrib-automl-dnn-forecasting']
        for pip_package in inference.AutoMLPipPackagesList + automl_forecast_dnn_package:
            if 'azureml' in pip_package:
                if pip_package in sdk_dependencies:
                    pip_package_list_with_version.append(pip_package + "==" + sdk_dependencies[pip_package])
            else:
                pip_package_list_with_version.append(pip_package)
        AutoMLCondaPackagesList = inference.AutoMLCondaPackagesList
        AutoMLCondaPackagesList.append("pytorch>=1.2")

        myenv = CondaDependencies.create(conda_packages=AutoMLCondaPackagesList,
                                         pip_packages=pip_package_list_with_version,
                                         python_version='3.7',
                                         pin_sdk_version=False)
        myenv.add_channel("pytorch")
        return myenv.serialize_to_string()
