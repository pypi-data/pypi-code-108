# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Manages settings for AutoML experiment."""
from typing import Any, cast, Dict, Mapping, Optional, Union
import logging
import os

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentOutOfRange, BadArgument
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InvalidArgumentType,
    InvalidComputeTargetForDatabricks,
    XGBoostAlgosAllowedButNotInstalled)
from azureml.telemetry import INSTRUMENTATION_KEY
import azureml.automl.core.shared.exceptions as common_exceptions
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.constants import FeaturizationConfigMode
from azureml.automl.core.shared import constants
from azureml.core.compute import ComputeTarget, DatabricksCompute
from azureml.core.experiment import Experiment
from .constants import Scenarios, PIPELINE_FETCH_BATCH_SIZE_LIMIT
from .exceptions import ConfigException


logger = logging.getLogger(__name__)


class AzureAutoMLSettings(AutoMLBaseSettings):
    """Persist and validate settings for an AutoML experiment."""

    # Default experiment timeout in minutes.
    DEFAULT_EXPERIMENT_TIMEOUT = int(constants.AutoMLDefaultTimeouts.DEFAULT_EXPERIMENT_TIMEOUT_SECONDS / 60.0)

    def __init__(self,
                 experiment=None,
                 path=None,
                 iterations=None,
                 data_script=None,
                 primary_metric=None,
                 task_type=None,
                 compute_target=None,
                 spark_context=None,
                 test_size=None,
                 validation_size=None,
                 n_cross_validations=None,
                 y_min=None,
                 y_max=None,
                 num_classes=None,
                 featurization=FeaturizationConfigMode.Auto,
                 max_cores_per_iteration=1,
                 max_concurrent_iterations=1,
                 iteration_timeout_minutes=None,
                 mem_in_mb=None,
                 enforce_time_on_windows=None,
                 experiment_timeout_minutes=None,
                 experiment_exit_score=None,
                 enable_early_stopping=True,
                 blacklist_models=None,
                 whitelist_models=None,
                 exclude_nan_labels=True,
                 verbosity=logging.INFO,
                 debug_log='automl.log',
                 debug_flag=None,
                 enable_voting_ensemble=True,
                 enable_stack_ensemble=None,
                 ensemble_iterations=None,
                 model_explainability=True,
                 enable_tf=True,
                 enable_subsampling=None,
                 subsample_seed=None,
                 cost_mode=constants.PipelineCost.COST_NONE,
                 is_timeseries=False,
                 enable_onnx_compatible_models=False,
                 scenario=Scenarios.SDK,
                 environment_label=None,
                 show_deprecate_warnings=False,
                 enable_local_managed=False,
                 **kwargs):
        """
        Manage settings used by AutoML components.

        :param experiment: The azureml.core experiment
        :param path: Full path to the project folder
        :param iterations: Number of different pipelines to test
        :param data_script: File path to the script containing get_data()
        :param primary_metric: The metric that you want to optimize.
        :param task_type: Field describing whether this will be a classification or regression experiment
        :param compute_target: The AzureML compute to run the AutoML experiment on
        :param spark_context: Spark context, only applicable when used inside azure databricks/spark environment.
        :type spark_context: SparkContext
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
        :param enable_early_stopping: flag to turn early stopping on when AutoML scores are not progressing.
        :param blacklist_models: List of algorithms to ignore for AutoML experiment
        :param whitelist_models: List of model names to search for AutoML experiment
        :param exclude_nan_labels: Flag whether to exclude rows with NaN values in the label
        :param verbosity: Verbosity level for AutoML log file
        :param debug_log: File path to AutoML logs
        :param enable_voting_ensemble: Flag to enable/disable an extra iteration for Voting ensemble.
        :param enable_stack_ensemble: Flag to enable/disable an extra iteration for Stack ensemble.
        :param ensemble_iterations: Number of models to consider for the ensemble generation
        :param model_explainability: Flag whether to explain best AutoML model at the end of training iterations.
        :param enable_TF: Flag to enable/disable Tensorflow algorithms
        :param enable_subsampling: Flag to enable/disable subsampling. Note that even if it's true,
            subsampling would not be enabled for small datasets or iterations.
        :param subsample_seed: random_state used to sample the data.
        :param cost_mode: Flag to set cost prediction modes. COST_NONE stands for none cost prediction,
            COST_FILTER stands for cost prediction per iteration.
        :type cost_mode: int or azureml.automl.core.shared.constants.PipelineCost
        :param is_timeseries: Flag whether AutoML should process your data as time series data.
        :type is_timeseries: bool
        :param enable_onnx_compatible_models: Flag to enable/disable enforcing the onnx compatible models.
        :param target_lags: The number of past periods to lag from the target column.

            When forecasting, this parameter represents the number of rows to lag the target values based
            on the frequency of the data. This is represented as a list or single integer. Lag should be used
            when the relationship between the independent variables and dependant variable do not match up or
            correlate by default. For example, when trying to forecast demand for a product, the demand in any
            month may depend on the price of specific commodities 3 months prior. In this example, you may want
            to lag the target (demand) negatively by 3 months so that the model is training on the correct
            relationship.
        :type target_lags: int
        :param feature_lags: Flag for generating lags for the numeric features
        :type feature_lags: str
        :param short_series_handling_configuration:
            The parameter defining how if AutoML should handle short time series.

            Possible values: 'auto' (default), 'pad', 'drop' and None.
            * **auto** short series will be padded if there are no long series,
            otherwise short series will be dropped.
            * **pad** all the short series will be padded.
            * **drop**  all the short series will be dropped".
            * **None** the short series will not be modified.
            If set to 'pad', the table will be padded with the zeroes and
            empty values for the regressors and random values for target with the mean
            equal to target value median for given time series id. If median is more or equal
            to zero, the minimal padded value will be clipped by zero:
            Input:

            +------------+---------------+----------+--------+
            | Date       | numeric_value | string   | target |
            +============+===============+==========+========+
            | 2020-01-01 | 23            | green    | 55     |
            +------------+---------------+----------+--------+
            Output assuming minimal number of values is four:
            +------------+---------------+----------+--------+
            | Date       | numeric_value | string   | target |
            +============+===============+==========+========+
            | 2019-12-29 | 0             | NA       | 55.1   |
            +------------+---------------+----------+--------+
            | 2019-12-30 | 0             | NA       | 55.6   |
            +------------+---------------+----------+--------+
            | 2019-12-31 | 0             | NA       | 54.5   |
            +------------+---------------+----------+--------+
            | 2020-01-01 | 23            | green    | 55     |
            +------------+---------------+----------+--------+

            **Note:** We have two parameters short_series_handling_configuration and
            legacy short_series_handling. When both parameters are set we are
            synchronize them as shown in the table below (short_series_handling_configuration and
            short_series_handling for brevity are marked as handling_configuration and handling
            respectively).

            +-----------+------------------------+--------------------+----------------------------------+
            |  handling | handling_configuration | resulting handling | resulting handling_configuration |
            +===========+========================+====================+==================================+
            | True      | auto                   | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | pad                    | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | drop                   | True               | auto                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | True      | None                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | auto                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | pad                    | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | drop                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+
            | False     | None                   | False              | None                             |
            +-----------+------------------------+--------------------+----------------------------------+

        :type short_series_handling_configuration: str
        :param freq: Forecast frequency.

            When forecasting, this parameter represents the period with which the forecast is desired,
            for example daily, weekly, yearly, etc. The forecast frequency is dataset frequency by default.
            You can optionally set it to greater (but not lesser) than dataset frequency.
            We'll aggregate the data and generate the results at forecast frequency. For example,
            for daily data, you can set the frequency to be daily, weekly or monthly, but not hourly.
            The frequency needs to be a pandas offset alias.
            Please refer to pandas documentation for more information:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
        :type freq: str or None
        :param target_aggregation_function: The function to be used to aggregate the time series target
                                            column to conform to a user specified frequency. If the
                                            target_aggregation_function is set, but the freq parameter
                                            is not set, the error is raised. The possible target
                                            aggregation functions are: "sum", "max", "min" and "mean".

                +----------------+-----------------------------+---------------------------------------------+
                |      freq      | target_aggregation_function |      Data regularity fixing mechanism       |
                +================+=============================+=============================================+
                | None (Default) | None (Default)              | The aggregation is not applied.             |
                |                |                             | If the valid frequency can not be           |
                |                |                             | determined the error will be raised.        |
                +----------------+-----------------------------+---------------------------------------------+
                | Some Value     | None (Default)              | The aggregation is not applied.             |
                |                |                             | If the number of data points compliant      |
                |                |                             | to given frequency grid is less then 90%    |
                |                |                             | these points will be removed, otherwise     |
                |                |                             | the error will be raised.                   |
                +----------------+-----------------------------+---------------------------------------------+
                | None (Default) | Aggregation function        | The error about missing frequency parameter |
                |                |                             | is raised.                                  |
                +----------------+-----------------------------+---------------------------------------------+
                | Some Value     | Aggregation function        | Aggregate to frequency using provided       |
                |                |                             | aggregation function.                       |
                +----------------+-----------------------------+---------------------------------------------+

        :type target_aggregation_function: str or None
        :param show_deprecate_warnings: Switch to show deprecate parameter warnings.
        :param environment_label: Label for the Environment used to train. Overrides JOS selected label.
        :type environment_label: Optional[str]
        :param kwargs:
        """
        self.path = path
        if experiment is None:
            self.name = None
            self.subscription_id = None
            self.resource_group = None
            self.workspace_name = None
            self.region = None

            # For now, if we don't have a workspace to work off of, just use the fallback key
            self._telemetry_instrumentation_key = None
        else:
            # This is used in the remote case values are populated through AMLSettings
            self.name = experiment.name
            self.subscription_id = experiment.workspace.subscription_id
            self.resource_group = experiment.workspace.resource_group
            self.workspace_name = experiment.workspace.name
            self.region = experiment.workspace.location
            try:
                # This makes a service call, so it can fail
                self._telemetry_instrumentation_key = \
                    cast(Optional[str], experiment.workspace._sdk_telemetry_app_insights_key)
            except Exception:
                self._telemetry_instrumentation_key = None
        self.compute_target = compute_target
        self.spark_context = spark_context
        self.spark_service = 'adb' if self.spark_context else None
        self.azure_service = os.environ.get('AZURE_SERVICE', 'Microsoft.AzureDataBricks') \
            if self.spark_context else None

        # if enable_subsampling is specified to be True or False, we do whatever the user wants
        # otherwise we will follow the following rules:
        #   off if iterations is specified
        #   off if it is timeseries
        #   otherwise we leave it for automl._subsampling_recommended() to decide
        #   based off num_samples and num_features after featurization stage
        if enable_subsampling is None:
            if iterations is not None or is_timeseries:
                enable_subsampling = False

        if iterations is None and experiment_timeout_minutes is None:
            enable_early_stopping = True

        if iterations is None:
            iterations = 1000

        if experiment_timeout_minutes is None:
            experiment_timeout_minutes = AzureAutoMLSettings.DEFAULT_EXPERIMENT_TIMEOUT

        # Whether or not this is a Many Models run
        self.many_models = kwargs.pop('many_models', False)

        # Max number of next pipelines to fetch from Jasmine
        self.pipeline_fetch_max_batch_size = kwargs.pop('pipeline_fetch_max_batch_size', 1)

        # Whether to enable batch run. This is currently enabled for remote experiments on their landmark runs
        self.enable_batch_run = kwargs.pop('enable_batch_run', False)

        # Whether to enable run restructure.
        self.enable_run_restructure = kwargs.pop('enable_run_restructure', False)

        # Whether to start the model explain and model test
        # runs before the parent is marked as complete.
        self.start_auxiliary_runs_before_parent_complete = \
            kwargs.pop('start_auxiliary_runs_before_parent_complete', False)

        # Whether to enable code generation during training for this experiment.
        self.enable_code_generation = kwargs.pop('enable_code_generation', False)

        # Set the rest of the instance variables and have base class verify settings
        super().__init__(
            path=path,
            iterations=iterations,
            data_script=data_script,
            primary_metric=primary_metric,
            task_type=task_type,
            compute_target=compute_target,
            test_size=test_size,
            validation_size=validation_size,
            n_cross_validations=n_cross_validations,
            y_min=y_min,
            y_max=y_max,
            num_classes=num_classes,
            featurization=featurization,
            max_cores_per_iteration=max_cores_per_iteration,
            max_concurrent_iterations=max_concurrent_iterations,
            iteration_timeout_minutes=iteration_timeout_minutes,
            mem_in_mb=mem_in_mb,
            enforce_time_on_windows=enforce_time_on_windows,
            experiment_timeout_minutes=experiment_timeout_minutes,
            experiment_exit_score=experiment_exit_score,
            enable_early_stopping=enable_early_stopping,
            blacklist_models=blacklist_models,
            whitelist_models=whitelist_models,
            exclude_nan_labels=exclude_nan_labels,
            verbosity=verbosity,
            debug_log=debug_log,
            debug_flag=debug_flag,
            enable_voting_ensemble=enable_voting_ensemble,
            enable_stack_ensemble=enable_stack_ensemble,
            ensemble_iterations=ensemble_iterations,
            model_explainability=model_explainability,
            enable_tf=enable_tf,
            enable_subsampling=False,
            subsample_seed=subsample_seed,
            cost_mode=cost_mode,
            is_timeseries=is_timeseries,
            enable_onnx_compatible_models=enable_onnx_compatible_models,
            show_deprecate_warnings=show_deprecate_warnings,
            scenario=scenario,
            enable_local_managed=enable_local_managed,
            environment_label=environment_label,
            **kwargs)

        # temporary measure to bypass the typecheck in base settings in common core
        # will remove once changes are in common core
        self.enable_subsampling = enable_subsampling

    def as_serializable_dict(self) -> Dict[str, Any]:
        return self._filter(['spark_context', '_experiment', '_telemetry_instrumentation_key'])

    @property
    def _instrumentation_key(self) -> str:
        if self._telemetry_instrumentation_key:
            return ",".join([str(self._telemetry_instrumentation_key), INSTRUMENTATION_KEY])
        return cast(str, INSTRUMENTATION_KEY)

    def apply_optional_package_filter(self) -> None:
        """Apply any missing optional pacakges to the blocklist if they arent installed."""

        default_warning = '{0} is included in recommended algorithms list but not installed locally. '\
            'If you would like to include {0} models in the recommended algorithms '\
            'please install {0} locally. Adding {0} to the blacklist.'
        xgbc = constants.SupportedModels.Classification.XGBoostClassifier
        xgbr = constants.SupportedModels.Regression.XGBoostRegressor
        model = None
        # If xgboost is in allowed list but not installed, remove it and print a warning.
        try:
            import xgboost
        except ImportError:
            if self.task_type == constants.Tasks.CLASSIFICATION:
                model = xgbc
            else:
                model = xgbr

            if self.whitelist_models == [model]:
                raise ConfigException._with_error(AzureMLError.create(XGBoostAlgosAllowedButNotInstalled,
                                                                      target=model,
                                                                      version=constants.XGBOOST_SUPPORTED_VERSION))
            elif self.whitelist_models is not None and model in self.whitelist_models:
                logging.warning("{} is in the allowed models list, but xgboost is not installed.".format(model))

            if self.blacklist_algos is None:
                self.blacklist_algos = [model]
                logger.warning(default_warning.format(model))
            else:
                if model not in self.blacklist_algos:
                    self.blacklist_algos.append(model)
                    logger.warning(default_warning.format(model))

        if self.is_timeseries:
            prophet = constants.SupportedModels.Forecasting.Prophet
            try:
                from azureml.automl.core.shared import import_utilities
                import_utilities.import_fbprophet()
            except (ImportError, RuntimeError):
                logger.warning(default_warning.format(prophet))
                if self.blacklist_algos is None:
                    self.blacklist_algos = [prophet]
                elif constants.SupportedModels.Forecasting.Prophet not in self.blacklist_algos:
                    self.blacklist_algos.append(prophet)

        self._validate_model_filter_lists()

    def _verify_settings(self) -> None:
        """
        Verify that input automl_settings are sensible.

        TODO (#357763): Reorganize the checks here and in AutoMLConfig and see what's redundant/can be reworked.

        :return:
        :rtype: None
        """
        # Base settings object will do most of the verification. Only add AzureML-specific checks here.
        try:
            super()._verify_settings()
        except ValueError as e:
            # todo figure out how this is reachable, and if it's right to raise it as ConfigException
            raise ConfigException._with_error(
                AzureMLError.create(BadArgument, target="_verify_settings", argument_name=str(e))
            )
        except (common_exceptions.ConfigException, common_exceptions.ValidationException):
            raise
        if self.compute_target is not None and not isinstance(self.compute_target, str) and \
                not isinstance(self.compute_target, ComputeTarget):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="compute_target",
                    argument="compute_target", actual_type=type(self.compute_target),
                    expected_types=", ".join(["str", "azureml.core.compute.ComputeTarget"]))
            )

        if isinstance(self.compute_target, DatabricksCompute) or \
                (isinstance(self.compute_target, str) and self.compute_target.lower() == 'databricks'):
            raise ConfigException._with_error(
                AzureMLError.create(InvalidComputeTargetForDatabricks, target="compute_target")
            )

        if self.pipeline_fetch_max_batch_size <= 0 or \
                self.pipeline_fetch_max_batch_size > PIPELINE_FETCH_BATCH_SIZE_LIMIT:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target="pipeline_fetch_max_batch_size",
                    argument_name="pipeline_fetch_max_batch_size", min=1, max=PIPELINE_FETCH_BATCH_SIZE_LIMIT
                )
            )

    @staticmethod
    def from_string_or_dict(val: Union[str, Dict[str, Any], AutoMLBaseSettings],
                            experiment: Optional[Experiment] = None,
                            overrides: Optional[Mapping[str, Any]] = None) -> 'AzureAutoMLSettings':
        """
        Convert a string or dictionary containing settings to an AzureAutoMLSettings object.

        If the provided value is already an AzureAutoMLSettings object, it is simply passed through.
        Specifying overrides will cause those settings to be overridden.

        :param val: the input data to convert
        :param experiment: the experiment being run
        :param overrides: setting overrides to use
        :return: an AzureAutoMLSettings object
        """
        if isinstance(val, str):
            val = eval(val)
        if isinstance(val, dict):
            if overrides is not None:
                val.update(overrides)
            return AzureAutoMLSettings(experiment=experiment, **val)

        if isinstance(val, AzureAutoMLSettings):
            if overrides is not None:
                for k, v in overrides.items():
                    if hasattr(val, k):
                        setattr(val, k, v)
                    else:
                        logger.warning('Attempted to override nonexistent property {} in settings object'.format(val))
            return val
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="automl_settings", argument="automl_settings", actual_type=type(val),
                    expected_types=", ".join(["str", "Dict"]))
            )
