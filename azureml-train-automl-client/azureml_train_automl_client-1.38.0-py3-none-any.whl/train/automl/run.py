# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains functionality for managing automated ML runs in Azure Machine Learning.

This module provides methods for starting and stopping runs, monitoring run status, and retrieving model output.
"""
import datetime
import json
import logging
import re
import sys
import time
from typing import cast, Dict, Optional, Any, Tuple, List

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty, BadArgument, ArgumentOutOfRange
from azureml._restclient.constants import AUTOML_RUN_USER_AGENT, RunStatus
from azureml._restclient.jasmine_client import JasmineClient
from azureml.automl.core import inference
from azureml.automl.core.console_interface import ConsoleInterface
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.automl.core.dataset_utilities import convert_inputs, convert_inputs_dataset
from azureml.automl.core.onnx_convert.onnx_convert_constants import OnnxConvertConstants, SplitOnnxModelName
from azureml.automl.core.package_utilities import (_has_version_discrepancies,
                                                   get_sdk_dependencies)
from azureml.automl.core.shared import constants as automl_shared_constants, logging_utilities, log_server
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    CancelUnsupportedForLocalRuns, ConflictingValueForArguments, ContinueRunUnsupportedForAdb,
    ContinueRunUnsupportedForUntrackedRuns, FeatureUnsupportedForIncompatibleArguments,
    InvalidArgumentType, InvalidIteration, InvalidOperationOnRunState, ModelMissing, NoMetricsData,
    OnnxNotEnabled, OnnxSplitsNotEnabled, ExecutionFailure, ContinueRunUnsupportedForImageRuns)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import AutoMLException, UserException
from azureml.automl.core.shared.utilities import minimize_or_maximize
from azureml.core import Run
from azureml.exceptions import ExperimentExecutionException, UserErrorException, \
    ServiceException as AzureMLServiceException
from azureml.train.automl._constants_azureml import Properties

from . import _constants_azureml, _logging, constants
from ._azureautomlsettings import AzureAutoMLSettings
from ._remote_console_interface import RemoteConsoleInterface
from .exceptions import (ConfigException,
                         ClientException,
                         OnnxConvertException,
                         NotFoundException)
from ._model_download_utilities import _download_automl_model, _download_automl_onnx_model

# Task: 287629 Remove when Mix-in available
STATUS = 'status'

RUNNING_STATES = RunStatus.get_running_statuses()
POST_PROCESSING_STATES = RunStatus.get_post_processing_statuses()

CONTINUE_EXPERIMENT_KEY = 'continue'
CONTINUE_EXPERIMENT_SET = 'Set'
CONTINUE_EXPERIMENT_STATUS_KEY = '_aml_system_automl_status'

ITERATIONS_STR = 'iterations'
PRIMARY_METRIC_STR = 'primary_metric'


logger = logging.getLogger(__name__)


class AutoMLRun(Run):
    """
    Represents an automated ML experiment run in Azure Machine Learning.

    The AutoMLRun class can be used to manage a run, check run status, and retrieve run
    details once an AutoML run is submitted. For more information on working with experiment runs,
    see the :class:`azureml.core.run.Run` class.

    .. remarks::

        An AutoMLRun object is returned when you use the :meth:`azureml.core.Experiment.submit` method
        of an experiment.

        To retrieve a run that has already started, use the following code:

        .. code-block:: python

            from azureml.train.automl.run import AutoMLRun
            ws = Workspace.from_config()
            experiment = ws.experiments['my-experiment-name']
            automl_run = AutoMLRun(experiment, run_id = 'AutoML_9fe201fe-89fd-41cc-905f-2f41a5a98883')

    :param experiment: The experiment associated with the run.
    :type experiment: azureml.core.Experiment
    :param run_id: The ID of the run.
    :type run_id: str
    """

    def __init__(self, experiment, run_id, **kwargs):
        """
        Initialize an AutoML run.

        :param experiment: The experiment associated with the run.
        :type experiment: azureml.core.Experiment
        :param run_id: The ID of the run.
        :type run_id: str
        """
        host = kwargs.pop('host', None)
        self._cached_best_model = None
        self._cached_best_run = None  # type: Optional[Run]
        try:
            user_agent = kwargs.pop('_user_agent', AUTOML_RUN_USER_AGENT)
            self._jasmine_client = JasmineClient(experiment.workspace.service_context,
                                                 experiment.name,
                                                 experiment.id,
                                                 host=host)
            super(AutoMLRun, self).__init__(experiment=experiment, run_id=run_id,
                                            _user_agent=user_agent,
                                            **kwargs)
        except AzureMLServiceException as e:
            logging_utilities.log_traceback(e, logger)
            raise

        self.model_id = None

        self._is_local_run = None   # type: Optional[bool]

    @property
    def _parent_run_id(self) -> str:
        """
        Get the parent run id for this execution context, or the run id if this is a parent run.

        :return: the parent run id
        """
        match = re.fullmatch(r'(.*?)_(?:setup|[0-9]+)', self.run_id)
        if match is None:
            return self.run_id
        return match.group(1)

    @property
    def run_id(self) -> str:
        """
        Return the run ID of the current run.

        :return: The run ID of the current run.
        :rtype: str
        """
        return cast(str, self._run_id)

    def _is_local(self) -> bool:
        """
        Check whether a run is local or not and return a boolean accordingly based on AutoMLSettings.

        Featurization run, Model explanation run, Child runs do not have AzureAutoMLSettings. The only side-effect of
        trying to retrieve AutoMLSettings is that in case of local child runs, this method will return False. However,
        to circumvent this, we explicitly set the value of the variable `_is_local_run` wherever possible.

        :return: Whether or not the current run is a local run. Note that this is returns `False` in case of local
        child run.
        """
        if self._is_local_run is not None:
            return self._is_local_run

        self._is_local_run = False
        try:
            settings = self._get_automl_settings()
            compute_target = settings.compute_target
            spark_service = settings.spark_service
            if spark_service != 'adb' and compute_target == constants.ComputeTargets.LOCAL:
                self._is_local_run = True
        except Exception as ex:
            logger.warning("Failed to retrieve AutoMLSettings for run: {0}".format(self.run_id))
            logging_utilities.log_traceback(ex, logger, is_critical=False)

        return self._is_local_run

    def complete(self, **kwargs):
        """
        Complete an AutoML Run.

        :return: None
        """
        if self._is_local():
            logging.warning("Manually completing the run is not supported. Run state for local runs is managed "
                            "by the back end service. If you see a run stuck in running, it will "
                            "automatically transition to terminal state once stuck condition met.")
        return super().complete(**kwargs)

    def fail(self, error_details=None, error_code=None, _set_status=True, **kwargs):
        """
        Fail an AutoML Run.

        Optionally set the Error property of the run with a message or exception passed to ``error_details``.

        :param error_details: Optional details of the error.
        :type error_details: str or BaseException
        :param error_code: Optional error code of the error for the error classification.
        :type error_code: str
        :param _set_status: Indicates whether to send the status event for tracking.
        :type _set_status: bool
        :return:
        """
        if self._is_local():
            logging.warning("Manually failing the run is not supported. Run state for local runs is managed "
                            "by the back end service. If you see a run stuck in running, it will "
                            "automatically transition to terminal state once stuck condition met.")
        return super().fail(error_details=error_details, error_code=error_code, _set_status=_set_status, **kwargs)

    def cancel(self):
        """
        Cancel an AutoML run.

        Return True if the AutoML run was canceled successfully.

        :return: None
        """
        if self._is_local():
            raise ConfigException._with_error(AzureMLError.create(CancelUnsupportedForLocalRuns, target="cancel"))

        with log_server.new_log_context():
            run_status = self._get_status()
            if run_status in RUNNING_STATES:
                try:
                    self._jasmine_client.cancel_run(self._run_id)
                except AzureMLServiceException as e:
                    logging_utilities.log_traceback(e, logger)
                    raise
                except Exception as e:
                    logging_utilities.log_traceback(e, logger)
                    raise ClientException.create_without_pii(
                        "Failed when communicating with Jasmine service to cancel parent run.") from None
            else:
                logger.warning("Run {} is already in a terminal state: {}".format(self.id, run_status))

    def cancel_iteration(self, iteration):
        """
        Cancel a particular child run.

        :param iteration: The iteration to cancel.
        :type iteration: int
        :return: None
        """
        try:
            childrun_id = self.run_id + "_" + str(iteration)
            child_run = self._client.run.get_runs_by_run_ids(run_ids=[childrun_id])
        except AzureMLServiceException as e:
            logging_utilities.log_traceback(e, logger)
            raise
        if child_run is None or len(list(child_run)) < 1:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidOperationOnRunState, target="cancel", operation_name="cancel_iteration",
                    run_id=childrun_id, run_state="NotCreated"
                )
            )
        child_run_status = child_run[0].get_status()
        if child_run_status in RUNNING_STATES:
            try:
                self._jasmine_client.cancel_run(child_run.run_id)
            except AzureMLServiceException as e:
                logging_utilities.log_traceback(e, logger)
                raise
            except Exception as e:
                logging_utilities.log_traceback(e, logger)
                raise ClientException.create_without_pii("Failed when communicating with  Jasmine service to "
                                                         "cancel iteration: {0}.".format(iteration)) from None
        else:
            logger.warning("Run {} is already in a terminal state: {}".format(child_run.run_id, child_run_status))

    def continue_experiment(
            self,
            X=None,
            y=None,
            sample_weight=None,
            X_valid=None,
            y_valid=None,
            sample_weight_valid=None,
            data=None,
            label=None,
            columns=None,
            cv_splits_indices=None,
            spark_context=None,
            experiment_timeout_hours=None,
            experiment_exit_score=None,
            iterations=None,
            show_output=False,
            training_data=None,
            validation_data=None,
            **kwargs):
        """
        Continue an existing AutoML experiment.

        :param X: Training features.
        :type X: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y: Training labels.
        :type y: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight: Sample weights for training data.
        :type sample_weight: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param X_valid: Validation features.
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param y_valid: Validation labels.
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param sample_weight_valid: validation set sample weights.
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray or azureml.dataprep.Dataflow
        :param data: Training features and label.
        :type data: pandas.DataFrame
        :param label: Label column in data.
        :type label: str
        :param columns: A list of allowed columns in the data to use as features.
        :type columns: list(str)
        :param cv_splits_indices:
            Indices where to split training data for cross validation.
            Each row is a separate cross fold and within each crossfold, provide 2 arrays,
            the first with the indices for samples to use for training data and the second
            with the indices to use for validation data. i.e [[t1, v1], [t2, v2], ...]
            where t1 is the training indices for the first cross fold and v1 is the validation
            indices for the first cross fold.
        :type cv_splits_indices: numpy.ndarray
        :param spark_context: Spark context, only applicable when used inside azure databricks/spark environment.
        :type spark_context: SparkContext
        :param experiment_timeout_hours: How many additional hours to run this experiment for.
        :type experiment_timeout_hours: float
        :param experiment_exit_score: If specified indicates that the experiment is terminated when this value is
            reached.
        :type experiment_exit_score: int
        :param iterations: How many additional iterations to run for this experiment.
        :type iterations: int
        :param show_output: Flag indicating whether to print output to console.
        :type show_output: bool
        :param training_data: Input training data.
        :type training_data: azureml.dataprep.Dataflow or pandas.DataFrame
        :param validation_data: Validation data.
        :type validation_data: azureml.dataprep.Dataflow or pandas.DataFrame
        :return: The AutoML parent run.
        :rtype: azureml.train.automl.run.AutoMLRun
        :raises: :class:`azureml.train.automl.exceptions.ConfigException`
        :raises: :class:`azureml.train.automl.exceptions.InvalidRunState`
        """
        if not isinstance(iterations, int) and iterations is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="iterations",
                    argument="iterations", actual_type=type(iterations), expected_types="int")
            )
        if not isinstance(experiment_timeout_hours, float) and experiment_timeout_hours is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="experiment_timeout_hours", argument="experiment_timeout_hours",
                    actual_type=type(experiment_timeout_hours), expected_types="float")
            )
        if not isinstance(experiment_exit_score, int) and not isinstance(experiment_exit_score, float) and \
                experiment_exit_score is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="experiment_exit_score", argument="experiment_exit_score",
                    actual_type=type(experiment_exit_score), expected_types="float, int")
            )

        tags = self.get_tags()
        properties = self.get_properties()
        if 'AMLSettingsJsonString' not in properties:
            err_msg = 'Previous run failed before starting any iterations. Please submit a new experiment.'
            raise UserException(azureml_error=AzureMLError.create(
                ExecutionFailure, operation_name="ContinueExperiment", error_details=err_msg),
                has_pii=False
            )

        # Continue is not supported for Image tasks
        if self._is_image_run():
            raise ConfigException._with_error(AzureMLError.create(
                ContinueRunUnsupportedForImageRuns, target="continue_experiment")
            )

        original_aml_settings = json.loads(properties['AMLSettingsJsonString'])

        # Do not continue experiments for which child runs are not tracked
        track_child_runs = original_aml_settings.get('track_child_runs')
        if track_child_runs is False:
            raise ConfigException._with_error(AzureMLError.create(
                ContinueRunUnsupportedForUntrackedRuns, target="continue_experiment")
            )

        # Deprecation of data_script
        try:
            data_script = kwargs.pop('data_script')
            original_aml_settings['data_script'] = data_script
            logging.warning("Get_data scripts will be deprecated. Instead of parameter 'data_script', "
                            "please pass a Dataset object into using the 'training_data' parameter.")
        except KeyError:
            pass

        updated_iterations = None
        if iterations is None:
            if ITERATIONS_STR in tags:
                iterations = int(tags[ITERATIONS_STR])
            else:
                iterations = int(original_aml_settings[ITERATIONS_STR])
            updated_iterations = iterations
        else:
            run_iters = len(list(self.get_children(_rehydrate_runs=False)))
            updated_iterations = iterations + run_iters

        experiment_timeout_minutes = int(experiment_timeout_hours * 60) \
            if experiment_timeout_hours is not None else None
        if experiment_timeout_minutes is None:
            experiment_timeout_minutes = kwargs.get('experiment_timeout_minutes')
            if experiment_timeout_minutes is not None:
                # logging.warning('Parameter `experiment_timeout_minutes` will be deprecated moving forward. ' +
                #                'Use `experiment_timeout_hours`.')
                pass

        # Let's reset some relevant properties so that they get re-initialized when the experiment continues.
        original_aml_settings['ensemble_iterations'] = None
        original_aml_settings['experiment_timeout_minutes'] = experiment_timeout_minutes
        original_aml_settings['experiment_exit_score'] = experiment_exit_score
        original_aml_settings['spark_context'] = spark_context
        original_aml_settings[ITERATIONS_STR] = updated_iterations

        automl_settings = AzureAutoMLSettings(
            experiment=self.experiment,
            **original_aml_settings)

        if automl_settings.spark_service == 'adb' and spark_context is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="spark_context", argument_name="spark_context")
            )

        if automl_settings.spark_service is None and spark_context:
            raise ConfigException._with_error(
                AzureMLError.create(
                    FeatureUnsupportedForIncompatibleArguments, target="continue_run",
                    feature_name='continue_run', arguments="spark_context"
                )
            )

        # early stopping should always be turned off for continue run
        tags = {
            ITERATIONS_STR: str(automl_settings.iterations),
            'experiment_timeout_minutes': str(automl_settings.experiment_timeout_minutes),
            'experiment_exit_score': str(automl_settings.experiment_exit_score),
            'enable_early_stopping': str(False),
            'start_time_utc': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        # update tags
        self.set_tags(tags)

        if X is not None and y is not None:
            X, y, sample_weight, X_valid, y_valid, sample_weight_valid = convert_inputs(
                X, y, sample_weight,
                X_valid, y_valid, sample_weight_valid
            )
        else:
            training_data, validation_data = convert_inputs_dataset(
                training_data,
                validation_data
            )

        if automl_settings.metric_operation is None:
            automl_settings.metric_operation = minimize_or_maximize(
                automl_settings.primary_metric)
        from ._experiment_drivers.experiment_driver import ExperimentDriver
        from ._azure_experiment_state import AzureExperimentState
        experiment_state = AzureExperimentState(self.experiment, automl_settings)
        driver = ExperimentDriver(experiment_state)
        experiment_state.parent_run_id = self._run_id
        experiment_state.current_run = self
        experiment_state.automl_settings.spark_context = spark_context
        experiment_state.console_writer.show_output = show_output

        if (automl_settings.compute_target not in (None, constants.ComputeTargets.LOCAL)) or spark_context:
            # Running under remote or ADB
            try:
                timeout_sec = None
                if experiment_timeout_minutes:
                    timeout_sec = experiment_timeout_minutes * 60
                self._jasmine_client.continue_remote_run(
                    self.id,
                    automl_settings.iterations,
                    timeout_sec,
                    automl_settings.experiment_exit_score)

                if automl_settings.spark_context is not None:
                    try:
                        from azureml.train.automl.runtime._experiment_drivers.spark_experiment_driver import \
                            SparkExperimentDriver
                    except ImportError:
                        raise ConfigException._with_error(AzureMLError.create(
                            ContinueRunUnsupportedForAdb, target="continue_experiment",
                            module_name="azureml-train-automl-runtime")
                        )
                    spark_exp_driver = SparkExperimentDriver(experiment_state)
                    spark_exp_driver.start(
                        X=X,
                        y=y,
                        sample_weight=sample_weight,
                        X_valid=X_valid,
                        y_valid=y_valid,
                        sample_weight_valid=sample_weight_valid,
                        cv_splits_indices=cv_splits_indices,
                        training_data=training_data,
                        validation_data=validation_data,
                        show_output=show_output,
                        existing_run=True)
                    # ADB handles show output so return here
                    return self

                if show_output:
                    RemoteConsoleInterface._show_output(self,
                                                        experiment_state.console_writer,
                                                        logger,
                                                        automl_settings.primary_metric)
            except Exception as e:
                logging_utilities.log_traceback(e, logger)
                raise

            return self

        if 'best_score' in tags:
            best_score = tags['best_score']
        else:
            try:
                best_run, _ = self.get_output()
                best_score = best_run.get_metrics()[automl_settings.primary_metric]
            except Exception:
                best_score = constants.Defaults.DEFAULT_PIPELINE_SCORE

        driver.experiment_state.best_score = best_score
        params = driver.create_parent_run(
            X=X,
            y=y,
            sample_weight=sample_weight,
            X_valid=X_valid,
            y_valid=y_valid,
            sample_weight_valid=sample_weight_valid,
            cv_splits_indices=cv_splits_indices,
            training_data=training_data,
            validation_data=validation_data,
            existing_run=True)
        params_to_update = {
            'X': X,
            'y': y,
            'sample_weight': sample_weight,
            'X_valid': X_valid,
            'y_valid': y_valid,
            'sample_weight_valid': sample_weight_valid,
            'cv_splits_indices': cv_splits_indices,
            'training_data': training_data,
            'validation_data': validation_data,
            'existing_run': True}
        params_to_update.update(params)
        return driver.start(**params_to_update)

    def _get_onnx_run(self,
                      children: List[Tuple[Run, float]],
                      iteration: Optional[int] = None,
                      return_split_onnx_model: Optional[SplitOnnxModelName] = None) -> Run:
        # Note: if conversion of split models fails, the entire onnx conversion of an iteration will fail.
        # This means that if the conversion of an iteration succeeds, and user set split convert config to true,
        # all the 3 models will be successfully converted.
        if return_split_onnx_model == SplitOnnxModelName.FeaturizerOnnxModel:
            model_name = OnnxConvertConstants.FeaturizerOnnxModelPath
        elif return_split_onnx_model == SplitOnnxModelName.EstimatorOnnxModel:
            model_name = OnnxConvertConstants.EstimatorOnnxModelPath
        else:
            model_name = constants.MODEL_PATH_ONNX

        curr_run = None
        if iteration is None:
            # If returning the ONNX best model,
            # we try to download the best score model, if it's not converted successfully,
            # use the 2nd best score model, and so on.
            for child_run, _ in children:
                if model_name in child_run.get_file_names():
                    curr_run = child_run
                    break
        else:
            child_run = Run(experiment=self.experiment, run_id=self.run_id + '_' + str(iteration))
            if model_name in child_run.get_file_names():
                curr_run = child_run

        Contract.assert_true(
            curr_run is not None,
            "Failed to retrieve a run with successful ONNX conversion",
            target="current_run",
            log_safe=True
        )

        return curr_run, model_name

    def _get_best_child_run(self,
                            iteration: Optional[int] = None,
                            metric: Optional[str] = None,
                            onnx_compatible: bool = False,
                            split_onnx_model_name: Optional[SplitOnnxModelName] = None,
                            activity_name: str = "_get_best_child_run") -> Tuple[Run, str]:
        """
        Get the best child run for a given metric, or get the child run for a given iteration.

        :param iteration: The iteration number of the corresponding run and fitted model to return.
        :type iteration: int
        :param metric: The metric to use to when selecting the best run and fitted model to return.
        :type metric: str
        :param onnx_compatible: This method will return the converted ONNX model if
                                  the ``enable_onnx_compatible_models`` parameter was set to True
                                  in the :class:`azureml.train.automl.automlconfig.AutoMLConfig` object.
        :type onnx_compatible: bool
        :param split_onnx_model_name: The type of the split onnx model to return
        :type split_onnx_model_name: azureml.automl.core.onnx_convert.onnx_convert_constants.SplitOnnxModelName
        :param activity_name: Which method or scenario this is being invoked from for logging purposes.
        :type activity_name: str
        :return: The run, the name of the corresponding fitted model.
        """
        # get automl settings
        model_name = constants.MODEL_PATH
        automl_settings = self._get_automl_settings()
        with log_server.new_log_context():
            self._set_custom_dimensions(automl_settings)
            with logging_utilities.log_activity(
                    logger,
                    activity_name=activity_name
            ):
                if onnx_compatible:
                    # onnx validation
                    if not automl_settings.enable_onnx_compatible_models:
                        raise OnnxConvertException._with_error(
                            AzureMLError.create(
                                OnnxNotEnabled, target="onnx_compatible")
                        )
                    if split_onnx_model_name and not automl_settings.enable_split_onnx_featurizer_estimator_models:
                        raise OnnxConvertException._with_error(
                            AzureMLError.create(
                                OnnxSplitsNotEnabled, target="split_onnx_model_name")
                        )
                    metric = metric or self._get_automl_settings().primary_metric
                    child_runs_and_scores = self._get_all_automl_child_runs(metric)
                    curr_run, model_name = self._get_onnx_run(
                        children=child_runs_and_scores,
                        iteration=iteration,
                        return_split_onnx_model=split_onnx_model_name
                    )
                else:
                    curr_run = self._get_run_internal(iteration, metric, "get_output")
                    if curr_run is None:
                        raise NotFoundException._with_error(
                            AzureMLError.create(
                                NoMetricsData, target="metric", metric=metric)
                        )
                    # Get the remote model path property.
                    props = curr_run.get_properties()
                    if constants.PROPERTY_KEY_OF_MODEL_PATH in props:
                        model_name = props[constants.PROPERTY_KEY_OF_MODEL_PATH]
        return curr_run, model_name

    def get_output(self,
                   iteration: Optional[int] = None,
                   metric: Optional[str] = None,
                   return_onnx_model: bool = False,
                   return_split_onnx_model: Optional[SplitOnnxModelName] = None,
                   **kwargs: Any
                   ) -> Tuple[Run, Any]:
        """
        Return the run with the corresponding best pipeline that has already been tested.

        If no input parameters are provided, ``get_output``
        returns the best pipeline according to the primary metric. Alternatively,
        you can use either the ``iteration`` or ``metric`` parameter to retrieve a particular
        iteration or the best run per provided metric, respectively.

        .. remarks::

            If you'd like to inspect the preprocessor(s) and algorithm (estimator) used, you can do so through
            ``Model.steps``, similar to ``sklearn.pipeline.Pipeline.steps``.
            For instance, the code below shows how to retrieve the estimator.

            .. code-block:: python

                best_run, model = parent_run.get_output()
                estimator = model.steps[-1]

        :param iteration: The iteration number of the corresponding run and fitted model to return.
        :type iteration: int
        :param metric: The metric to use to when selecting the best run and fitted model to return.
        :type metric: str
        :param return_onnx_model: This method will return the converted ONNX model if
                                  the ``enable_onnx_compatible_models`` parameter was set to True
                                  in the :class:`azureml.train.automl.automlconfig.AutoMLConfig` object.
        :type return_onnx_model: bool
        :param return_split_onnx_model: The type of the split onnx model to return
        :type return_split_onnx_model: azureml.automl.core.onnx_convert.onnx_convert_constants.SplitOnnxModelName
        :return: The run, the corresponding fitted model.
        :rtype: azureml.core.run.Run, Model
        :raises: :class:`azureml.automl.core.shared.exceptions.ConfigException`
        :raises: :class:`azureml.train.automl.exceptions.OnnxConvertException`
        :raises: :class:`azureml.train.automl.exceptions.NotFoundException`
        """
        # If cached output is present and all parameters have default values return the cached output.
        # This optimization exists to avoid calling Run History when possible.
        if iteration is None and metric is None and not return_onnx_model and return_split_onnx_model is None and \
                self._has_cached_output():
            return self._cached_best_run, self._cached_best_model

        # get automl settings
        automl_settings = self._get_automl_settings()
        with log_server.new_log_context():
            self._set_custom_dimensions(automl_settings)
            with logging_utilities.log_activity(
                logger,
                activity_name=automl_shared_constants.TelemetryConstants.GET_OUTPUT
            ):
                curr_run, model_name = self._get_best_child_run(
                    iteration=iteration,
                    metric=metric,
                    onnx_compatible=return_onnx_model,
                    split_onnx_model_name=return_split_onnx_model,
                    activity_name=automl_shared_constants.TelemetryConstants.GET_OUTPUT
                )

                if return_onnx_model:
                    fitted_model = _download_automl_onnx_model(curr_run, model_name)
                else:
                    fitted_model = _download_automl_model(curr_run, model_name)

            return curr_run, fitted_model

    def get_best_child(self,
                       metric: Optional[str] = None,
                       onnx_compatible: bool = False,
                       **kwargs: Any) -> Run:
        """
        Return the child run with the best score for this AutoML Run.

        :param metric: The metric to use to when selecting the best run to return. Defaults to the primary metric.
        :type metric: str
        :param onnx_compatible: Whether to only return runs that generated onnx models.
        :type: bool
        :param kwargs:
        :return: AutoML Child Run.
        """
        # If cached output is present and all parameters have default values return the cached output.
        # This optimization exists to avoid calling Run History when possible.
        if metric is None and not onnx_compatible and self._has_cached_output():
            return self._cached_best_run
        run, _ = self._get_best_child_run(metric=metric,
                                          onnx_compatible=onnx_compatible,
                                          activity_name=automl_shared_constants.TelemetryConstants.GET_BEST_CHILD)
        return run

    def _has_cached_output(self) -> bool:
        """Determine whether the run has valid cached output."""
        return self._cached_best_run is not None and self._cached_best_model is not None

    def _get_automl_settings(self) -> AzureAutoMLSettings:
        """Get the AutoML settings for this run."""
        return AzureAutoMLSettings(
            experiment=self.experiment,
            show_deprecate_warnings=False,
            **json.loads(self._get_property('AMLSettingsJsonString')))

    def _get_property(self, property_name):
        """Get a property of this run."""
        if property_name not in self.properties:
            self.get_properties()

        return self.properties.get(property_name)

    def _get_run_internal(
        self,
        iteration: Optional[int],
        metric: Optional[str],
        operation_name: Optional[str] = "_get_run_internal"
    ) -> Run:
        """
        Get the best run and all other runs and their scores.

        :param iteration: Which iteration to fetch.
        :param metric: Which metric to optimize for.
        :param operation_name: Which method is calling this internal function. Used for telemetry.
        :return: The AutoML Run
        """
        if iteration is not None and metric is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=operation_name, arguments=", ".join(["metric", "iteration"]))
            )

        # get automl settings
        automl_settings = self._get_automl_settings()

        with logging_utilities.log_activity(
            logger,
            activity_name=automl_shared_constants.TelemetryConstants.GET_CHILDREN
        ):
            run_tags = self.get_tags()
            child_runs_and_scores = []          # type: List[Tuple[Run, float]]
            if iteration is not None:
                curr_run = self._get_automl_child_iteration(iteration, parent_tags=run_tags)
            elif metric is not None and metric != automl_settings.primary_metric:
                child_runs_and_scores = self._get_all_automl_child_runs(metric)
                curr_run = child_runs_and_scores[0][0]
            else:
                best_run_tag = run_tags.get('automl_best_child_run_id')
                if best_run_tag is not None:
                    curr_run = self._get_automl_child_iteration(None,
                                                                child_run_id=best_run_tag)
                else:
                    child_runs_and_scores = self._get_all_automl_child_runs(automl_settings.primary_metric)
                    curr_run = child_runs_and_scores[0][0]

        return curr_run

    def _get_all_automl_child_runs(
        self,
        metric: str
    ) -> List[Tuple[Run, float]]:
        if metric in constants.Metric.CLASSIFICATION_SET:
            objective = constants.MetricObjective.Classification[metric]
        elif metric in constants.Metric.REGRESSION_SET:
            objective = constants.MetricObjective.Regression[metric]
        elif metric in constants.Metric.IMAGE_CLASSIFICATION_PRIMARY_SET:
            objective = constants.MetricObjective.ImageClassification[metric]
        elif metric in constants.Metric.IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET:
            objective = constants.MetricObjective.ImageClassificationMultiLabel[metric]
        elif metric in constants.Metric.IMAGE_OBJECT_DETECTION_PRIMARY_SET:
            objective = constants.MetricObjective.ImageObjectDetection[metric]
        else:
            raise ConfigException._with_error(
                AzureMLError.create(BadArgument, target="metric", argument_name="metric")
            )

        with logging_utilities.log_activity(
            logger,
            activity_name=automl_shared_constants.TelemetryConstants.GET_CHILDREN
        ):
            child_runs_scores = []
            # need to use recursive=True when one of the children is a HyperDrive run to get to the leaf nodes
            children = self.get_children(
                _rehydrate_runs=False,
                recursive=True,
                properties={'runTemplate': 'automl_child'})
            metrics = self.get_metrics(recursive=True)
            for child in children:
                try:
                    if child._run_dto[STATUS] == RunStatus.COMPLETED:
                        candidate_score = metrics.get(child.id, {}).get(metric, None)
                        if candidate_score not in [None, "nan", "NaN"]:
                            child_runs_scores.append((child, candidate_score))
                except Exception:
                    continue

            if objective == constants.OptimizerObjectives.MAXIMIZE:
                is_desc = True
            elif objective == constants.OptimizerObjectives.MINIMIZE:
                is_desc = False
            child_runs_scores.sort(key=lambda obj: obj[1], reverse=is_desc)

            if len(child_runs_scores) == 0:
                raise AutoMLException._with_error(AzureMLError.create(ModelMissing, target="metric", metric=metric))

        return child_runs_scores

    def _get_automl_child_iteration(self,
                                    iteration: Optional[int],
                                    child_run_id: Optional[str] = None,
                                    parent_tags: Optional[Dict[str, str]] = None) -> Run:
        if child_run_id is None:
            if parent_tags is None:
                parent_tags = self.get_tags()
            if ITERATIONS_STR in parent_tags:
                total_runs = int(parent_tags[ITERATIONS_STR])
            else:
                total_runs = int(self._get_property('num_iterations'))

            if iteration is None or (not isinstance(iteration, str) and iteration >= total_runs):
                raise NotFoundException._with_error(
                    AzureMLError.create(
                        InvalidIteration, target="iteration", run_id=self.run_id, num_iterations=total_runs)
                )
            child_run_id = self.run_id + '_' + str(iteration)

        try:
            curr_run = Run(experiment=self.experiment, run_id=child_run_id)
            run_status = curr_run.get_status()
            if run_status != RunStatus.COMPLETED:
                err_msg = "Run {0} is in {1} state.".format(iteration, run_status)
                logger.error(err_msg)
                raise UserException(azureml_error=AzureMLError.create(
                    ExecutionFailure, operation_name="InvalidRunState({})".format(str(run_status)),
                    error_details=err_msg),
                    has_pii=False
                )
        except AzureMLServiceException as e:
            if 'ResourceNotFoundException' in e.message:
                err_msg = "Run {0} has not started yet.".format(iteration)
                raise UserException(azureml_error=AzureMLError.create(
                    ExecutionFailure, operation_name="InvalidRunState", error_details=err_msg),
                    has_pii=False
                )
            else:
                raise

        return curr_run

    def summary(self):
        """
        Get a table containing a summary of algorithms attempted and their scores.

        :return: Pandas DataFrame containing AutoML model statistics.
        :rtype: pandas.DataFrame
        """
        automl_settings = json.loads(self._get_property('AMLSettingsJsonString'))
        primary_metric = self._get_property(PRIMARY_METRIC_STR)
        objective = automl_settings['metric_operation']
        children = self.get_children(
            _rehydrate_runs=False,
            recursive=True,
            properties={'runTemplate': 'automl_child'})

        algo_count = {}     # type: Dict[str, int]
        best_score = {}
        for child_run in children:
            # skip summary generation for hyperdrive parent run
            if child_run.type.lower() == "hyperdrive":
                continue

            metrics = child_run.get_metrics()
            properties = child_run.get_properties()
            score = constants.Defaults.DEFAULT_PIPELINE_SCORE
            if primary_metric in metrics:
                score = metrics[primary_metric]
            if 'run_algorithm' in properties:
                algo = properties['run_algorithm']
            else:
                algo = 'Failed'
            if algo not in algo_count:
                algo_count[algo] = 1
                best_score[algo] = score
            else:
                algo_count[algo] = algo_count[algo] + 1
                if objective == constants.OptimizerObjectives.MINIMIZE:
                    if score < best_score[algo] or best_score[algo] in [None, "nan", "NaN"]:
                        best_score[algo] = score
                else:
                    if score > best_score[algo] or best_score[algo] in [None, "nan", "NaN"]:
                        best_score[algo] = score

        algo_comp = []
        for key in algo_count:
            algo_comp.append([
                key, algo_count[key], best_score[key]])
        return algo_comp

    def _fetch_guardrails(self) -> Dict[str, Any]:
        verifier_str = self._download_artifact_contents_to_string(constants.VERIFIER_RESULTS_PATH)
        verifier_results = json.loads(verifier_str)           # type: Dict[str, Any]
        return verifier_results

    def _print_guardrails(self, ci: ConsoleInterface, verifier_results: Dict[str, Any] = {}) -> None:
        if verifier_results:
            version = verifier_results.get("schema_version")
            ci.print_guardrails(verifier_results['faults'], True, schema_version=version)
        else:
            try:
                verifier_results = self._fetch_guardrails()
                if len(verifier_results['faults']) > 0:
                    self._print_guardrails(ci, verifier_results)
            except UserErrorException:
                ci.print_line("Current Run does not have Guardrail data.")

    def get_guardrails(self, to_console: bool = True) -> Dict[str, Any]:
        """Print and return detailed results from running Guardrail verification.

        :param to_console: Indicates whether to write the verification results to the console.
        :type to_console: bool
        :returns: A dictionary of verifier results.
        :rtype: dict
        :raises: :class:`azureml.exceptions.UserErrorException`
        """
        writer = ConsoleWriter(sys.stdout if to_console else None)
        ci = ConsoleInterface('verifier_results', writer)
        verifier_results = {}           # type: Dict[str, Any]
        try:
            verifier_results = self._fetch_guardrails()
            if len(verifier_results['faults']) == 0:
                writer.println("Guardrail verification completed without any detected problems.")
            elif to_console:
                self._print_guardrails(ci, verifier_results)
        except UserErrorException:
            writer.println("Current Run does not have Guardrail data.")
        finally:
            return verifier_results

    def register_model(self, model_name=None, description=None, tags=None, iteration=None, metric=None):
        """
        Register the model with AzureML ACI service.

        :param model_name: The name of the model being deployed.
        :type model_name: str
        :param description: The description for the model being deployed.
        :type description: str
        :param tags: Tags for the model being deployed.
        :type tags: dict
        :param iteration: Override for which model to deploy. Deploys the model for a given iteration.
        :type iteration: int
        :param metric: Override for which model to deploy. Deploys the best model for a different metric.
        :type metric: str
        :return: The registered model object.
        :rtype: Model
        """
        automl_settings = self._get_automl_settings()
        with log_server.new_log_context():
            self._set_custom_dimensions(automl_settings)
            with logging_utilities.log_activity(
                logger,
                activity_name=automl_shared_constants.TelemetryConstants.REGISTER_MODEL
            ):
                best_run = self._get_run_internal(iteration, metric, "register_model")

                auto_gen_model_id = best_run.properties.get(inference.AutoMLInferenceArtifactIDs.ModelName)
                if not auto_gen_model_id:
                    auto_gen_model_id = best_run.get_properties().get(inference.AutoMLInferenceArtifactIDs.ModelName)
                if model_name is not None and len(model_name) > 0:
                    best_run.model_id = model_name
                elif auto_gen_model_id is not None:
                    best_run.model_id = auto_gen_model_id
                else:
                    best_run.model_id = self.run_id.replace('_', '').replace('-', '')[:15]
                    if iteration is not None:
                        best_run.model_id += str(iteration)
                    elif metric is not None:
                        best_run.model_id += metric
                    else:
                        best_run.model_id += 'best'
                    best_run.model_id = best_run.model_id.replace('_', '')[:29]
                self.model_id = best_run.model_id

                properties = best_run.get_properties()
                model_path = properties.get(constants.PROPERTY_KEY_OF_MODEL_PATH,
                                            constants.MODEL_PATH)

                res = best_run.register_model(
                    model_path=model_path,
                    model_name=self.model_id,
                    tags=tags,
                    description=description)
            return res

    def retry(self):
        """Return True if the AutoML run was retried successfully.

        This method is not implemented.

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def pause(self):
        """Return True if the AutoML run was paused successfully.

        This method is not implemented.

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def resume(self):
        """Return True if the AutoML run was resumed successfully.

        This method is not implemented.

        :raises: NotImplementedError:
        """
        raise NotImplementedError

    def _set_custom_dimensions(self, settings: AzureAutoMLSettings) -> None:
        """Set telemetry custom dimensions."""
        _logging.set_run_custom_dimensions(
            automl_settings=settings,
            parent_run_id=self._parent_run_id,
            child_run_id=self.run_id,
            parent_run_uuid=self._run_dto.get("parent_run_uuid", None),
            child_run_uuid=self._run_dto.get("run_uuid", None)
        )

    def get_run_sdk_dependencies(
        self,
        iteration=None,
        check_versions=True,
        **kwargs
    ):
        """
        Get the SDK run dependencies for a given run.

        :param iteration: The iteration number of the fitted run to be retrieved. If None, retrieve the
            parent environment.
        :type iteration: int
        :param check_versions: If True, check the versions with current environment. If False, pass.
        :type check_versions: bool
        :return: The dictionary of dependencies retrieved from RunHistory.
        :rtype: dict
        :raises: :class:`azureml.train.automl.exceptions.ConfigException`
        """
        if iteration is not None:
            if iteration < 0:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange, target="iteration", argument_name="iteration", min=0, max=1000
                    )
                )
        try:
            dependencies_versions_json = self._get_property('dependencies_versions')
            if iteration is not None:
                curr_run = AutoMLRun(experiment=self.experiment,
                                     run_id=self.run_id + '_' + str(iteration))
                dependencies_versions_json = curr_run._get_property('dependencies_versions')
            dependencies_versions = json.loads(dependencies_versions_json)
            logging.debug('All the dependencies and the corresponding versions in the environment are:')
            logging.debug(
                ';'.join(
                    [
                        '{}=={}'.format(d, dependencies_versions[d]) for d in sorted(dependencies_versions.keys())
                    ]
                )
            )
        except Exception:
            logging.warning(
                'No dependencies information found in the RunHistory.')
            return dict()

        sdk_dependencies = get_sdk_dependencies(
            all_dependencies_versions=dependencies_versions
        )
        if check_versions:
            _has_version_discrepancies(sdk_dependencies)

        return sdk_dependencies

    # Task: 287629 Remove when Mix-in available
    def wait_for_completion(self, show_output=False, wait_post_processing=False):
        """
        Wait for the completion of this run.

        Returns the status object after the wait.

        :param show_output: Indicates whether to show the run output on sys.stdout.
        :type show_output: bool
        :param wait_post_processing: Indicates whether to wait for the post processing to
            complete after the run completes.
        :type wait_post_processing: bool
        :return: The status object.
        :rtype: dict
        :raises: :class:`azureml.exceptions.ExperimentExecutionException`
        """
        if show_output:
            try:
                # Use cached object if available
                run_properties = self.properties
                if not run_properties:
                    run_properties = self.get_properties()

                primary_metric = run_properties[PRIMARY_METRIC_STR]
                console_writer = ConsoleWriter(sys.stdout)
                console_writer.print_run_info(run=self)
                RemoteConsoleInterface._show_output(self,
                                                    console_writer,
                                                    None,
                                                    primary_metric)
            except KeyboardInterrupt:
                error_message = "The output streaming for the run interrupted.\n" \
                                "But the run is still executing on the compute target."

                raise ExperimentExecutionException(error_message)
        else:
            running_states = RUNNING_STATES
            if wait_post_processing:
                running_states.extend(POST_PROCESSING_STATES)

            current_status = None
            while current_status is None or current_status in running_states:
                current_status = self.get_tags().get('_aml_system_automl_status', None)
                if current_status is None:
                    current_status = self.get_status()
                time.sleep(3)

        return self.get_details()

    def _get_problem_info_dict(self):
        problem_info_str = self.properties[_constants_azureml.Properties.PROBLEM_INFO]
        return json.loads(problem_info_str)

    def _is_image_run(self):
        properties = self.get_properties()
        if Properties.DISPLAY_TASK_TYPE_PROPERTY in properties:
            if properties[Properties.DISPLAY_TASK_TYPE_PROPERTY] is not None and \
                    "image" in str(properties[Properties.DISPLAY_TASK_TYPE_PROPERTY]):
                return True

        return False

    def _get_status(self):
        """Combine the continue experiment status with the status pull from RunHistory."""
        tags = self.get_tags()
        # continue run cases
        if CONTINUE_EXPERIMENT_KEY in tags and CONTINUE_EXPERIMENT_STATUS_KEY in tags:
            if tags[CONTINUE_EXPERIMENT_KEY] == CONTINUE_EXPERIMENT_SET:
                return tags[CONTINUE_EXPERIMENT_STATUS_KEY]
        else:
            return self.get_status()

    @staticmethod
    def _from_run_dto(experiment, run_dto):
        """Return AutoML run from a dto.

        :param experiment: The experiment that contains this run.
        :type experiment: azureml.core.experiment.Experiment
        :param run_dto: The AzureML run dto as received from the cloud.
        :type run_dto: RunDto
        :return: The AutoMLRun object.
        :rtype: AutoMLRun
        """
        return AutoMLRun(experiment, run_dto.run_id)
