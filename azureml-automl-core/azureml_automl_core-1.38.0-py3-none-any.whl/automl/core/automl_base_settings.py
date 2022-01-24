# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages settings for AutoML experiments."""
import logging
import math
import os
import sys
from typing import Any, Dict, List, Optional, Union, cast

import pkg_resources

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty, ArgumentOutOfRange

from azureml.automl.core._logging import log_server
from azureml.automl.core.constants import (
    FeatureType,
    FeaturizationConfigMode,
    SupportedTransformers,
    TransformerParams,
)
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.forecasting_parameters import ForecastingParameters
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AllAlgorithmsAreBlocked,
    AllowedModelsSubsetOfBlockedModels,
    ConflictingFeaturizationConfigDroppedColumns,
    ConflictingFeaturizationConfigReservedColumns,
    ConflictingValueForArguments,
    FeatureUnsupportedForIncompatibleArguments,
    FeaturizationConfigForecastingStrategy,
    FeaturizationConfigMultipleImputers,
    InvalidArgumentForTask,
    InvalidArgumentType,
    InvalidArgumentWithSupportedValues,
    InvalidInputDatatype,
    NonDnnTextFeaturizationUnsupported,
    NotSupported,
)
from azureml.automl.core.shared.constants import SupportedModelNames, TimeSeries, _PrivateModelNames
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import ColumnTransformerParamType
from azureml.automl.core.shared.utilities import get_primary_metrics, minimize_or_maximize

from .onnx_convert import OnnxConvertConstants

logger = logging.getLogger(__name__)


class AutoMLBaseSettings:
    """Persist and validate settings for an AutoML experiment."""

    MAXIMUM_DEFAULT_ENSEMBLE_SELECTION_ITERATIONS = 15
    MINIMUM_REQUIRED_ITERATIONS_ENSEMBLE = 2

    # 525600 minutes = 1 year
    MAXIMUM_EXPERIMENT_TIMEOUT_MINUTES = 525600

    # 43200 minutes = 1 month
    MAXIMUM_ITERATION_TIMEOUT_MINUTES = 43200

    # 1073741824 MB = 1 PB
    MAXIMUM_MEM_IN_MB = 1073741824

    MAX_LAG_LENGTH = 2000
    MAX_N_CROSS_VALIDATIONS = 1000
    MAX_CORES_PER_ITERATION = 16384

    MIN_EXPTIMEOUT_MINUTES = 15

    # TODO: Add the following bits back to AzureML SDK:
    # - experiment
    # - compute target
    # - spark context

    def __init__(
        self,
        path: Optional[str] = None,
        iterations: int = 1000,
        data_script: Optional[str] = None,
        primary_metric: Optional[str] = None,
        task_type: Optional[str] = None,
        positive_label: Optional[Any] = None,
        test_size: Optional[float] = None,
        validation_size: Optional[float] = None,
        n_cross_validations: Optional[int] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        num_classes: Optional[int] = None,
        featurization: Union[str, FeaturizationConfig] = FeaturizationConfigMode.Auto,
        max_cores_per_iteration: int = 1,
        max_concurrent_iterations: int = 1,
        iteration_timeout_minutes: Optional[int] = None,
        mem_in_mb: Optional[int] = None,
        enforce_time_on_windows: bool = os.name == "nt",
        experiment_timeout_minutes: Optional[int] = None,
        experiment_exit_score: Optional[float] = None,
        blocked_models: Optional[List[str]] = None,
        blacklist_models: Optional[List[str]] = None,
        allowed_models: Optional[List[str]] = None,
        whitelist_models: Optional[List[str]] = None,
        exclude_nan_labels: bool = True,
        verbosity: int = log_server.DEFAULT_VERBOSITY,
        debug_log: Optional[str] = "automl.log",
        debug_flag: Optional[Dict[str, Any]] = None,
        enable_voting_ensemble: bool = True,
        enable_stack_ensemble: Optional[bool] = None,
        ensemble_iterations: Optional[int] = None,
        model_explainability: bool = True,
        enable_tf: bool = True,
        enable_subsampling: Optional[bool] = None,
        subsample_seed: Optional[int] = None,
        cost_mode: int = constants.PipelineCost.COST_NONE,
        is_timeseries: bool = False,
        enable_early_stopping: bool = True,
        early_stopping_n_iters: int = 10,
        enable_onnx_compatible_models: bool = False,
        enable_feature_sweeping: bool = False,
        enable_nimbusml: Optional[bool] = None,
        enable_streaming: Optional[bool] = None,
        force_streaming: Optional[bool] = None,
        label_column_name: Optional[str] = None,
        weight_column_name: Optional[str] = None,
        cv_split_column_names: Optional[List[str]] = None,
        enable_local_managed: bool = False,
        vm_type: Optional[str] = None,
        track_child_runs: bool = True,
        show_deprecate_warnings: Optional[bool] = True,
        forecasting_parameters: Optional[ForecastingParameters] = None,
        allowed_private_models: Optional[List[str]] = None,
        scenario: Optional[str] = None,
        environment_label: Optional[str] = None,
        save_mlflow: bool = False,
        test_include_predictions_only: bool = False,
        run_source: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Manage settings used by AutoML components.

        :param path: Full path to the project folder
        :param iterations: Number of different pipelines to test
        :param data_script: File path to the script containing get_data()
        :param primary_metric: The metric that you want to optimize.
        :param task_type: Field describing whether this will be a classification or regression experiment
        :param positive_label: The positive class label to calculate binary metrics with.
        :param test_size: What percent of the data to hold out for test
        :param validation_size: What percent of the data to hold out for validation
        :param n_cross_validations: How many cross validations to perform
        :param y_min: Minimum value of y for a regression experiment
        :param y_max: Maximum value of y for a regression experiment
        :param num_classes: Number of classes in the label data
        :param featurization: Indicator for whether featurization step should be done automatically or not,
            or whether customized featurization should be used.
        :param max_cores_per_iteration: Maximum number of threads to use for a given iteration
        :param max_concurrent_iterations:
            Maximum number of iterations that would be executed in parallel.
            This should be less than the number of cores on the AzureML compute. Formerly concurrent_iterations.
        :param iteration_timeout_minutes: Maximum time in seconds that each iteration before it terminates
        :param mem_in_mb: Maximum memory usage of each iteration before it terminates
        :param enforce_time_on_windows: flag to enforce time limit on model training at each iteration under windows.
        :param experiment_timeout_minutes: Maximum amount of time that all iterations combined can take
        :param experiment_exit_score:
            Target score for experiment. Experiment will terminate after this score is reached.
        :param blocked_models: List of algorithms to ignore for AutoML experiment
        :param blacklist_models: Deprecated, please use blocked_models.
        :param allowed_models: List of model names to search for AutoML experiment.
        :param whitelist_models: Deprecated, please use allowed_models.
        :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label
        :param verbosity: Verbosity level for AutoML log file
        :param debug_log: File path to AutoML logs
        :param enable_voting_ensemble: Flag to enable/disable an extra iteration for Voting ensemble.
        :param enable_stack_ensemble: Flag to enable/disable an extra iteration for Stack ensemble.
        :param ensemble_iterations: Number of models to consider for the ensemble generation
        :param model_explainability: Flag whether to explain best AutoML model at the end of training iterations.
        :param enable_tf: Flag to enable/disable Tensorflow algorithms
        :param enable_subsampling: Flag to enable/disable subsampling.
        :param subsample_seed: random_state used to sample the data.
        :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
            COST_FILTER stands for cost prediction per iteration.
        :type cost_mode: int or azureml.automl.core.shared.constants.PipelineCost
        :param is_timeseries: Flag whether AutoML should process your data as time series data.
        :type is_timeseries: bool
        :param enable_early_stopping: Flag whether the experiment should stop early if the score is not improving.
        :type enable_early_stopping: bool
        :param early_stopping_n_iters: The number of iterations to run in addition to landmark pipelines before
            early stopping kicks in.
        :type early_stopping_n_iters: int
        :param enable_onnx_compatible_models: Flag to enable/disable enforcing the onnx compatible models.
        :param enable_feature_sweeping: Flag to enable/disable feature sweeping.
        :param enable_nimbusml: Flag to enable/disable NimbusML transformers / learners.
        :param enable_streaming: Flag to enable/disable streaming.
        :param force_streaming: Flag to force streaming to kick in.
        :param label_column_name: The name of the label column.
        :param weight_column_name: Name of the column corresponding to the sample weights.
        :param cv_split_column_names: List of names for columns that contain custom cross validation split.
        :param enable_local_managed: flag whether to allow local managed runs
        :type enable_local_managed: bool
        :param track_child_runs: Flag whether to upload all child run details to Run History. If false, only the
            best child run and other summary details will be uploaded.
        :param target_lags: The number of past periods to lag from the target column.
            This setting is being deprecated. Please use forecasting_parameters instead.

            When forecasting, this parameter represents the number of rows to lag the target values based
            on the frequency of the data. This is represented as a list or single integer. Lag should be used
            when the relationship between the independent variables and dependant variable do not match up or
            correlate by default. For example, when trying to forecast demand for a product, the demand in any
            month may depend on the price of specific commodities 3 months prior. In this example, you may want
            to lag the target (demand) negatively by 3 months so that the model is training on the correct
            relationship.
        :type target_lags: List(int)
        :param feature_lags: Flag for generating lags for the numeric features
            This setting is being deprecated. Please use forecasting_parameters instead.
        :type feature_lags: str
        :param freq: The time series data set frequency.
            This setting is being deprecated. Please use forecasting_parameters instead.

            When forecasting this parameter represents the period with which the events are supposed to happen,
            for example daily, weekly, yearly, etc. The frequency needs to be a pandas offset alias.
            Please refer to pandas documentation for more information:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
        :type freq: str
        :param forecasting_parameters: A ForecastingParameters object that holds all
            the forecasting specific parameters.
        :type forecasting_parameters: azureml.automl.core.forecasting_parameters.ForecastingParameters
        :param allowed_private_models: A list of private models to add to the allowed_list. Private models
            are models that are implemented in SDK/JOS, but are not yet public facing.
        :type allowed_private_models: List(str)
        :param show_deprecate_warnings: Switch to show deprecate parameter warnings.
        :param scenario: Client Scenario being used for this run, set by AutoMLConfig.
        :type sceanrio: Optional[str]
        :param environment_label: Label for the Environment used to train. Overrides JOS selected label.
        :type environment_label: Optional[str]
        :param save_mlflow: Flag for whether to save the output using MLFlow.
        :type save_mlflow: bool
        :param test_include_predictions_only: Flag for whether to only include predictions in the test run.
        :type test_include_predictions_only: bool
        :param run_source: String used to set a RootAttribution property different from 'automl'.
        :type run_source: Optional[str]
        :param kwargs:
        """
        self._init_logging(debug_log, verbosity)
        self.path = os.path.abspath(
            path or (os.path.dirname(os.path.abspath(debug_log)) if debug_log else os.getcwd())
        )
        os.makedirs(self.path, exist_ok=True)

        self.iterations = iterations

        if primary_metric is None and task_type is None:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, argument_name="primary_metric/task_type")
            )
        elif primary_metric is None and task_type is not None:
            self.task_type = task_type
            if task_type == constants.Tasks.CLASSIFICATION:
                self.primary_metric = constants.Metric.Accuracy
            elif task_type == constants.Tasks.REGRESSION:
                self.primary_metric = constants.Metric.Spearman
        elif primary_metric is not None and task_type is None:
            self.primary_metric = primary_metric
            if self.primary_metric in constants.Metric.REGRESSION_PRIMARY_SET:
                self.task_type = constants.Tasks.REGRESSION
            elif self.primary_metric in constants.Metric.CLASSIFICATION_PRIMARY_SET:
                self.task_type = constants.Tasks.CLASSIFICATION
            else:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues,
                        target="primary_metric",
                        arguments="primary_metric",
                        supported_values=", ".join(
                            set.union(
                                constants.Metric.CLASSIFICATION_PRIMARY_SET, constants.Metric.REGRESSION_PRIMARY_SET
                            )
                        ),
                    )
                )
        else:
            self.primary_metric = cast(str, primary_metric)
            self.task_type = cast(str, task_type)
            if self.primary_metric not in get_primary_metrics(self.task_type):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues,
                        target="primary_metric",
                        arguments="primary_metric",
                        supported_values=", ".join(get_primary_metrics(self.task_type)),
                    )
                )

        self.positive_label = positive_label
        if self.task_type != constants.Tasks.CLASSIFICATION and self.positive_label is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentForTask,
                    target="positive_label",
                    arguments=self.positive_label,
                    task_type=self.task_type,
                )
            )

        self.data_script = data_script

        self.test_size = float(test_size) if test_size else 0.0
        self.test_include_predictions_only = test_include_predictions_only

        # TODO remove this once Miro/AutoML common code can handle None
        if validation_size is None:
            self.validation_size = 0.0
        else:
            self.validation_size = validation_size
        self.n_cross_validations = n_cross_validations

        self.y_min = y_min
        self.y_max = y_max

        self.num_classes = num_classes

        if isinstance(featurization, FeaturizationConfig):
            self.featurization = featurization.__dict__  # type: Union[str, Dict[str, Any]]
        else:
            self.featurization = featurization

        # Empty featurization config setting, run in auto featurization mode
        if isinstance(self.featurization, Dict) and FeaturizationConfig._is_featurization_dict_empty(
            self.featurization
        ):
            self.featurization = FeaturizationConfigMode.Auto

        # Flag whether to ensure or ignore package version
        # incompatibilities of Automated Machine learning's dependent packages.
        self._ignore_package_version_incompatibilities = (
            "AUTOML_IGNORE_PACKAGE_VERSION_INCOMPATIBILITIES".lower() in os.environ
        )

        # Deprecation of preprocess
        try:
            preprocess = kwargs.pop("preprocess")
            # TODO: Enable logging
            # logging.warning("Parameter `preprocess` will be deprecated. Use `featurization`")
            if self.featurization == FeaturizationConfigMode.Auto and preprocess is False:
                self.featurization = FeaturizationConfigMode.Off
            # TODO: Enable logging
            # else:
            #     logging.warning("Detected both `preprocess` and `featurization`. `preprocess` is being deprecated "
            #                     "and will be overridden by `featurization` setting.")
        except KeyError:
            pass

        time_column_name = kwargs.get("time_column_name", None)  # str
        if forecasting_parameters or time_column_name:
            # For many models run, we do not use automlconfig that sets this flag, so we need to repopulate
            # the timeseries flag based on the settings.
            is_timeseries = True

        self.is_timeseries = is_timeseries

        self.max_cores_per_iteration = max_cores_per_iteration
        self.max_concurrent_iterations = max_concurrent_iterations
        self.iteration_timeout_minutes = iteration_timeout_minutes
        self.mem_in_mb = mem_in_mb
        self.enforce_time_on_windows = enforce_time_on_windows
        self.experiment_timeout_minutes = experiment_timeout_minutes
        self.experiment_exit_score = experiment_exit_score

        # Deprecation of blacklist_models
        if blacklist_models is not None:
            if blocked_models is not None and blocked_models != blacklist_models:
                raise ConfigException._with_error(
                    AzureMLError.create(ConflictingValueForArguments, argument_name="blacklist_models/blocked_models")
                )
            blocked_models = blacklist_models

        # Deprecation of whitelist_models
        if whitelist_models is not None:
            if allowed_models is not None and allowed_models != whitelist_models:
                raise ConfigException._with_error(
                    AzureMLError.create(ConflictingValueForArguments, argument_name="whitelist_models/allowed_models")
                )
            allowed_models = whitelist_models

        # Need to verify allow/block list types prior to filter model call to ensure user gets
        # an actionable error if they provided the wrong type
        if allowed_models is not None and not isinstance(allowed_models, list):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="allowed_models",
                    argument="allowed_models",
                    actual_type=type(allowed_models),
                    expected_types="List[str]",
                )
            )
        if blocked_models is not None and not isinstance(blocked_models, list):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="blocked_models",
                    argument="blocked_models",
                    actual_type=type(blocked_models),
                    expected_types="List[str]",
                )
            )

        self.whitelist_models = self._filter_model_names_to_supported_private(allowed_models)
        self.blacklist_algos = self._filter_model_names_to_customer_facing_only(blocked_models)
        self.supported_models = self._get_supported_model_names()
        self.private_models = self._get_private_model_names()

        if self.whitelist_models is not None:
            self._validate_allowed_model_list()

        self.auto_blacklist = True
        self.blacklist_samples_reached = False
        self.exclude_nan_labels = exclude_nan_labels

        self.verbosity = verbosity
        self._debug_log = debug_log
        self.show_warnings = False
        self.model_explainability = model_explainability
        self.service_url = None
        self.sdk_url = None
        self.sdk_packages = None

        self.enable_onnx_compatible_models = enable_onnx_compatible_models
        if self.enable_onnx_compatible_models:
            # Read the config of spliting the onnx models of the featurizer and estimator parts.
            enable_split_onnx_featurizer_estimator_models = kwargs.get(
                "enable_split_onnx_featurizer_estimator_models", False
            )
            self.enable_split_onnx_featurizer_estimator_models = enable_split_onnx_featurizer_estimator_models
        else:
            self.enable_split_onnx_featurizer_estimator_models = False

        self.vm_type = vm_type

        # telemetry settings
        self.telemetry_verbosity = verbosity
        self.send_telemetry = True

        # enable/ disable neural networks for forecasting and natural language processing
        self.enable_dnn = kwargs.pop("enable_dnn", False)

        self.scenario = scenario
        self.environment_label = environment_label

        self.save_mlflow = save_mlflow

        # enable/ disable categorical indicators feature
        self.enable_categorical_indicators = cast(bool, kwargs.pop("enable_categorical_indicators", False))

        # Throw configuration exception if dataset language is specified to a non english code
        # but enable_dnn is not enabled.
        if not isinstance(self.featurization, dict) or self.featurization.get("_dataset_language", None) is None:
            # isinstance(self.featurization, dict) checks for whether featurization customization is used.
            language = "eng"
        else:
            language = self.featurization.get("_dataset_language", "eng")
        if language != "eng" and self.task_type == constants.Tasks.CLASSIFICATION and not self.enable_dnn:
            raise ConfigException._with_error(
                AzureMLError.create(NonDnnTextFeaturizationUnsupported, target="_dataset_language")
            )

        self.force_text_dnn = kwargs.pop("force_text_dnn", False)
        if (
            self.task_type == constants.Tasks.CLASSIFICATION
            and self.enable_dnn
            and self.featurization == FeaturizationConfigMode.Off
        ):
            self.featurization = FeaturizationConfigMode.Auto
            logger.info(
                "Resetting AutoMLBaseSettings param featurization='auto' " "required by DNNs for classification."
            )

        is_feature_sweeping_possible = (not is_timeseries) and (not self.enable_onnx_compatible_models)
        self.enable_feature_sweeping = is_feature_sweeping_possible and enable_feature_sweeping

        # Force enable feature sweeping so enable_dnn flag can be honored for text DNNs.
        if (
            is_feature_sweeping_possible
            and self.enable_dnn
            and self.task_type == constants.Tasks.CLASSIFICATION
            and not self.enable_feature_sweeping
        ):
            self.enable_feature_sweeping = True
            logger.info(
                "Resetting AutoMLBaseSettings param enable_feature_sweeping=True required by DNNs for classification."
            )

        # time series settings
        if is_timeseries:
            if forecasting_parameters is None:
                msg = (
                    "Using different time series parameters in AutoML configs for forecasting tasks will "
                    "be deprecated, please use ForecastingParameters class instead."
                )
                self._warning(msg, show_deprecate_warnings)
                forecasting_parameters = ForecastingParameters.from_parameters_dict(
                    kwargs, True, show_deprecate_warnings
                )
            forecasting_parameters.validate_parameters()
            # pop all the forecasting parameters to avoid set them again.
            for param in TimeSeries.ALL_FORECASTING_PARAMETERS:
                kwargs.pop(param, None)
            self.time_column_name = forecasting_parameters.time_column_name
            self.grain_column_names = forecasting_parameters.formatted_time_series_id_column_names
            self.drop_column_names = forecasting_parameters.formatted_drop_column_names
            self.max_horizon = forecasting_parameters.forecast_horizon
            self.dropna = forecasting_parameters.dropna
            self.overwrite_columns = forecasting_parameters.overwrite_columns
            self.transform_dictionary = forecasting_parameters.transform_dictionary
            self.window_size = forecasting_parameters.target_rolling_window_size
            self.country_or_region = forecasting_parameters.country_or_region_for_holidays
            self.lags = forecasting_parameters.formatted_target_lags
            self.feature_lags = forecasting_parameters.feature_lags
            self.seasonality = forecasting_parameters.seasonality
            self.use_stl = forecasting_parameters.use_stl
            self.short_series_handling = forecasting_parameters._short_series_handling
            self.freq = forecasting_parameters.freq
            self.short_series_handling_configuration = forecasting_parameters.short_series_handling_configuration
            self.target_aggregation_function = forecasting_parameters.target_aggregation_function
            self.cv_step_size = forecasting_parameters.cv_step_size
            if self.target_aggregation_function:
                logger.info(
                    "User has defined target_aggregation_function({}) for "
                    "forecasting tasks.".format(self.target_aggregation_function)
                )
            if self.n_cross_validations is None and self.cv_step_size is not None:
                logging.warning(
                    "User has defined 'cv_step_size' ({}) while not speficifying 'n_cross_validations'. "
                    "Will proceed with train/valid and ignore 'cv_step_size'.".format(self.cv_step_size)
                )

        # Early stopping settings
        self.enable_early_stopping = enable_early_stopping
        self.early_stopping_n_iters = early_stopping_n_iters

        if debug_flag:
            if "service_url" in debug_flag:
                self.service_url = debug_flag["service_url"]
            if "show_warnings" in debug_flag:
                self.show_warnings = debug_flag["show_warnings"]
            if "sdk_url" in debug_flag:
                self.sdk_url = debug_flag["sdk_url"]
            if "sdk_packages" in debug_flag:
                self.sdk_packages = debug_flag["sdk_packages"]

        # Image settings
        self.arguments = kwargs.pop("arguments", None)
        self.dataset_id = kwargs.pop("dataset_id", None)
        self.hyperdrive_config = kwargs.pop("hyperdrive_config", None)
        self.validation_dataset_id = kwargs.pop("validation_dataset_id", None)
        self.run_source = run_source

        # Deprecated param
        self.metrics = None

        self.enable_metric_confidence = kwargs.get("enable_metric_confidence", False)

        # backward compatible settings
        old_voting_ensemble_flag = kwargs.pop("enable_ensembling", None)
        old_stack_ensemble_flag = kwargs.pop("enable_stack_ensembling", None)
        enable_voting_ensemble = (
            old_voting_ensemble_flag if old_voting_ensemble_flag is not None else enable_voting_ensemble
        )
        enable_stack_ensemble = (
            old_stack_ensemble_flag if old_stack_ensemble_flag is not None else enable_stack_ensemble
        )

        if self.enable_onnx_compatible_models:
            if enable_stack_ensemble:
                logging.warning(
                    "Disabling Stack Ensemble iteration because ONNX convertible models were chosen. \
                    Currently Stack Ensemble is not ONNX compatible."
                )
            # disable Stack Ensemble until support for ONNX comes in
            enable_stack_ensemble = False

        if is_timeseries:
            if enable_stack_ensemble is None:
                # disable stack ensemble for time series tasks as the validation sets can be really small,
                # not enough to train the Stack Ensemble meta learner
                logging.info(
                    "Disabling Stack Ensemble by default for TimeSeries task, \
                    to avoid any overfitting when validation dataset is small."
                )
                enable_stack_ensemble = False
            elif enable_stack_ensemble:
                logging.warning("Stack Ensemble can potentially overfit for TimeSeries tasks.")

        if enable_stack_ensemble is None:
            # if nothing has disabled StackEnsemble so far, enable it.
            enable_stack_ensemble = True
        total_ensembles = 0
        if enable_voting_ensemble:
            total_ensembles += 1
        if enable_stack_ensemble:
            total_ensembles += 1

        if self.iterations >= AutoMLBaseSettings.MINIMUM_REQUIRED_ITERATIONS_ENSEMBLE + total_ensembles:
            self.enable_ensembling = enable_voting_ensemble
            self.enable_stack_ensembling = enable_stack_ensemble
            if ensemble_iterations is not None:
                self.ensemble_iterations = ensemble_iterations  # type: Optional[int]
            else:
                self.ensemble_iterations = min(
                    AutoMLBaseSettings.MAXIMUM_DEFAULT_ENSEMBLE_SELECTION_ITERATIONS, self.iterations
                )
        else:
            self.enable_ensembling = False
            self.enable_stack_ensembling = False
            self.ensemble_iterations = None

        self.enable_tf = enable_tf
        self.enable_subsampling = enable_subsampling
        self.subsample_seed = subsample_seed
        self.enable_nimbusml = False if enable_nimbusml is None else enable_nimbusml
        self.enable_streaming = False if enable_streaming is None else enable_streaming
        self.force_streaming = False if force_streaming is None else force_streaming

        self.track_child_runs = track_child_runs

        empty_list_str = []  # type: List[str]
        self.allowed_private_models = allowed_private_models if allowed_private_models is not None else empty_list_str

        self.label_column_name = label_column_name
        self.weight_column_name = weight_column_name
        self.cv_split_column_names = cv_split_column_names
        self.enable_local_managed = enable_local_managed
        self._local_managed_run_id = kwargs.pop("_local_managed_run_id", None)

        self.cost_mode = cost_mode
        # Show warnings for deprecating lag_length

        lags = kwargs.pop("lag_length", 0)
        if lags is None:
            lags = 0
        if lags != 0:
            msg = (
                "Parameter 'lag_length' will be deprecated. Please use "
                "target_lags parameter in forecasting task to set it."
            )
            self._warning(msg, show_deprecate_warnings)
        setattr(self, "lag_length", lags)

        # If there are any private allowed models, add them to the allowed list
        if self.whitelist_models is not None:
            self.whitelist_models.extend(self.allowed_private_models)
            self.whitelist_models = list(set(self.whitelist_models))  # Remove any possible duplicates.
        elif len(self.allowed_private_models) > 0:
            self.whitelist_models = self.allowed_private_models.copy()

        self._verify_settings()

        # Settings that need to be set after verification
        if self.task_type is not None and self.primary_metric is not None:
            self.metric_operation = minimize_or_maximize(task=self.task_type, metric=self.primary_metric)
        else:
            self.metric_operation = None

        # Deprecation of concurrent_iterations
        try:
            concurrent_iterations = kwargs.pop("concurrent_iterations")  # type: int
            msg = "Parameter 'concurrent_iterations' will be deprecated. Use 'max_concurrent_iterations'"
            self._warning(msg, show_deprecate_warnings)
            self.max_concurrent_iterations = concurrent_iterations
        except KeyError:
            pass

        # Deprecation of max_time_sec
        try:
            max_time_sec = kwargs.pop("max_time_sec")  # type: int
            msg = "Parameter 'max_time_sec' will be deprecated. Use 'iteration_timeout_minutes'"
            self._warning(msg, show_deprecate_warnings)
            if max_time_sec:
                self.iteration_timeout_minutes = math.ceil(max_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_time_sec
        try:
            exit_time_sec = kwargs.pop("exit_time_sec")  # type: int
            msg = "Parameter 'exit_time_sec' will be deprecated. Use 'experiment_timeout_minutes'"
            self._warning(msg, show_deprecate_warnings)
            if exit_time_sec:
                self.experiment_timeout_minutes = math.ceil(exit_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_score
        try:
            exit_score = kwargs.pop("exit_score")
            msg = "Parameter 'exit_score' will be deprecated. Use 'experiment_exit_score'"
            self._warning(msg, show_deprecate_warnings)
            self.experiment_exit_score = exit_score
        except KeyError:
            pass

        # Deprecation of blacklist_algos
        try:
            old_algos_param = kwargs.pop("blacklist_algos")
            # TODO: Re-enable this warning once we change everything to use blacklist_models
            # logging.warning("Parameter 'blacklist_algos' will be deprecated. Use 'blacklist_models.'")
            if self.blacklist_algos and old_algos_param is not None:
                self.blacklist_algos = self.blacklist_algos + self._filter_model_names_to_customer_facing_only(
                    list(set(old_algos_param) - set(self.blacklist_algos))
                )
            else:
                self.blacklist_algos = self._filter_model_names_to_customer_facing_only(old_algos_param)
        except KeyError:
            pass

        # Deprecation of preprocess
        # preprocess flag is preserved in here only to be accessible from JOS validation service.
        self.preprocess = False if self.featurization == FeaturizationConfigMode.Off else True

        # Update custom dimensions
        automl_core_sdk_version = pkg_resources.get_distribution("azureml-automl-core").version
        if self.is_timeseries:
            task_type = "forecasting"
        else:
            task_type = self.task_type
        custom_dimensions = {"task_type": task_type, "automl_core_sdk_version": automl_core_sdk_version}
        log_server.update_custom_dimensions(custom_dimensions)

        for key, value in kwargs.items():
            if key not in self.__dict__.keys():
                msg = "Received unrecognized parameter {}".format(key)
                logging.warning(msg)  # print warning to console
            setattr(self, key, value)

    @property
    def debug_log(self) -> Optional[str]:
        return self._debug_log

    @debug_log.setter
    def debug_log(self, debug_log: Optional[str]) -> None:
        """
        Set the new log file path. Setting this will also update the log server with the new path.

        :param debug_log:
        :return:
        """
        self._debug_log = debug_log
        log_server.set_log_file(debug_log)

    @property
    def _instrumentation_key(self) -> str:
        return ""

    def _init_logging(self, debug_log: Optional[str], verbosity: int) -> None:
        """
        Initialize logging system using the user provided log file and verbosity.

        :return:
        """
        if debug_log is not None:
            log_server.set_log_file(debug_log)
        if self._instrumentation_key:
            log_server.enable_telemetry(self._instrumentation_key)
        log_server.set_verbosity(verbosity)

    def _verify_settings(self):
        """
        Verify that input automl_settings are sensible.

        TODO (#357763): Reorganize the checks here and in AutoMLConfig and see what's redundant/can be reworked.

        :return:
        :rtype: None
        """
        if self.validation_size is not None:
            if self.validation_size > 1.0 or self.validation_size < 0.0:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange, target="validation_size", argument_name="validation_size", min=0, max=1
                    )
                )

        if self.n_cross_validations is not None:
            if not isinstance(self.n_cross_validations, int):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType,
                        target="n_cross_validations",
                        argument="n_cross_validations",
                        actual_type=type(self.n_cross_validations),
                        expected_types="int",
                    )
                )
            if self.n_cross_validations < 2 or self.n_cross_validations > AutoMLBaseSettings.MAX_N_CROSS_VALIDATIONS:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange,
                        target="n_cross_validations",
                        argument_name="n_cross_validations",
                        min=2,
                        max=AutoMLBaseSettings.MAX_N_CROSS_VALIDATIONS,
                    )
                )
            if self.enable_dnn and self.task_type == constants.Tasks.CLASSIFICATION:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments,
                        target="enable_dnn",
                        feature_name="enable_dnn",
                        arguments=", ".join(["n_cross_validations", self.task_type]),
                    )
                )

        if self.cv_split_column_names is not None and self.enable_streaming:
            raise ConfigException._with_error(
                AzureMLError.create(
                    FeatureUnsupportedForIncompatibleArguments,
                    target="enable_streaming",
                    feature_name="enable_streaming",
                    arguments="cv_split_column_names",
                )
            )

        if self.iterations < 0 or self.iterations > constants.MAX_ITERATIONS:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="iterations",
                    argument_name="iterations",
                    min=0,
                    max=constants.MAX_ITERATIONS,
                )
            )

        ensemble_enabled = self.enable_ensembling or self.enable_stack_ensembling
        if ensemble_enabled and cast(int, self.ensemble_iterations) < 1:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="ensemble_iterations",
                    argument_name="ensemble_iterations",
                    min=1,
                    max=self.iterations,
                )
            )

        if ensemble_enabled and cast(int, self.ensemble_iterations) > self.iterations:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="ensemble_iterations",
                    argument_name="ensemble_iterations",
                    min=1,
                    max=self.iterations,
                )
            )

        if self.path is not None and not isinstance(self.path, str):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="path",
                    argument="path",
                    actual_type=type(self.path),
                    expected_types="str",
                )
            )

        if (
            self.max_cores_per_iteration is not None
            and self.max_cores_per_iteration != -1
            and (
                self.max_cores_per_iteration < 1
                or self.max_cores_per_iteration > AutoMLBaseSettings.MAX_CORES_PER_ITERATION
            )
        ):
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="max_cores_per_iteration",
                    argument_name="max_cores_per_iteration",
                    min=1,
                    max=AutoMLBaseSettings.MAX_CORES_PER_ITERATION,
                )
            )
        if self.max_concurrent_iterations is not None and self.max_concurrent_iterations < 1:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="max_concurrent_iterations",
                    argument_name="max_concurrent_iterations",
                    min=1,
                    max="inf",
                )
            )
        if self.iteration_timeout_minutes is not None and (
            self.iteration_timeout_minutes < 1
            or self.iteration_timeout_minutes > AutoMLBaseSettings.MAXIMUM_ITERATION_TIMEOUT_MINUTES
        ):
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="iteration_timeout_minutes",
                    argument_name="iteration_timeout_minutes",
                    min=1,
                    max=AutoMLBaseSettings.MAXIMUM_ITERATION_TIMEOUT_MINUTES,
                )
            )
        if self.mem_in_mb is not None and (
            self.mem_in_mb < 1 or self.mem_in_mb > AutoMLBaseSettings.MAXIMUM_MEM_IN_MB
        ):
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="mem_in_mb",
                    argument_name="mem_in_mb",
                    min=1,
                    max=AutoMLBaseSettings.MAXIMUM_MEM_IN_MB,
                )
            )
        if self.enforce_time_on_windows is not None and not isinstance(self.enforce_time_on_windows, bool):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="enforce_time_on_windows",
                    argument="enforce_time_on_windows",
                    actual_type=type(self.enforce_time_on_windows),
                    expected_types="boolean",
                )
            )
        if self.experiment_timeout_minutes is not None and (
            self.experiment_timeout_minutes < AutoMLBaseSettings.MIN_EXPTIMEOUT_MINUTES
            or self.experiment_timeout_minutes > AutoMLBaseSettings.MAXIMUM_EXPERIMENT_TIMEOUT_MINUTES
        ):
            # The user facing setting is hours, so convert back so users get the appropriate message
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="experiment_timeout_hours",
                    argument_name="experiment_timeout_hours",
                    min=AutoMLBaseSettings.MIN_EXPTIMEOUT_MINUTES / 60,
                    max=AutoMLBaseSettings.MAXIMUM_EXPERIMENT_TIMEOUT_MINUTES / 60,
                )
            )
        if self.blacklist_algos is not None and not isinstance(self.blacklist_algos, list):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="blocked_models",
                    argument="blocked_models",
                    actual_type=type(self.blacklist_algos),
                    expected_types="List[str]",
                )
            )
        if not isinstance(self.exclude_nan_labels, bool):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="exclude_nan_labels",
                    argument="exclude_nan_labels",
                    actual_type=type(self.exclude_nan_labels),
                    expected_types="boolean",
                )
            )
        if self.debug_log is not None and not isinstance(self.debug_log, str):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="debug_log",
                    argument="debug_log",
                    actual_type=type(self.self.debug_log),
                    expected_types="str",
                )
            )
        if self.is_timeseries:
            if isinstance(self.featurization, dict):
                self._validate_timeseries_featurization_settings(self.featurization)
            if self.task_type == constants.Tasks.CLASSIFICATION:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments,
                        target="task_type",
                        feature_name="Timeseries",
                        arguments="self.task_type",
                    )
                )

            lag_length = getattr(self, "lag_length", 0)
            if lag_length < 0 or lag_length > AutoMLBaseSettings.MAX_LAG_LENGTH:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange,
                        target="lag_length",
                        argument_name="lag_length ({})".format(lag_length),
                        min=0,
                        max=AutoMLBaseSettings.MAX_LAG_LENGTH,
                    )
                )

        if self.enable_onnx_compatible_models:
            incompatibility_reasons = []
            if sys.version_info >= OnnxConvertConstants.OnnxIncompatiblePythonVersion:
                major = OnnxConvertConstants.OnnxIncompatiblePythonVersion[0]
                minor = OnnxConvertConstants.OnnxIncompatiblePythonVersion[1]
                incompatibility_reasons.append("Python Version >= {}.{}".format(major, minor))
            if self.is_timeseries:
                incompatibility_reasons.append("is_timeseries")
            if self.enable_tf:
                incompatibility_reasons.append("enable_tf")
            if self.enable_dnn and self.task_type == constants.Tasks.CLASSIFICATION:
                incompatibility_reasons.append("enable_dnn, task_type == {}".format(constants.Tasks.CLASSIFICATION))

            if incompatibility_reasons:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments,
                        target="enable_onnx_compatible_models",
                        feature_name="enable_onnx_compatible_models",
                        arguments=", ".join(incompatibility_reasons),
                    )
                )

        if self.enable_subsampling and not isinstance(self.enable_subsampling, bool):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="enable_subsampling",
                    argument="enable_subsampling",
                    actual_type=type(self.enable_subsampling),
                    expected_types="boolean",
                )
            )
        if not self.enable_subsampling and self.subsample_seed:
            msg = 'Input parameter "enable_subsampling" is set to False but "subsample_seed" was specified.'
            self._warning(msg)
        if self.enable_subsampling and self.subsample_seed and not isinstance(self.subsample_seed, int):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType,
                    target="subsample_seed",
                    argument="subsample_seed",
                    actual_type=type(self.subsample_seed),
                    expected_types="int",
                )
            )

        self._validate_model_filter_lists()
        self._validate_allowed_private_model_list()

        if self.early_stopping_n_iters < 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    target="early_stopping_n_iters",
                    argument_name="early_stopping_n_iters",
                    min=0,
                    max="inf",
                )
            )

        if not isinstance(self.track_child_runs, bool):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidInputDatatype,
                    target="track_child_runs",
                    input_type=type(self.track_child_runs),
                    supported_types=bool.__name__,
                )
            )

    def _validate_model_filter_lists(self):
        """
        Validate that allowed_models and blocked_models are correct.

        Assumes that blacklist_algos and whitelist_models have been filtered to contain only
        valid model names.
        """

        bla = set()
        wlm = set()

        # check blocked models
        if self.blacklist_algos is not None:
            bla = set(self.blacklist_algos)
            enabled_algos = set(self._get_supported_model_names()) - bla
            if len(enabled_algos) == 0:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        AllAlgorithmsAreBlocked,
                        target="blocked_models",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_BLOCKED_ALL_MODELS,
                    )
                )

        # check whitelist
        if self.whitelist_models is not None:
            # check whitelist not empty
            if len(self.whitelist_models) == 0:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues,
                        target="allowed_models",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_ALLOWEDMODELS_EMPTY,
                        arguments="allowed_models",
                        supported_values=self._get_supported_model_names(),
                    )
                )
            wlm = set(self.whitelist_models)

            actual_wlm = wlm - bla
            shared = bla.intersection(wlm)

            if len(actual_wlm) == 0:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        AllowedModelsSubsetOfBlockedModels,
                        target="allowed_models/blocked_models",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_BLOCKED_MODELS_EQUAL_ALLOW_MODEL,
                    )
                )
            if len(shared) > 0:
                logging.warning("blocked_models and allowed_models contain shared models.")

    def _validate_allowed_model_list(self) -> None:
        # Verify if any models in _PrivateModelList is called in allowed_models
        for model in self.whitelist_models:
            if model in self.private_models:
                logging.warning(
                    "This version of the SDK does not fully support {}, "
                    "please consider upgrading the SDK via "
                    "'pip install --upgrade azureml-train-automl'.".format(model)
                )

    def _validate_allowed_private_model_list(self) -> None:
        """
        Check that models listed in allowed_private_models are set as private models in the global constants.
        """
        if self.is_timeseries:
            private_model_names = set(
                [model.customer_model_name for model in _PrivateModelNames.PrivateForecastingModelList]
            )
            # Verify all models in allowed private list are in private_model_names
            if not set(self.allowed_private_models).issubset(private_model_names):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues,
                        target="allowed_private_models",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_PRIVATEALLOWEDMODELS_INVALID,
                        arguments="allowed_private_models",
                        supported_values=list(private_model_names),
                    )
                )

    def _filter_model_names_to_customer_facing_only(self, model_names):
        if model_names is None:
            return None
        supported_model_names = self._get_supported_model_names()
        return [model for model in model_names if model in supported_model_names]

    def _filter_model_names_to_supported_private(self, model_names):
        if model_names is None:
            return None
        supported_model_names = self._get_supported_model_names()
        private_model_names = self._get_private_model_names()
        return [model for model in model_names if (model in supported_model_names or model in private_model_names)]

    def _get_supported_model_names(self):
        supported_model_names = []  # type: List[str]
        if self.task_type == constants.Tasks.CLASSIFICATION:
            supported_model_names = list(
                set([m.customer_model_name for m in SupportedModelNames.SupportedClassificationModelList])
            )
        elif self.task_type == constants.Tasks.REGRESSION:
            supported_model_names = list(
                set([model.customer_model_name for model in SupportedModelNames.SupportedRegressionModelList])
            )
        if self.is_timeseries:
            supported_model_names = list(
                set([model.customer_model_name for model in SupportedModelNames.SupportedForecastingModelList])
            )
        return supported_model_names

    def _get_private_model_names(self):
        private_model_names = []  # type: List[str]
        if self.task_type == constants.Tasks.CLASSIFICATION:
            private_model_names = list(
                set([model.customer_model_name for model in _PrivateModelNames.PrivateClassificationModelList])
            )
        elif self.task_type == constants.Tasks.REGRESSION:
            private_model_names = list(
                set([model.customer_model_name for model in _PrivateModelNames.PrivateRegressionModelList])
            )
        if self.is_timeseries:
            private_model_names = list(
                set([model.customer_model_name for model in _PrivateModelNames.PrivateForecastingModelList])
            )
        return private_model_names

    @staticmethod
    def from_string_or_dict(val: Union[Dict[str, Any], str, "AutoMLBaseSettings"]) -> "AutoMLBaseSettings":
        """
        Convert a string or dictionary containing settings to an AutoMLBaseSettings object.

        If the provided value is already an AutoMLBaseSettings object, it is simply passed through.

        :param val: the input data to convert
        :return: an AutoMLBaseSettings object
        """
        if isinstance(val, str):
            val = eval(val)
        if isinstance(val, dict):
            val = AutoMLBaseSettings(**val)

        if isinstance(val, AutoMLBaseSettings):
            return val
        else:
            raise ValueError("`input` parameter is not of type string or dict")

    def __str__(self):
        """
        Convert this settings object into human readable form.

        :return: a human readable representation of this object
        """
        output = [" - {0}: {1}".format(k, v) for k, v in self.__dict__.items()]
        return "\n".join(output)

    def _format_selective(self, black_list_keys):
        """
        Format selective items for logging.

        Returned string will look as follows below
        Example:
            - key1: value1
            - key2: value2

        :param black_list_keys: List of keys to ignore.
        :type black_list_keys: list(str)
        :return: Filterd settings as string
        :rtype: str
        """
        dict_copy = self._filter(black_list_keys=black_list_keys)
        output = [" - {0}: {1}".format(k, v) for k, v in dict_copy.items()]
        return "\n".join(output)

    def as_serializable_dict(self) -> Dict[str, Any]:
        return self._filter(["spark_context"])

    def _filter(self, black_list_keys: Optional[List[str]]) -> Dict[str, Any]:
        return dict([(k, v) for k, v in self.__dict__.items() if black_list_keys is None or k not in black_list_keys])

    def _get_featurization_config_mode(self) -> str:
        featurization = self.__dict__.get("featurization")
        if featurization:
            if isinstance(featurization, str):
                if featurization == FeaturizationConfigMode.Auto or featurization == FeaturizationConfigMode.Off:
                    return featurization
            return FeaturizationConfigMode.Customized
        return ""

    def _validate_timeseries_featurization_settings(self, featurization: Dict[str, Any]) -> None:
        """
        Validate whether the custom featurization is supported.

        :param featurization: The customized featurization config dict.
        """
        warning_msg_template = (
            "Custom {0} is currently not supported by forecasting task. "
            "All the settings related will be ignored by AutoML."
        )

        blocked_transformers = featurization.get("_blocked_transformers")
        if blocked_transformers is not None and len(blocked_transformers) > 0:
            self._warning(warning_msg_template.format("blocked_transformers"))

        self._validate_ts_column_purposes(featurization)

        self._validate_ts_featurization_drop_columns(featurization)

        self._validate_ts_featurization_transform_params(featurization)

    def _validate_ts_featurization_drop_columns(self, featurization: Dict[str, Any]) -> None:
        """
        Validate the custom featurization's drop columns.

        :param featurization: The customized featurization config dict.
        """
        drop_columns = set(featurization.get("_drop_columns") or [])

        if self.time_column_name in drop_columns:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingFeaturizationConfigReservedColumns,
                    target="drop_columns",
                    sub_config_name="drop_columns",
                    reserved_columns=self.time_column_name,
                    reference_code=ReferenceCodes._SETTINGS_CONFIG_DROP_TIME_COLUMN,
                )
            )

        shared_grain_columns = drop_columns.intersection(self.grain_column_names or [])
        if len(shared_grain_columns) > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingFeaturizationConfigReservedColumns,
                    target="drop_columns",
                    sub_config_name="drop_columns",
                    reserved_columns=",".join(shared_grain_columns),
                    reference_code=ReferenceCodes._SETTINGS_CONFIG_DROP_GRAIN_COLUMNS,
                )
            )

        shared_reserve_columns = drop_columns.intersection(constants.TimeSeriesInternal.RESERVED_COLUMN_NAMES)
        if len(shared_reserve_columns) > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingFeaturizationConfigReservedColumns,
                    target="drop_columns",
                    sub_config_name="drop_columns",
                    reserved_columns=",".join(shared_reserve_columns),
                    reference_code=ReferenceCodes._SETTINGS_CONFIG_DROP_RESERVED_COLUMNS,
                )
            )

        shared_drop_columns = drop_columns.intersection(self.drop_column_names or [])
        if len(shared_drop_columns) > 0:
            warning_msg = (
                "Featurization's drop column configuration and automl settings' drop column configuration "
                "have columns specified in common."
            )
            self._warning(warning_msg)

    def _validate_ts_featurization_strategies(
        self, transformer_params: Dict[str, List[ColumnTransformerParamType]]
    ) -> None:
        """
        Validate the custom featurization's transform params strategies.

        :param transformer_params: The customized featurization config params.
        """
        wrong_featurization_msg = (
            "Forecasting task only supports simple imputation with following strategies: {}. "
            "All other imputation settings will be ignored.".format(
                ", ".join(sorted(TransformerParams.Imputer.ForecastingEnabledStrategies))
            )
        )
        target_columns = {self.label_column_name, constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN}
        for cols, params in transformer_params[SupportedTransformers.Imputer]:
            strategy = params.get(TransformerParams.Imputer.Strategy)
            if strategy not in TransformerParams.Imputer.ForecastingEnabledStrategies:
                self._warning(wrong_featurization_msg)
            if strategy not in TransformerParams.Imputer.ForecastingTargetEnabledStrategies:
                for col in cols:
                    if col in target_columns:
                        raise ConfigException._with_error(
                            AzureMLError.create(
                                FeaturizationConfigForecastingStrategy,
                                target="featurization_config",
                                strategies=", ".join(
                                    sorted(TransformerParams.Imputer.ForecastingTargetEnabledStrategies)
                                ),
                                reference_code=ReferenceCodes._SETTINGS_CONFIG_IMPUTE_TARGET_UNSUPPORT,
                            )
                        )

    def _validate_ts_featurization_transform_params(self, featurization: Dict[str, Any]) -> None:
        """
        Validate the custom featurization's transform params.

        :param featurization: The customized featurization config dict.
        """
        transformer_params = featurization.get("_transformer_params")
        if transformer_params is not None and len(transformer_params) > 0:
            if SupportedTransformers.Imputer not in transformer_params:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        NotSupported,
                        target="featurization_config",
                        scenario_name="transformers except imputer for forecasting tasks",
                        reference_code=ReferenceCodes._FEATURIZATION_CONFIG_WRONG_TRANSFORMER_TYPE_FORECASTING,
                    )
                )
            if transformer_params.get(SupportedTransformers.Imputer) is not None:
                self._validate_ts_featurization_strategies(transformer_params)
                self._validate_ts_featurization_strategies_columns(transformer_params)
                self._validate_ts_featurization_multi_strategies_columns(transformer_params)

    def _validate_ts_featurization_strategies_columns(
        self, transformer_params: Dict[str, List[ColumnTransformerParamType]]
    ) -> None:
        """
        Validate the custom featurization's transform params column not in reserve or drop columns.

        :param transformer_params: The customized featurization config params.
        """
        drop_columns = set(self.drop_column_names or [])

        # the DUMMY_TARGET_COLUMN is used as target column for if user is using X and y as input.
        cannot_customized_reserved_columns = set(
            [
                col
                for col in constants.TimeSeriesInternal.RESERVED_COLUMN_NAMES
                if col != constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
            ]
        )

        config_dropped_columns = list()
        config_reserved_columns = list()
        all_cols = set()
        for cols, params in transformer_params[SupportedTransformers.Imputer]:
            strategy = params.get(TransformerParams.Imputer.Strategy)
            if strategy in TransformerParams.Imputer.ForecastingEnabledStrategies:
                for col in cols:
                    all_cols.add(col)
                    if col in drop_columns:
                        config_dropped_columns.append(col)
                    if col in cannot_customized_reserved_columns:
                        config_reserved_columns.append(col)

        if len(config_dropped_columns) > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingFeaturizationConfigDroppedColumns,
                    target="featurization_config",
                    sub_config_name="transformer_params",
                    dropped_columns=",".join(config_dropped_columns),
                    reference_code=ReferenceCodes._SETTINGS_CONFIG_IMPUTE_COLUMN_DROPPED,
                )
            )

        if len(config_reserved_columns) > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingFeaturizationConfigReservedColumns,
                    target="featurization_config",
                    sub_config_name="transformer_params",
                    reserved_columns=",".join(config_reserved_columns),
                    reference_code=ReferenceCodes._SETTINGS_CONFIG_IMPUTE_COLUMN_RESERVED,
                )
            )

        if self.label_column_name is not None:
            all_cols.discard(self.label_column_name)
        all_cols.discard(constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN)
        if all_cols:
            self._validate_none_target_agg_func("featurization config non label column name customized imputation")

    def _validate_ts_featurization_multi_strategies_columns(
        self, transformer_params: Dict[str, List[ColumnTransformerParamType]]
    ) -> None:
        """
        Validate the custom featurization's transform params column not have different stategies.

        :param transformer_params: The customized featurization config params.
        """
        col_strategies = dict()  # type: Dict[str, List[str]]
        for cols, params in transformer_params[SupportedTransformers.Imputer]:
            strategy = params.get(TransformerParams.Imputer.Strategy)
            if strategy in TransformerParams.Imputer.ForecastingEnabledStrategies:
                for col in cols:
                    if col in col_strategies:
                        col_strategies[col].append(strategy)
                    else:
                        col_strategies[col] = [strategy]

        error_msg_list = []
        for col, imputers in col_strategies.items():
            if len(imputers) > 1:
                error_msg_list.append("{}: {}".format(col, ", ".join(imputers)))
        if len(error_msg_list) > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    FeaturizationConfigMultipleImputers,
                    target="featurization_config",
                    columns="\n".join(error_msg_list),
                    reference_code=ReferenceCodes._SETTINGS_CONFIG_IMPUTE_COLUMN_CONFLICT,
                )
            )

    def _validate_ts_column_purposes(self, featurization: Dict[str, Any]) -> None:
        """
        Validate the column purposes in featurization config for forecasting tasks.

        :param featurization: The featurizaiton config dict.
        :raises: Column purpose column in settings.drop_column_names.
        """
        column_purposes = featurization.get("_column_purposes")
        if not column_purposes:
            return None

        self._validate_none_target_agg_func("featurization config column purposes")

        ts_enabled_column_purposes = {FeatureType.DateTime, FeatureType.Numeric, FeatureType.Categorical}

        drop_columns = set(self.drop_column_names or [])

        unsupported_cols = set()
        dropped_cols = list()
        for col, purpose in column_purposes.items():
            if purpose not in ts_enabled_column_purposes:
                unsupported_cols.add(col)
            if col in drop_columns:
                dropped_cols.append(col)

        unsupported_warning_msg = (
            "Forecasting supports the following column purposes only: {}. "
            "All other inputs will be ignored".format(", ".join(ts_enabled_column_purposes))
        )
        if len(unsupported_cols) > 0:
            self._warning(unsupported_warning_msg)

        if len(dropped_cols) > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingFeaturizationConfigDroppedColumns,
                    target="featurization_config",
                    sub_config_name="column_purposes",
                    dropped_columns=",".join(dropped_cols),
                    reference_code=ReferenceCodes._SETTINGS_CONFIG_DROP_COLUMN_PURPOSE,
                )
            )

    def _validate_none_target_agg_func(self, featurization_config_name):
        if self.target_aggregation_function:
            raise ConfigException._with_error(
                AzureMLError.create(
                    NotSupported,
                    target="featurization_config",
                    scenario_name="target_aggregation_function with {}".format(featurization_config_name),
                    reference_code=ReferenceCodes._FORECASTING_FEATURIZATION_CONFIG_TARGET_AGG_NOT_SUPPORTED,
                )
            )

    def _warning(self, msg: str, show_warnings: Optional[bool] = True) -> None:
        if show_warnings:
            logging.warning(msg)  # print warning to console
            logger.warning(msg)  # print warning to logs
