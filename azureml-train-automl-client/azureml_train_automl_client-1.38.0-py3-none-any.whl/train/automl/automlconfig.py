# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Contains configuration for submitting an automated ML experiment in Azure Machine Learning.

Functionality in this module includes methods for defining training features and labels, iteration count and
max time, optimization metrics, compute targets, and algorithms to block.
"""
import inspect
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Union

import math
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import \
    ArgumentBlankOrEmpty, ArgumentMismatch, ArgumentOutOfRange, ComputeNotFound
from azureml.automl.core.shared._diagnostics.automl_error_definitions import \
    AllowedModelsSubsetOfBlockedModels, ComputeNotReady, ConflictingValueForArguments, \
    FeatureUnsupportedForIncompatibleArguments, InputDataWithMixedType, InvalidArgumentType, \
    InvalidArgumentWithSupportedValues, InvalidArgumentWithSupportedValuesForTask, InvalidCVSplits, \
    InvalidInputDatatype, LargeDataAlgorithmsWithUnsupportedArguments, NotSupported, \
    TensorflowAlgosAllowedButDisabled, UnpartitionedData

try:
    from azureml.pipeline.core.pipeline_output_dataset import PipelineOutputTabularDataset

    has_pipeline_pkg = True
except ImportError:
    has_pipeline_pkg = False

from azureml.core import Run
from azureml.core._experiment_method import experiment_method
from azureml.core.compute_target import LocalTarget
from azureml.core.workspace import Workspace
from azureml.core.experiment import Experiment
from azureml.core.runconfig import RunConfiguration
from . import constants
from azureml.automl.core import dataprep_utilities, dataset_utilities, log_server, package_utilities
from azureml.automl.core.config_utilities import _check_validation_config
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.forecasting_parameters import ForecastingParameters
from azureml.automl.core.shared import import_utilities
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.constants import TextDNNLanguages
from .exceptions import ConfigException
from .constants import FeaturizationConfigMode
from azureml._base_sdk_common.tracking import global_tracking_info_registry
from azureml._base_sdk_common.workspace.models import ProvisioningState
from azureml.train.automl._constants_azureml import EnvironmentSettings, MLFlowSettings
from azureml.train.automl._environment_utilities import is_prod, validate_non_prod_env_exists
from azureml.train.automl import _azureautomlsettings
from azureml.train.automl._experiment_drivers.experiment_driver import ExperimentDriver
from azureml.train.automl._azure_experiment_state import AzureExperimentState
from azureml.train.automl._local_managed_utils import is_docker_installed
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.output_dataset_config import OutputTabularDatasetConfig
from azureml.data.constants import DIRECT_MODE
from .constants import Framework

from azureml.automl.core.shared.constants import SupportedInputDatatypes, SupportedModelNames, SupportedModels

logger = logging.getLogger(__name__)


def _automl_static_submit(automl_config_object: 'AutoMLConfig',
                          workspace: Workspace,
                          experiment_name: str,
                          **kwargs: Any) -> Run:
    """
    Start AutoML execution with the given config on the given workspace.

    :param automl_config_object:
    :param workspace:
    :param experiment_name:
    :param kwargs:
    :return:
    """
    experiment = Experiment(workspace, experiment_name)
    show_output = kwargs.get('show_output', False)

    parent_run_id = kwargs.get('_parent_run_id', None)
    run_config = automl_config_object._run_configuration
    compute_target = automl_config_object.user_settings.get('compute_target')

    automl_config_object._validate_config_settings(workspace)
    fit_params = automl_config_object._get_fit_params()

    # retrieve settings which are present in user but not part of fit_params
    settings_dict = {k: v for (k, v) in automl_config_object.user_settings.items() if k not in fit_params}
    settings = _azureautomlsettings.AzureAutoMLSettings(experiment=experiment, **settings_dict)

    with log_server.new_log_context(parent_run_id=parent_run_id):
        automl_run = _start_execution(
            experiment,
            settings,
            fit_params,
            run_config,
            compute_target,
            parent_run_id,
            show_output)

        automl_run.add_properties(global_tracking_info_registry.gather_all(settings.path))

        return automl_run


def _default_execution(experiment: Experiment,
                       settings_obj: _azureautomlsettings.AzureAutoMLSettings,
                       fit_params: Dict[str, Any],
                       legacy_local: bool,
                       show_output: bool = False,
                       parent_run_id: Optional[str] = None) -> Run:
    if parent_run_id:
        fit_params['parent_run_id'] = parent_run_id

    # If legacy local or ADB we need to filter out pipelines which rely on optional packages
    # and are not installed. We can assume managed execution will install optional packages
    # (either through curated envs or _environment_utilities).
    if legacy_local or settings_obj.spark_context:
        settings_obj.apply_optional_package_filter()
    experiment_state = AzureExperimentState(experiment, settings_obj)
    experiment_state.console_writer.show_output = show_output
    driver = ExperimentDriver(experiment_state)
    updated_params = driver.create_parent_run(**fit_params)
    fit_params.update(updated_params)
    return driver.start(**fit_params)


def _start_execution(
        experiment: Experiment,
        settings_obj: _azureautomlsettings.AzureAutoMLSettings,
        fit_params: Dict[str, Any],
        run_config: Optional[RunConfiguration] = None,
        compute_target: Optional[Any] = None,
        parent_run_id: Optional[str] = None,
        show_output: bool = False) -> Run:
    """
    Determine which code path should be used given the user's settings.

    It will start execution and return the parent run for either Local Legacy, Local Managed, Remote Compute, or ADB.

    :param experiment: Experiment to submit the experiment to.
    :param settings_obj: User settings not part of fit params.
    :param fit_params: User settings passed directly to azureautomlclient's fit method.
    :param run_config: The RunConfiguration.
    :param compute_target: The user provided compute target.
    :param parent_run_id: The parent run id if that has been created outside of AutoML.
    :param show_output: Whether to block and show output.
    :return:
    """
    in_process = False
    is_managed = False
    has_docker = is_docker_installed()

    if run_config is None and compute_target is None:
        logger.info("No compute target or run config provided. Running local legacy run.")
        in_process = True
    elif run_config is not None:
        if run_config.target == 'local':
            is_managed = True
            logger.info("Local run configuration provided with docker set to {}. Running local managed run."
                        .format(run_config.docker.use_docker))
        elif compute_target is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments,
                    argument_name="run_config/compute_target",
                    arguments=run_config
                )
            )
    elif isinstance(compute_target, LocalTarget):
        is_managed = True
        # Still create a run configuration for this so that we can leverage the curated environment
        run_config = RunConfiguration()
        run_config.target = compute_target
        run_config.docker.use_docker = has_docker
        logger.info("LocalTarget provided as compute, submitting a local managed run with docker set to {}."
                    .format(str(run_config.docker.use_docker)))
        settings_obj.compute_target = constants.ComputeTargets.LOCAL
    elif compute_target == "local":
        if run_config is None:
            run_config = RunConfiguration()
            run_config.docker.use_docker = has_docker
        logger.info("String local provided as compute, submitting a local managed run with docker set to {}."
                    .format(str(run_config.docker.use_docker)))
        is_managed = True

    if is_managed:
        if not has_docker and settings_obj.enable_local_managed:
            msg = "Docker is not available. Disabling local managed and running in the current process."
            logger.error(msg)
            logging.warning(msg)
        else:
            is_managed = settings_obj.enable_local_managed
            in_process = not is_managed

    fit_params["run_configuration"] = run_config

    if settings_obj.spark_context is not None:
        logger.info("Running on spark.")
        print("Submitting spark run.")
        _disable_mlflow(settings_obj)
        automl_run = _default_execution(experiment, settings_obj, fit_params, False, show_output)
    elif in_process is True:
        logger.info("Submitting local legacy run.")
        _disable_mlflow(settings_obj)
        if not settings_obj._ignore_package_version_incompatibilities:
            package_utilities._get_package_incompatibilities(
                packages=package_utilities.AUTOML_PACKAGES,
                ignored_dependencies=package_utilities._PACKAGES_TO_IGNORE_VERSIONS
            )
        automl_run = _default_execution(experiment, settings_obj, fit_params, True, show_output, parent_run_id)
    elif is_managed:
        logger.info("Submitting local managed run.")
        print("Submitting local conda or docker run.")
        automl_run = _default_execution(experiment, settings_obj, fit_params, False, show_output)
    else:
        logger.info("Submitting remote.")
        print("Submitting remote run.")
        if settings_obj.scenario == constants.Scenarios._NON_PROD:
            validate_non_prod_env_exists(experiment.workspace)
        automl_run = _default_execution(experiment, settings_obj, fit_params, False, show_output)

    return automl_run


def _disable_mlflow(automl_settings: _azureautomlsettings.AzureAutoMLSettings) -> None:
    if automl_settings.save_mlflow:
        msg = "save_mlflow is only supported for remote runs. Disabling mlflow for this run."
        logging.warning(msg)
        logger.warning(msg)
        automl_settings.save_mlflow = False


class AutoMLConfig(object):
    """
    Represents configuration for submitting an automated ML experiment in Azure Machine Learning.

    This configuration object contains and persists the parameters for configuring the experiment run,
    as well as the training data to be used at run time. For guidance on selecting your
    settings, see https://aka.ms/AutoMLConfig.

    .. remarks::

        The following code shows a basic example of creating an AutoMLConfig object and submitting an
        experiment for regression:

        .. code-block:: python

            automl_settings = {
                "n_cross_validations": 3,
                "primary_metric": 'r2_score',
                "enable_early_stopping": True,
                "experiment_timeout_hours": 1.0,
                "max_concurrent_iterations": 4,
                "max_cores_per_iteration": -1,
                "verbosity": logging.INFO,
            }

            automl_config = AutoMLConfig(task = 'regression',
                                        compute_target = compute_target,
                                        training_data = train_data,
                                        label_column_name = label,
                                        **automl_settings
                                        )

            ws = Workspace.from_config()
            experiment = Experiment(ws, "your-experiment-name")
            run = experiment.submit(automl_config, show_output=True)

        A full sample is available at `Regression <https://github.com/Azure/MachineLearningNotebooks/
        blob/master/how-to-use-azureml/automated-machine-learning/regression/auto-ml-regression.ipynb>`_

        Examples of using AutoMLConfig for forecasting are in these notebooks:

        * `Orange Juice Sales Forecasting <https://github.com/Azure/MachineLearningNotebooks/blob/master/
          how-to-use-azureml/automated-machine-learning/forecasting-orange-juice-sales/
          auto-ml-forecasting-orange-juice-sales.ipynb>`_
        * `Forecasting using the Energy Demand Dataset <https://github.com/Azure/MachineLearningNotebooks/blob/master/
          how-to-use-azureml/automated-machine-learning/forecasting-energy-demand/
          auto-ml-forecasting-energy-demand.ipynb>`_
        * `BikeShare Demand Forecasting <https://github.com/Azure/MachineLearningNotebooks/blob/master/
          how-to-use-azureml/automated-machine-learning/forecasting-bike-share/auto-ml-forecasting-bike-share.ipynb>`_

        Examples of using AutoMLConfig for all task types can be found in these `automated ML notebooks
        <https://github.com/Azure/MachineLearningNotebooks/tree/master/
        how-to-use-azureml/automated-machine-learning>`_.

        For background on automated ML, see the articles:

        * `How to define a machine learning task <https://docs.microsoft.com/azure/machine-learning/
          how-to-define-task-type>`_
        * `Configure automated ML experiments in Python <https://docs.microsoft.com/azure/machine-learning/
          how-to-configure-auto-train>`_. In this article, there is information about the different algorithms
          and primary metrics used for each task type.
        * `Auto-train a time-series forecast model <https://docs.microsoft.com/azure/machine-learning/
          how-to-auto-train-forecast>`_. In this article, there is information about which constructor
          parameters and ``**kwargs`` are used in forecasting.

        For more information about different options for configuring training/validation data splits and
        cross-validation for your automated machine learning, AutoML, experiments, see
        `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
        /azure/machine-learning/how-to-configure-cross-validation-data-splits>`_.

    :param task:
        The type of task to run. Values can be 'classification', 'regression', or 'forecasting'
        depending on the type of automated ML problem to solve.
    :type task: str or azureml.train.automl.constants.Tasks
    :param path:
        The full path to the Azure Machine Learning project folder. If not specified, the default is
        to use the current directory or ".".
    :type path: str
    :param iterations:
        The total number of different algorithm and parameter combinations
        to test during an automated ML experiment. If not specified, the default is 1000 iterations.
    :type iterations: int
    :param primary_metric:
        The metric that Automated Machine Learning will optimize for model selection.
        Automated Machine Learning collects more metrics than it can optimize.
        You can use :meth:`azureml.train.automl.utilities.get_primary_metrics` to get a list of
        valid metrics for your given task. For more information on how metrics are calculated, see
        https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

        If not specified, accuracy is used for classification tasks, normalized root mean squared is
        used for forecasting and regression tasks, accuracy is used for image classification and
        image multi label classification, and mean average precision is used for image object
        detection.
    :type primary_metric: str or azureml.automl.core.shared.constants.Metric
    :param positive_label:
        The positive class label that Automated Machine Learning will use to calculate binary metrics with.
        Binary metrics are calculated in two conditions for classification tasks:
        1. label column consists of two classes indicating binary classification task
        AutoML will use specified positive class when `positive_label` is passed in,
        otherwise AutoML will pick a positive class based on label encoded value.
        2. multi class classification task with `positive_label` specified

        For more information on classification, checkout
        `metrics for classification scenarios <https://docs.microsoft.com
        /azure/machine-learning/how-to-configure-auto-train#metrics-for-classification-scenarios>`_.
    :type positive_label: Any
    :param compute_target:
        The Azure Machine Learning compute target to run the Automated Machine Learning experiment on.
        See https://docs.microsoft.com/en-us/azure/machine-learning/concept-automated-ml#local-remote for more
        information on compute targets.
    :type compute_target: azureml.core.compute_target.AbstractComputeTarget
    :param spark_context:
        The Spark context. Only applicable when used inside Azure Databricks/Spark environment.
    :type spark_context: SparkContext
    :param X:
        The training features to use when fitting pipelines during an experiment. This setting is being
        deprecated. Please use training_data and label_column_name instead.
    :type X: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset or azureml.data.TabularDataset
    :param y:
        The training labels to use when fitting pipelines during an experiment.
        This is the value your model will predict. This setting is being deprecated.
        Please use training_data and label_column_name instead.
    :type y: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset or azureml.data.TabularDataset
    :param sample_weight:
        The weight to give to each training sample when running fitting pipelines,
        each row should correspond to a row in X and y data.

        Specify this parameter when specifying ``X``.
        This setting is being deprecated. Please use training_data and weight_column_name instead.
    :type sample_weight: pandas.DataFrame or numpy.ndarray
        or azureml.data.TabularDataset
    :param X_valid:
        Validation features to use when fitting pipelines during an experiment.

        If specified, then ``y_valid`` or ``sample_weight_valid`` must also be specified.
        This setting is being deprecated. Please use validation_data and label_column_name instead.
    :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset or azureml.data.TabularDataset
    :param y_valid:
        Validation labels to use when fitting pipelines during an experiment.

        Both ``X_valid`` and ``y_valid`` must be specified together.
        This setting is being deprecated. Please use validation_data and label_column_name instead.
    :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset or azureml.data.TabularDataset
    :param sample_weight_valid:
        The weight to give to each validation sample when running scoring pipelines,
        each row should correspond to a row in X and y data.

        Specify this parameter when specifying ``X_valid``.
        This setting is being deprecated. Please use validation_data and weight_column_name instead.
    :type sample_weight_valid: pandas.DataFrame or numpy.ndarray
        or azureml.data.TabularDataset
    :param cv_splits_indices:
        Indices where to split training data for cross validation.
        Each row is a separate cross fold and within each crossfold, provide 2 numpy arrays,
        the first with the indices for samples to use for training data and the second with the indices to
        use for validation data. i.e., [[t1, v1], [t2, v2], ...] where t1 is the training indices for the first
        cross fold and v1 is the validation indices for the first cross fold.

        To specify existing data as validation data, use ``validation_data``. To let AutoML extract validation
        data out of training data instead, specify either ``n_cross_validations`` or ``validation_size``.
        Use ``cv_split_column_names`` if you have cross validation column(s) in ``training_data``.
    :type cv_splits_indices: List[List[numpy.ndarray]]
    :param validation_size:
        What fraction of the data to hold out for validation when user validation data
        is not specified. This should be between 0.0 and 1.0 non-inclusive.

        Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
        ``validation_size`` to extract validation data out of the specified training data.
        For custom cross validation fold, use ``cv_split_column_names``.

        For more information, see
        `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
        /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
    :type validation_size: float
    :param n_cross_validations:
        How many cross validations to perform when user validation data is not specified.

        Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
        ``validation_size`` to extract validation data out of the specified training data.
        For custom cross validation fold, use ``cv_split_column_names``.

        For more information, see
        `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
        /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
    :type n_cross_validations: int
    :param y_min:
        Minimum value of y for a regression experiment. The combination of ``y_min`` and ``y_max`` are used to
        normalize test set metrics based on the input data range. This setting is being deprecated. Instead, this
        value will be computed from the data.
    :type y_min: float
    :param y_max:
        Maximum value of y for a regression experiment. The combination of ``y_min`` and ``y_max`` are used to
        normalize test set metrics based on the input data range. This setting is being deprecated. Instead, this
        value will be computed from the data.
    :type y_max: float
    :param num_classes:
        The number of classes in the label data for a classification experiment. This setting is being deprecated.
        Instead, this value will be computed from the data.
    :type num_classes: int
    :param featurization:
        'auto' / 'off' / FeaturizationConfig
        Indicator for whether featurization step should be done automatically or not,
        or whether customized featurization should be used.
        Note: If the input data is sparse, featurization cannot be turned on.

        Column type is automatically detected. Based on the detected column type
        preprocessing/featurization is done as follows:

        * Categorical: Target encoding, one hot encoding, drop high cardinality categories, impute missing values.
        * Numeric: Impute missing values, cluster distance, weight of evidence.
        * DateTime: Several features such as day, seconds, minutes, hours etc.
        * Text: Bag of words, pre-trained Word embedding, text target encoding.

        More details can be found in the article `Configure automated ML experiments in
        Python <https://docs.microsoft.com/azure/machine-learning/
        how-to-configure-auto-train#data-featurization>`__.

        To customize featurization step, provide a FeaturizationConfig object.
        Customized featurization currently supports blocking a set of transformers, updating column purpose,
        editing transformer parameters, and dropping columns. For more information, see `Customize feature
        engineering <https://docs.microsoft.com/azure/machine-learning/
        how-to-configure-auto-train#customize-feature-engineering>`_.

        Note: Timeseries features are handled separately when the task type is set to forecasting independent
        of this parameter.
    :type featurization: str or azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig
    :param max_cores_per_iteration:
        The maximum number of threads to use for a given training iteration.
        Acceptable values:

        * Greater than 1 and less than or equal to the maximum number of cores on the compute target.

        * Equal to -1, which means to use all the possible cores per iteration per child-run.

        * Equal to 1, the default.
    :type max_cores_per_iteration: int
    :param max_concurrent_iterations:
        Represents the maximum number of iterations that would be executed in parallel. The default value
        is 1.

        * AmlCompute clusters support one interation running per node.
          For multiple AutoML experiment parent runs executed in parallel on a single AmlCompute cluster, the
          sum of the ``max_concurrent_iterations`` values for all experiments should be less
          than or equal to the maximum number of nodes. Otherwise, runs will be queued until nodes are available.

        * DSVM supports multiple iterations per node. ``max_concurrent_iterations`` should
          be less than or equal to the number of cores on the DSVM. For multiple experiments
          run in parallel on a single DSVM, the sum of the ``max_concurrent_iterations`` values for all
          experiments should be less than or equal to the maximum number of nodes.

        * Databricks - ``max_concurrent_iterations`` should be less than or equal to the number of
          worker nodes on Databricks.

        ``max_concurrent_iterations`` does not apply to local runs. Formerly, this parameter
        was named ``concurrent_iterations``.
    :type max_concurrent_iterations: int
    :param iteration_timeout_minutes:
        Maximum time in minutes that each iteration can run for before it terminates.
        If not specified, a value of 1 month or 43200 minutes is used.
    :type iteration_timeout_minutes: int
    :param mem_in_mb:
        Maximum memory usage that each iteration can run for before it terminates.
        If not specified, a value of 1 PB or 1073741824 MB is used.
    :type mem_in_mb: int
    :param enforce_time_on_windows:
        Whether to enforce a time limit on model training at each iteration on Windows. The default is True.
        If running from a Python script file (.py), see the documentation for allowing resource limits
        on Windows.
    :type enforce_time_on_windows: bool
    :param experiment_timeout_hours:
        Maximum amount of time in hours that all iterations combined can take before the
        experiment terminates. Can be a decimal value like 0.25 representing 15 minutes. If not
        specified, the default experiment timeout is 6 days. To specify a timeout
        less than or equal to 1 hour, make sure your dataset's size is not greater than
        10,000,000 (rows times column) or an error results.
    :type experiment_timeout_hours: float
    :param experiment_exit_score:
        Target score for experiment. The experiment terminates after this score is reached.
        If not specified (no criteria), the experiment runs until no further progress is made
        on the primary metric. For for more information on exit criteria, see this `article
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#exit-criteria>`_.
    :type experiment_exit_score: float
    :param enable_early_stopping:
        Whether to enable early termination if the score is not improving in the short term.
        The default is True.

        Early stopping logic:

        * No early stopping for first 20 iterations (landmarks).

        * Early stopping window starts on the 21st iteration and looks for early_stopping_n_iters iterations
            (currently set to 10). This means that the first iteration where stopping can occur is
            the 31st.

        * AutoML still schedules 2 ensemble iterations AFTER early stopping, which might result in
            higher scores.

        * Early stopping is triggered if the absolute value of best score calculated is the same for past
            early_stopping_n_iters iterations, that is, if there is no improvement in score for
            early_stopping_n_iters iterations.
    :type enable_early_stopping: bool
    :param blocked_models:
        A list of algorithms to ignore for an experiment. If ``enable_tf`` is False, TensorFlow models
        are included in ``blocked_models``.
    :type blocked_models: list(str)
        or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
        or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
        or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
    :param blacklist_models:
        Deprecated parameter, use blocked_models instead.
    :type blacklist_models: list(str)
        or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
        or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
        or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
    :param exclude_nan_labels:
        Whether to exclude rows with NaN values in the label. The default is True.
    :type exclude_nan_labels: bool
    :param verbosity:
        The verbosity level for writing to the log file. The default is INFO or 20.
        Acceptable values are defined in the Python `logging
        library <https://docs.python.org/3/library/logging.html>`_.
    :type verbosity: int
    :param enable_tf:
        Deprecated parameter to enable/disable Tensorflow algorithms. The default is False.
    :type enable_tf: bool
    :param model_explainability:
        Whether to enable explaining the best AutoML model at the end of all AutoML training iterations.
        The default is True. For more information, see
        `Interpretability: model explanations in automated machine learning
        <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`_.
    :type model_explainability: bool
    :param allowed_models:
        A list of model names to search for an experiment. If not specified, then all models supported
        for the task are used minus any specified in ``blocked_models`` or deprecated TensorFlow models.
        The supported models for each task type are described in the
        :class:`azureml.train.automl.constants.SupportedModels` class.
    :type allowed_models: list(str)
        or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
        or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
        or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
    :param whitelist_models:
        Deprecated parameter, use allowed_models instead.
    :type whitelist_models: list(str)
        or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
        or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
        or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
    :param enable_onnx_compatible_models:
        Whether to enable or disable enforcing the ONNX-compatible models. The default is False.
        For more information about Open Neural Network Exchange (ONNX) and Azure Machine Learning,
        see this `article <https://docs.microsoft.com/azure/machine-learning/concept-onnx>`__.
    :type enable_onnx_compatible_models: bool
    :param forecasting_parameters: A ForecastingParameters object to hold all the forecasting specific parameters.
    :type forecasting_parameters: azureml.automl.core.forecasting_parameters.ForecastingParameters
    :param time_column_name:
        The name of the time column. This parameter is required when forecasting to specify the datetime
        column in the input data used for building the time series and inferring its frequency.
        This setting is being deprecated. Please use forecasting_parameters instead.
    :type time_column_name: str
    :param max_horizon:
        The desired maximum forecast horizon in units of time-series frequency. The default value is 1.

        Units are based on the time interval of your training data, e.g., monthly, weekly that the forecaster
        should predict out. When task type is forecasting, this parameter is required. For more information on
        setting forecasting parameters, see `Auto-train a time-series forecast model <https://docs.microsoft.com/
        azure/machine-learning/how-to-auto-train-forecast>`_. This setting is being deprecated. Please use
        forecasting_parameters instead.
    :type max_horizon: int
    :param grain_column_names:
        The names of columns used to group a timeseries.
        It can be used to create multiple series. If grain is not defined, the data set is assumed
        to be one time-series. This parameter is used with task type forecasting.
        This setting is being deprecated. Please use forecasting_parameters instead.
    :type grain_column_names: str or list(str)
    :param target_lags:
        The number of past periods to lag from the target column. The default is 1. This setting is being deprecated.
        Please use forecasting_parameters instead.

        When forecasting, this parameter represents the number of rows to lag the target values based
        on the frequency of the data. This is represented as a list or single integer. Lag should be used
        when the relationship between the independent variables and dependant variable do not match up or
        correlate by default. For example, when trying to forecast demand for a product, the demand in any
        month may depend on the price of specific commodities 3 months prior. In this example, you may want
        to lag the target (demand) negatively by 3 months so that the model is training on the correct
        relationship. For more information, see `Auto-train a time-series forecast model
        <https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-forecast>`_.
    :type target_lags: int or list(int)
    :param feature_lags: Flag for generating lags for the numeric features. This setting is being deprecated.
        Please use forecasting_parameters instead.
    :type feature_lags: str
    :param target_rolling_window_size:
        The number of past periods used to create a rolling window average of the target column.
        This setting is being deprecated. Please use forecasting_parameters instead.

        When forecasting, this parameter represents `n` historical periods to use to generate forecasted values,
        <= training set size. If omitted, `n` is the full training set size. Specify this parameter
        when you only want to consider a certain amount of history when training the model.
    :type target_rolling_window_size: int
    :param country_or_region:
        The country/region used to generate holiday features.
        These should be ISO 3166 two-letter country/region code, for example 'US' or 'GB'.
        This setting is being deprecated. Please use forecasting_parameters instead.
    :type country_or_region: str
    :param use_stl: Configure STL Decomposition of the time-series target column.
                    use_stl can take three values: None (default) - no stl decomposition, 'season' - only generate
                    season component and season_trend - generate both season and trend components.
                    This setting is being deprecated. Please use forecasting_parameters instead.
    :type use_stl: str
    :param seasonality: Set time series seasonality. If seasonality is set to 'auto', it will be inferred.
                This setting is being deprecated. Please use forecasting_parameters instead.
    :type seasonality: int or str
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
    :param enable_voting_ensemble:
        Whether to enable/disable VotingEnsemble iteration. The default is True.
        For more information about ensembles, see `Ensemble configuration
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`_.
    :type enable_voting_ensemble: bool
    :param enable_stack_ensemble:
        Whether to enable/disable StackEnsemble iteration. The default is None.
        If `enable_onnx_compatible_models` flag is being set, then StackEnsemble iteration will be disabled.
        Similarly, for Timeseries tasks, StackEnsemble iteration will be disabled by default, to avoid risks of
        overfitting due to small training set used in fitting the meta learner.
        For more information about ensembles, see `Ensemble configuration
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`_.
    :type enable_stack_ensemble: bool
    :param debug_log:
        The log file to write debug information to. If not specified, 'automl.log' is used.
    :type debug_log: str
    :param training_data:
        The training data to be used within the experiment.
        It should contain both training features and a label column (optionally a sample weights column).
        If ``training_data`` is specified, then the ``label_column_name`` parameter must also be specified.

        ``training_data`` was introduced in version 1.0.81.
    :type training_data: pandas.DataFrame or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param validation_data:
        The validation data to be used within the experiment.
        It should contain both training features and label column (optionally a sample weights column).
        If ``validation_data`` is specified, then ``training_data`` and ``label_column_name`` parameters must
        be specified.

        ``validation_data`` was introduced in version 1.0.81. For more information, see
        `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
        /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
    :type validation_data: pandas.DataFrame or azureml.core.Dataset
        or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
    :param test_data:
        The Model Test feature using test datasets or test data splits is a feature in
        Preview state and might change at any time.
        The test data to be used for a test run that will automatically be started after
        model training is complete. The test run will get predictions using the best model
        and will compute metrics given these predictions.

        If this parameter or the ``test_size`` parameter are not specified then
        no test run will be executed automatically after model training is completed.
        Test data should contain both features and label column.
        If ``test_data`` is specified then the ``label_column_name`` parameter must be specified.
    :type test_data: azureml.core.Dataset or azureml.data.TabularDataset
    :param test_size:
        The Model Test feature using test datasets or test data splits is a feature in
        Preview state and might change at any time.
        What fraction of the training data to hold out for test data for a test run that will
        automatically be started after model training is complete. The test run will get
        predictions using the best model and will compute metrics given these predictions.

        This should be between 0.0 and 1.0 non-inclusive.
        If ``test_size`` is specified at the same time as ``validation_size``,
        then the test data is split from ``training_data`` before the validation data is split.
        For example, if ``validation_size=0.1``, ``test_size=0.1`` and the original training data has 1000 rows,
        then the test data will have 100 rows, the validation data will contain 90 rows
        and the training data will have 810 rows.

        For regression based tasks, random sampling is used. For classification
        tasks, stratified sampling is used. Forecasting does not currently
        support specifying a test dataset using a train/test split.

        If this parameter or the ``test_data`` parameter are not specified then
        no test run will be executed automatically after model training is completed.
    :type test_size: float
    :param label_column_name:
        The name of the label column. If the input data is from a pandas.DataFrame which doesn't
        have column names, column indices can be used instead, expressed as integers.

        This parameter is applicable to ``training_data``, ``validation_data`` and ``test_data`` parameters.
        ``label_column_name`` was introduced in version 1.0.81.
    :type label_column_name: typing.Union[str, int]
    :param weight_column_name:
        The name of the sample weight column. Automated ML supports a weighted column
        as an input, causing rows in the data to be weighted up or down.
        If the input data is from a pandas.DataFrame which doesn't have column names,
        column indices can be used instead, expressed as integers.

        This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
        ``weight_column_names`` was introduced in version 1.0.81.
    :type weight_column_name: typing.Union[str, int]
    :param cv_split_column_names:
        List of names of the columns that contain custom cross validation split.
        Each of the CV split columns represents one CV split where each row are either marked
        1 for training or 0 for validation.

        This parameter is applicable to ``training_data`` parameter for custom cross validation purposes.
        ``cv_split_column_names`` was introduced in version 1.6.0

        Use either ``cv_split_column_names`` or ``cv_splits_indices``.

        For more information, see
        `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
        /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
    :type cv_split_column_names: list(str)
    :param enable_local_managed: Disabled parameter. Local managed runs can not be enabled at this time.
    :type enable_local_managed: bool
    :param enable_dnn: Whether to include DNN based models during model selection. The default is False.
    :type enable_dnn: bool
    :raises azureml.train.automl.exceptions.ConfigException: Raised for problems with configuration.
        Each exception message describes the problem.
    :raises azureml.automl.core.shared.exceptions.ConfigException: Raised for configuration parameters that
        should be specified and were missing. Each exception message describes the problem.
    """

    @experiment_method(submit_function=_automl_static_submit)
    def __init__(self,
                 task: str,
                 path: Optional[str] = None,
                 iterations: Optional[int] = None,
                 primary_metric: Optional[str] = None,
                 positive_label: Optional[Any] = None,
                 compute_target: Optional[Any] = None,
                 spark_context: Optional[Any] = None,
                 X: Optional[Any] = None,
                 y: Optional[Any] = None,
                 sample_weight: Optional[Any] = None,
                 X_valid: Optional[Any] = None,
                 y_valid: Optional[Any] = None,
                 sample_weight_valid: Optional[Any] = None,
                 cv_splits_indices: Optional[List[List[Any]]] = None,
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
                 enforce_time_on_windows: bool = os.name == 'nt',
                 experiment_timeout_hours: Optional[float] = None,
                 experiment_exit_score: Optional[float] = None,
                 enable_early_stopping: bool = True,
                 blocked_models: Optional[List[str]] = None,
                 blacklist_models: Optional[List[str]] = None,
                 exclude_nan_labels: bool = True,
                 verbosity: int = logging.INFO,
                 enable_tf: bool = False,
                 model_explainability: bool = True,
                 allowed_models: Optional[List[str]] = None,
                 whitelist_models: Optional[List[str]] = None,
                 enable_onnx_compatible_models: bool = False,
                 enable_voting_ensemble: bool = True,
                 enable_stack_ensemble: Optional[bool] = None,
                 debug_log: str = 'automl.log',
                 training_data: Optional[Any] = None,
                 validation_data: Optional[Any] = None,
                 test_data: Optional[Any] = None,
                 test_size: Optional[float] = None,
                 label_column_name: Optional[str] = None,
                 weight_column_name: Optional[str] = None,
                 cv_split_column_names: Optional[List[str]] = None,
                 enable_local_managed: bool = False,
                 enable_dnn: bool = False,
                 forecasting_parameters: Optional[ForecastingParameters] = None,
                 **kwargs: Any) -> None:
        """
        Create an AutoMLConfig.

        :param task:
            The type of task to run. Values can be 'classification', 'regression', or 'forecasting'
            depending on the type of automated ML problem to solve.
        :type task: str or azureml.train.automl.constants.Tasks
        :param path:
            The full path to the Azure Machine Learning project folder. If not specified, the default is
            to use the current directory or ".".
        :type path: str
        :param iterations:
            The total number of different algorithm and parameter combinations
            to test during an automated ML experiment. If not specified, the default is 1000 iterations.
        :type iterations: int
        :param primary_metric:
            The metric that Automated Machine Learning will optimize for model selection.
            Automated Machine Learning collects more metrics than it can optimize.
            You can use :meth:`azureml.train.automl.utilities.get_primary_metrics` to get a list of
            valid metrics for your given task. For more information on how metrics are calculated, see
            https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#primary-metric.

            If not specified, accuracy is used for classification tasks, normalized root mean squared is
            used for forecasting and regression tasks, accuracy is used for image classification and
            image multi label classification, and mean average precision is used for image object
            detection.
        :type primary_metric: str or azureml.automl.core.shared.constants.Metric
        :param positive_label:
            The positive class label that Automated Machine Learning will use to calculate binary metrics with.
            Binary metrics are calculated in two conditions for classification tasks:
            1. label column consists of two classes indicating binary classification task
            AutoML will use specified positive class when `positive_label` is passed in,
            otherwise AutoML will pick a positive class based on label encoded value.
            2. multi class classification task with `positive_label` specified

            For more information on classification, checkout
            `metrics for classification scenarios <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-auto-train#metrics-for-classification-scenarios>`_.
        :type positive_label: Any
        :param compute_target:
            The Azure Machine Learning compute target to run the
            Automated Machine Learning experiment on.
            See https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-remote for more
            information on compute targets.
        :type compute_target: azureml.core.compute_target.AbstractComputeTarget
        :param spark_context:
            The Spark context. Only applicable when used inside Azure Databricks/Spark environment.
        :type spark_context: SparkContext
        :param X:
            The training features to use when fitting pipelines during an experiment. This setting is being
            deprecated. Please use training_data and label_column_name instead.
        :type X: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param y:
            The training labels to use when fitting pipelines during an experiment.
            This is the value your model will predict. This setting is being deprecated.
            Please use training_data and label_column_name instead.
        :type y: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param sample_weight:
            The weight to give to each training sample when running fitting pipelines,
            each row should correspond to a row in X and y data.

            Specify this parameter when specifying ``X``.
            This setting is being deprecated. Please use training_data and weight_column_name instead.
        :type sample_weight: pandas.DataFrame or numpy.ndarray
            or azureml.data.TabularDataset
        :param X_valid:
            Validation features to use when fitting pipelines during an experiment.

            If specified, then ``y_valid`` or ``sample_weight_valid`` must also be specified.
            This setting is being deprecated. Please use validation_data and label_column_name instead.
        :type X_valid: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param y_valid:
            Validation labels to use when fitting pipelines during an experiment.

            Both ``X_valid`` and ``y_valid`` must be specified together.
            This setting is being deprecated. Please use validation_data and label_column_name instead.
        :type y_valid: pandas.DataFrame or numpy.ndarray or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param sample_weight_valid:
            The weight to give to each validation sample when running scoring pipelines,
            each row should correspond to a row in X and y data.

            Specify this parameter when specifying ``X_valid``.
            This setting is being deprecated. Please use validation_data and weight_column_name instead.
        :type sample_weight_valid: pandas.DataFrame or numpy.ndarray
            or azureml.data.TabularDataset
        :param cv_splits_indices:
            Indices where to split training data for cross validation.
            Each row is a separate cross fold and within each crossfold, provide 2 numpy arrays,
            the first with the indices for samples to use for training data and the second with the indices to
            use for validation data. i.e., [[t1, v1], [t2, v2], ...] where t1 is the training indices for the first
            cross fold and v1 is the validation indices for the first cross fold.
            This option is supported when data is passed as separate Features dataset and Label column.

            To specify existing data as validation data, use ``validation_data``. To let AutoML extract validation
            data out of training data instead, specify either ``n_cross_validations`` or ``validation_size``.
            Use ``cv_split_column_names`` if you have cross validation column(s) in ``training_data``.
        :type cv_splits_indices: List[List[numpy.ndarray]]
        :param validation_size:
            What fraction of the data to hold out for validation when user validation data
            is not specified. This should be between 0.0 and 1.0 non-inclusive.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
        :type validation_size: float
        :param n_cross_validations:
            How many cross validations to perform when user validation data is not specified.

            Specify ``validation_data`` to provide validation data, otherwise set ``n_cross_validations`` or
            ``validation_size`` to extract validation data out of the specified training data.
            For custom cross validation fold, use ``cv_split_column_names``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
        :type n_cross_validations: int
        :param y_min:
            Minimum value of y for a regression experiment. The combination of ``y_min`` and ``y_max`` are used to
            normalize test set metrics based on the input data range. This setting is being deprecated. Instead, this
            value will be computed from the data.
        :type y_min: float
        :param y_max:
            Maximum value of y for a regression experiment. The combination of ``y_min`` and ``y_max`` are used to
            normalize test set metrics based on the input data range. This setting is being deprecated. Instead, this
            value will be computed from the data.
        :type y_max: float
        :param num_classes:
            The number of classes in the label data for a classification experiment. This setting is being deprecated.
            Instead, this value will be computed from the data.
        :type num_classes: int
        :param featurization:
            'auto' / 'off' / FeaturizationConfig
            Indicator for whether featurization step should be done automatically or not,
            or whether customized featurization should be used.
            Note: If the input data is sparse, featurization cannot be turned on.

            Column type is automatically detected. Based on the detected column type
            preprocessing/featurization is done as follows:

            * Categorical: Target encoding, one hot encoding, drop high cardinality categories, impute missing values.
            * Numeric: Impute missing values, cluster distance, weight of evidence.
            * DateTime: Several features such as day, seconds, minutes, hours etc.
            * Text: Bag of words, pre-trained Word embedding, text target encoding.

            More details can be found in the article `Configure automated ML experiments in
            Python <https://docs.microsoft.com/azure/machine-learning/
            how-to-configure-auto-train#data-featurization>`__.

            To customize featurization step, provide a FeaturizationConfig object.
            Customized featurization currently supports blocking a set of transformers, updating column purpose,
            editing transformer parameters, and dropping columns. For more information, see `Customize feature
            engineering <https://docs.microsoft.com/azure/machine-learning/
            how-to-configure-auto-train#customize-feature-engineering>`_.

            Note: Timeseries features are handled separately when the task type is set to forecasting independent
            of this parameter.
        :type featurization: str or azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig
        :param max_cores_per_iteration:
            The maximum number of threads to use for a given training iteration.
            Acceptable values:

            * Greater than 1 and less than or equal to the maximum number of cores on the compute target.

            * Equal to -1, which means to use all the possible cores per iteration per child-run.

            * Equal to 1, the default value.
        :type max_cores_per_iteration: int
        :param max_concurrent_iterations:
            Represents the maximum number of iterations that would be executed in parallel. The default value
            is 1.

            * AmlCompute clusters support one interation running per node.
              For multiple experiments run in parallel on a single AmlCompute cluster, the
              sum of the ``max_concurrent_iterations`` values for all experiments should be less
              than or equal to the maximum number of nodes.

            * DSVM supports multiple iterations per node. ``max_concurrent_iterations`` should
              be less than or equal to the number of cores on the DSVM. For multiple experiments
              run in parallel on a single DSVM, the sum of the ``max_concurrent_iterations`` values for all
              experiments should be less than or equal to the maximum number of nodes.

            * Databricks - ``max_concurrent_iterations`` should be less than or equal to the number of
              worker nodes on Databricks.

            ``max_concurrent_iterations`` does not apply to local runs. Formerly, this parameter
            was named ``concurrent_iterations``.
        :type max_concurrent_iterations: int
        :param iteration_timeout_minutes:
            Maximum time in minutes that each iteration can run for before it terminates.
            If not specified, a value of 1 month or 43200 minutes is used.
        :type iteration_timeout_minutes: int
        :param mem_in_mb:
            Maximum memory usage that each iteration can run for before it terminates.
            If not specified, a value of 1 PB or 1073741824 MB is used.
        :type mem_in_mb: int
        :param enforce_time_on_windows:
            Whether to enforce a time limit on model training at each iteration on Windows. The default is True.
            If running from a Python script file (.py), see the documentation for allowing resource limits
            on Windows.
        :type enforce_time_on_windows: bool
        :param experiment_timeout_hours:
            Maximum amount of time in hours that all iterations combined can take before the
            experiment terminates. Can be a decimal value like 0.25 representing 15 minutes. If not
            specified, the default experiment timeout is 6 days. To specify a timeout
            less than or equal to 1 hour, make sure your dataset's size is not greater than
            10,000,000 (rows times column) or an error results.
        :type experiment_timeout_hours: float
        :param experiment_exit_score:
            Target score for experiment. The experiment terminates after this score is reached.
            If not specified (no criteria), the experiment runs until no further progress is made
            on the primary metric. For for more information on exit criteria, see this `article
            `<https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#exit-criteria>`_.
        :type experiment_exit_score: float
        :param enable_early_stopping:
            Whether to enable early termination if the score is not improving in the short term.
            The default is True.

            Early stopping logic:

            * No early stopping for first 20 iterations (landmarks).

            * Early stopping window starts on the 21st iteration and looks for early_stopping_n_iters iterations
              (currently set to 10). This means that the first iteration where stopping can occur is
              the 31st.

            * AutoML still schedules 2 ensemble iterations AFTER early stopping, which might result in
              higher scores.

            * Early stopping is triggered if the absolute value of best score calculated is the same for past
              early_stopping_n_iters iterations, that is, if there is no improvement in score for
              early_stopping_n_iters iterations.
        :type enable_early_stopping: bool
        :param blocked_models:
            A list of algorithms to ignore for an experiment. If ``enable_tf`` is False, TensorFlow models
            are included in ``blocked_models``.
        :type blocked_models: list(str)
            or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
            or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
            or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
        :param blacklist_models:
            Deprecated parameter, use blocked_models instead.
        :type blacklist_models: list(str)
            or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
            or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
            or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
        :param exclude_nan_labels:
            Whether to exclude rows with NaN values in the label. The default is True.
        :type exclude_nan_labels: bool
        :param verbosity:
            The verbosity level for writing to the log file. The default is INFO or 20.
            Acceptable values are defined in the Python `logging
            library <https://docs.python.org/3/library/logging.html>`_.
        :type verbosity: int
        :param enable_tf:
            Whether to enable/disable TensorFlow algorithms. The default is False.
        :type enable_tf: bool
        :param model_explainability:
            Whether to enable explaining the best AutoML model at the end of all AutoML training iterations.
            The default is True. For more information, see
            `Interpretability: model explanations in automated machine learning
            <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`_.
        :type model_explainability: bool
        :param allowed_models:
            A list of model names to search for an experiment. If not specified, then all models supported
            for the task are used minus any specified in ``blocked_models`` or deprecated TensorFlow models.
            The supported models for each task type are described in the
            :class:`azureml.train.automl.constants.SupportedModels` class.
        :type allowed_models: list(str)
            or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
            or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
            or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
        :param allowed_models:
            A list of model names to search for an experiment. If not specified, then all models supported
            for the task are used minus any specified in ``blocked_models`` or deprecated TensorFlow models.
            The supported models for each task type are described in the
            :class:`azureml.train.automl.constants.SupportedModels` class.
        :type allowed_models: list(str)
            or list(azureml.train.automl.constants.SupportedModels.Classification) for classification task,
            or list(azureml.train.automl.constants.SupportedModels.Regression) for regression task,
            or list(azureml.train.automl.constants.SupportedModels.Forecasting) for forecasting task
        :param whitelist_models:
            Deprecated parameter, use allowed_models instead.
        :param enable_onnx_compatible_models:
            Whether to enable or disable enforcing the ONNX-compatible models. The default is False.
            For more information about Open Neural Network Exchange (ONNX) and Azure Machine Learning,
            see this `article <https://docs.microsoft.com/azure/machine-learning/concept-onnx>`__.
        :type enable_onnx_compatible_models: bool
        :param forecasting_parameters: An object to hold all the forecasting specific parameters.
        :type forecasting_parameters: azureml.automl.core.forecasting_parameters.ForecastingParameters
        :param time_column_name:
            The name of the time column. This parameter is required when forecasting to specify the datetime
            column in the input data used for building the time series and inferring its frequency.
            This setting is being deprecated. Please use forecasting_parameters instead.
        :type time_column_name: str
        :param max_horizon:
            The desired maximum forecast horizon in units of time-series frequency. The default value is 1.
            This setting is being deprecated. Please use forecasting_parameters instead.

            Units are based on the time interval of your training data, e.g., monthly, weekly that the forecaster
            should predict out. When task type is forecasting, this parameter is required. For more information on
            setting forecasting parameters, see `Auto-train a time-series forecast model <https://docs.microsoft.com/
            azure/machine-learning/how-to-auto-train-forecast>`_.
        :type max_horizon: int
        :param grain_column_names:
            The names of columns used to group a timeseries.
            It can be used to create multiple series. If grain is not defined, the data set is assumed
            to be one time-series. This parameter is used with task type forecasting.
            This setting is being deprecated. Please use forecasting_parameters instead.
        :type grain_column_names: str or list(str)
        :param target_lags:
            The number of past periods to lag from the target column. The default is 1.
            This setting is being deprecated. Please use forecasting_parameters instead.

            When forecasting, this parameter represents the number of rows to lag the target values based
            on the frequency of the data. This is represented as a list or single integer. Lag should be used
            when the relationship between the independent variables and dependant variable do not match up or
            correlate by default. For example, when trying to forecast demand for a product, the demand in any
            month may depend on the price of specific commodities 3 months prior. In this example, you may want
            to lag the target (demand) negatively by 3 months so that the model is training on the correct
            relationship. For more information, see `Auto-train a time-series forecast model
            <https://docs.microsoft.com/azure/machine-learning/how-to-auto-train-forecast>`_.
        :type target_lags: int or list(int)
        :param feature_lags: Flag for generating lags for the numeric features.
            This setting is being deprecated. Please use forecasting_parameters instead.
        :type feature_lags: str
        :param target_rolling_window_size:
            The number of past periods used to create a rolling window average of the target column.
            This setting is being deprecated. Please use forecasting_parameters instead.

            When forecasting, this parameter represents `n` historical periods to use to generate forecasted values,
            <= training set size. If omitted, `n` is the full training set size. Specify this parameter
            when you only want to consider a certain amount of history when training the model.
        :type target_rolling_window_size: int
        :param country_or_region: The country/region used to generate holiday features.
            These should be ISO 3166 two-letter country/region codes, for example 'US' or 'GB'.
            This setting is being deprecated. Please use forecasting_parameters instead.
        :type country_or_region: str
        :param use_stl: Configure STL Decomposition of the time-series target column.
                    use_stl can take three values: None (default) - no stl decomposition, 'season' - only generate
                    season component and season_trend - generate both season and trend components.
                    This setting is being deprecated. Please use forecasting_parameters instead.
        :type use_stl: str
        :param seasonality: Set time series seasonality. If seasonality is set to -1, it will be inferred.
                    If use_stl is not set, this parameter will not be used.
                    This setting is being deprecated. Please use forecasting_parameters instead.
        :type seasonality: int
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
        :param enable_voting_ensemble:
            Whether to enable/disable VotingEnsemble iteration. The default is True.
            For more information about ensembles, see `Ensemble configuration
            <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`_.
        :type enable_voting_ensemble: bool
        :param enable_stack_ensemble:
            Whether to enable/disable StackEnsemble iteration. The default is None.
            If `enable_onnx_compatible_models` flag is being set, then StackEnsemble iteration will be disabled.
            Similarly, for Timeseries tasks, StackEnsemble iteration will be disabled by default, to avoid risks of
            overfitting due to small training set used in fitting the meta learner.
            For more information about ensembles, see `Ensemble configuration
            <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train#ensemble>`_.
        :type enable_stack_ensemble: bool
        :param debug_log:
            The log file to write debug information to. If not specified, 'automl.log' is used.
        :type debug_log: str
        :param training_data:
            The training data to be used within the experiment.
            It should contain both training features and a label column (optionally a sample weights column).
            If ``training_data`` is specified, then the ``label_column_name`` parameter must also be specified.

            ``training_data`` was introduced in version 1.0.81.
        :type training_data: pandas.DataFrame or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param validation_data:
            The validation data to be used within the experiment.
            It should contain both training features and label column (optionally a sample weights column).
            If ``validation_data`` is specified, then ``training_data`` and ``label_column_name`` parameters must
            be specified.

            ``validation_data`` was introduced in version 1.0.81. For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
        :type validation_data: pandas.DataFrame or azureml.core.Dataset
            or azureml.data.dataset_definition.DatasetDefinition or azureml.data.TabularDataset
        :param test_data:
            The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            The test data to be used for a test run that will automatically be started after
            model training is complete. The test run will get predictions using the best model
            and will compute metrics given these predictions.

            If this parameter or the ``test_size`` parameter are not specified then
            no test run will be executed automatically after model training is completed.
            Test data should contain both features and label column.
            If ``test_data`` is specified then the ``label_column_name`` parameter must be specified.
        :type test_data: azureml.core.Dataset or azureml.data.TabularDataset
        :param test_size:
            The Model Test feature using test datasets or test data splits is a feature in
            Preview state and might change at any time.
            What fraction of the training data to hold out for test data for a test run that will
            automatically be started after model training is complete. The test run will get
            predictions using the best model and will compute metrics given these predictions.

            This should be between 0.0 and 1.0 non-inclusive.
            If ``test_size`` is specified at the same time as ``validation_size``,
            then the test data is split from ``training_data`` before the validation data is split.
            For example, if ``validation_size=0.1``, ``test_size=0.1`` and the original training data has 1000 rows,
            then the test data will have 100 rows, the validation data will contain 90 rows
            and the training data will have 810 rows.

            For regression based tasks, random sampling is used. For classification
            tasks, stratified sampling is used. Forecasting does not currently
            support specifying a test dataset using a train/test split.

            If this parameter or the ``test_data`` parameter are not specified then
            no test run will be executed automatically after model training is completed.
        :type test_size: float
        :param label_column_name:
            The name of the label column. If the input data is from a pandas.DataFrame which doesn't
            have column names, column indices can be used instead, expressed as integers.

            This parameter is applicable to ``training_data``, ``validation_data`` and ``test_data`` parameters.
            ``label_column_name`` was introduced in version 1.0.81.
        :type label_column_name: typing.Union[str, int]
        :param weight_column_name:
            The name of the sample weight column. Automated ML supports a weighted column
            as an input, causing rows in the data to be weighted up or down.
            If the input data is from a pandas.DataFrame which doesn't have column names,
            column indices can be used instead, expressed as integers.

            This parameter is applicable to ``training_data`` and ``validation_data`` parameters.
            ``weight_column_names`` was introduced in version 1.0.81.
        :type weight_column_name: typing.Union[str, int]
        :param cv_split_column_names:
            List of names of the columns that contain custom cross validation split.
            Each of the CV split columns represents one CV split where each row are either marked
            1 for training or 0 for validation.

            This parameter is applicable to ``training_data`` parameter for custom cross validation purposes.
            ``cv_split_column_names`` was introduced in version 1.6.0

            Use either ``cv_split_column_names`` or ``cv_splits_indices``.

            For more information, see
            `Configure data splits and cross-validation in automated machine learning <https://docs.microsoft.com
            /azure/machine-learning/how-to-configure-cross-validation-data-splits>`__.
        :type cv_split_column_names: list(str)
        :param enable_local_managed: Disabled parameter. Local managed runs can not be enabled at this time.
        :type enable_local_managed: bool
        :param enable_dnn: Whether to include DNN based models during model selection. The default is False.
        :type enable_dnn: bool
        :raises azureml.train.automl.exceptions.ConfigException: Raised for problems with configuration.
            Each exception message describes the problem.
        :raises azureml.automl.core.shared.exceptions.ConfigException: Raised for configuration parameters that
            should be specified and were missing. Each exception message describes the problem.
        """
        self.user_settings = {}     # type: Dict[str, Any]
        self._run_configuration = None
        self.is_timeseries = False
        blocked_tf = []           # type: List[str]

        if task not in constants.Tasks.ALL:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="task_type", arguments=task,
                    supported_values=constants.Tasks.ALL
                )
            )
        if task == constants.Tasks.CLASSIFICATION:
            # set default metric if not set
            if primary_metric is None:
                primary_metric = constants.Metric.Accuracy
            if not self.user_settings.get('enable_tf') and not enable_tf:
                blocked_tf = [SupportedModels.Classification.TensorFlowDNNClassifier,
                              SupportedModels.Classification.TensorFlowLinearClassifier]
        elif task == constants.Tasks.IMAGE_CLASSIFICATION_MULTILABEL:
            if primary_metric is None:
                primary_metric = constants.Metric.IOU
        elif task == constants.Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION:  # for temporary backward-compatibility
            if primary_metric is None:
                primary_metric = constants.Metric.IOU
        elif task in [constants.Tasks.IMAGE_OBJECT_DETECTION, constants.Tasks.IMAGE_INSTANCE_SEGMENTATION]:
            if primary_metric is None:
                primary_metric = constants.Metric.MeanAveragePrecision
        elif task in constants.Tasks.ALL_IMAGE:
            if primary_metric is None:
                primary_metric = constants.Metric.Accuracy
        elif task in constants.Tasks.ALL_TEXT:
            if primary_metric is None:
                primary_metric = constants.Metric.Accuracy
        else:
            if task == constants.Tasks.FORECASTING:
                self.is_timeseries = True
                task = constants.Tasks.REGRESSION
            if primary_metric is None:
                primary_metric = constants.Metric.NormRMSE
            if not self.user_settings.get('enable_tf'):
                blocked_tf = [SupportedModels.Regression.TensorFlowDNNRegressor,
                              SupportedModels.Regression.TensorFlowLinearRegressor]

        if num_classes is not None:
            logger.warning("Parameter `num_classes` is being deprecated. Number of classes will be automatically "
                           "computed from the data.")
            num_classes = None

        if y_min is not None or y_max is not None:
            logger.warning("Parameters `y_min`, `y_max` are being deprecated. They will be automatically computed "
                           "from the data.")
            y_min = None
            y_max = None

        if isinstance(featurization, str):
            featurization = featurization.lower()
            if featurization == FeaturizationConfigMode.Off or featurization == FeaturizationConfigMode.Auto:
                self.user_settings['featurization'] = featurization
            else:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentWithSupportedValues, target="featurization", arguments=featurization,
                        supported_values=", ".join([FeaturizationConfigMode.Off, FeaturizationConfigMode.Auto])
                    )
                )
        elif isinstance(featurization, FeaturizationConfig):
            self.user_settings['featurization'] = featurization
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="featurization", arguments=featurization,
                    supported_values=", ".join([FeaturizationConfigMode.Off, FeaturizationConfigMode.Auto])
                )
            )

        # Deprecation of preprocess
        try:
            preprocess = kwargs.pop('preprocess')
            logging.warning("Parameter `preprocess` will be deprecated. Use `featurization`")
            if featurization == FeaturizationConfigMode.Auto and preprocess is False:
                self.user_settings['featurization'] = FeaturizationConfigMode.Off
            else:
                logging.warning("Detected both `preprocess` and `featurization`. `preprocess` is being deprecated "
                                "and will be overridden by `featurization` setting.")
        except KeyError:
            pass

        self.user_settings["enable_dnn"] = enable_dnn
        self.user_settings["force_text_dnn"] = kwargs.get("force_text_dnn", False)
        if task == constants.Tasks.CLASSIFICATION \
                and self.user_settings["enable_dnn"] \
                and self.user_settings['featurization'] == FeaturizationConfigMode.Off:
            self.user_settings['featurization'] = FeaturizationConfigMode.Auto
            logging.info("Resetting AutoMLConfig param featurization='auto' "
                         "required by neural nets for classification.")

        # disable tensorflow if module is not present or data is preprocessed outside tf.
        if enable_tf:
            logging.warning("Tensorflow support within AutoML is being deprecated.")
            if not AutoMLConfig._is_tensorflow_module_present():
                enable_tf = False
                logging.warning("tensorflow module is not installed")
            elif (isinstance(self.user_settings['featurization'], str) and
                  self.user_settings['featurization'] == FeaturizationConfigMode.Auto) or \
                    isinstance(self.user_settings['featurization'], FeaturizationConfig):
                enable_tf = False
                logging.info("tensorflow models are not supported with featurization")

        # Deprecation of blacklist_models
        if blacklist_models is not None:
            if blocked_models is not None and blocked_models != blacklist_models:
                raise ConfigException._with_error(
                    AzureMLError.create(ConflictingValueForArguments, argument_name="blacklist_models/blocked_models")
                )
            else:
                blocked_models = blacklist_models
            logging.warning("Parameter 'blacklist_models' will be deprecated. Use 'blocked_models'")

        # Deprecation of whitelist_models
        if whitelist_models is not None:
            if allowed_models is not None and allowed_models != whitelist_models:
                raise ConfigException._with_error(
                    AzureMLError.create(ConflictingValueForArguments, argument_name="whitelist_models/allowed_models")
                )
            else:
                allowed_models = whitelist_models
            logging.warning("Parameter 'whitelist_models' will be deprecated. Use 'allowed_models'")

        # validate allowed models aren't all blocked
        if not enable_tf or blocked_models is not None:
            blocked_models_temp = []
            if not enable_tf:
                blocked_models_temp.extend(blocked_tf)
            if blocked_models is not None:
                blocked_models_temp.extend(blocked_models)
            if len(blocked_models_temp) > 0:
                all_models = self._get_supported_models(task)

                if allowed_models is None:
                    if all_models is not None:
                        all_model_names = [m.customer_model_name for m in all_models]
                        if set(all_model_names).issubset(set(blocked_models_temp)):
                            raise ConfigException._with_error(
                                AzureMLError.create(
                                    AllowedModelsSubsetOfBlockedModels, target="allowed_models/blocked_models"
                                )
                            )
                else:
                    all_deprecated_model_names = [m.customer_model_name for m in all_models if m.is_deprecated]
                    if enable_tf:
                        all_deprecated_model_names = [m for m in all_deprecated_model_names if m not in blocked_tf]

                    if not enable_tf and set(allowed_models).issubset(set(blocked_tf)):
                        raise ConfigException._with_error(
                            AzureMLError.create(TensorflowAlgosAllowedButDisabled, target="enable_tf")
                        )

                    if any(model in allowed_models for model in all_deprecated_model_names):
                        msg = "Allowed models contains deprecated models. The following models are no longer " \
                              "supported. {}".format(all_deprecated_model_names)
                        logging.warning(msg)

                    if blocked_models_temp is not None and set(allowed_models).issubset(set(blocked_models_temp)):
                        raise ConfigException._with_error(
                            AzureMLError.create(
                                AllowedModelsSubsetOfBlockedModels, target="allowed_models/blocked_models"
                            )
                        )

        for key, value in kwargs.items():
            self.user_settings[key] = value

        # Validation/fixing of params for distributed Featurization.
        if "forecasting_dnn_models_only" in kwargs:
            param_override_msg = (
                "Enabling distributed featurization will result in the following parameter overrides:\n"
                "\tcv_step_size\n\ttarget_lags\n\tfeature_lags\n\ttarget_rolling_window_size\n\t"
                "cv based validation settings"
            )
            logging.warning(param_override_msg)
            # ensure these are enabled
            enable_dnn = True
            allowed_models = [SupportedModels.Forecasting.TCNForecaster]

            # ensure these are disabled
            cv_split_column_names = None
            cv_splits_indices = None

            # this is a dirty work around. See 1484325
            if validation_data is None:
                n_cross_validations = 2

            validation_size = None
            if forecasting_parameters:
                forecasting_parameters._cv_step_size = None
                forecasting_parameters._feature_lags = None
                forecasting_parameters._target_rolling_window_size = None
                forecasting_parameters._target_lags = None

                if forecasting_parameters.time_series_id_column_names is None:
                    logging.error("Distributed featurization requires time_series_id_column_names.")
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            NotSupported, scenario_name="missing_timeseries_ids"
                        )
                    )

            if spark_context:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        NotSupported, scenario_name="spark_context"
                    )
                )
            if enable_local_managed:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        NotSupported, scenario_name="local_managed"
                    )
                )
            if max_concurrent_iterations <= 1:
                logging.warning(
                    "max_concurrent_iterations will be used to determine cluster size for featurization. "
                    "It is recommended to use a value larger than 1 but no larger than max_cluster_size."
                )
                raise ConfigException._with_error(
                    AzureMLError.create(
                        NotSupported, scenario_name="max_concurrent_iterations<=1"
                    )
                )

            if not training_data.partition_keys:  # type: ignore
                raise DataException._with_error(
                    AzureMLError.create(
                        UnpartitionedData,
                        target="training_data"
                    )
                )

            if validation_data is not None and not validation_data.partition_keys:
                raise DataException._with_error(
                    AzureMLError.create(
                        UnpartitionedData,
                        target="validation_data"
                    )
                )

        self.user_settings['task_type'] = task
        self.user_settings["primary_metric"] = primary_metric
        self.user_settings["compute_target"] = compute_target
        self.user_settings["positive_label"] = positive_label

        # For backward compatibility if user passes these, keep as is
        self.user_settings['X'] = X
        self.user_settings['y'] = y
        self.user_settings['sample_weight'] = sample_weight
        self.user_settings['X_valid'] = X_valid
        self.user_settings['y_valid'] = y_valid
        self.user_settings['sample_weight_valid'] = sample_weight_valid
        self.user_settings['cv_splits_indices'] = cv_splits_indices
        self.user_settings['training_data'] = training_data
        self.user_settings['validation_data'] = validation_data
        self.user_settings['test_data'] = test_data
        self.user_settings['label_column_name'] = label_column_name
        self.user_settings['weight_column_name'] = weight_column_name
        self.user_settings['cv_split_column_names'] = cv_split_column_names
        self.user_settings["num_classes"] = num_classes
        self.user_settings["y_min"] = y_min
        self.user_settings["y_max"] = y_max
        self.user_settings["path"] = path
        self.user_settings["iterations"] = iterations
        self.user_settings["test_size"] = test_size
        self.user_settings["validation_size"] = validation_size
        self.user_settings["n_cross_validations"] = n_cross_validations
        self.user_settings["max_cores_per_iteration"] = max_cores_per_iteration
        self.user_settings["max_concurrent_iterations"] = max_concurrent_iterations
        self.user_settings["iteration_timeout_minutes"] = iteration_timeout_minutes
        self.user_settings["mem_in_mb"] = mem_in_mb
        self.user_settings["enforce_time_on_windows"] = enforce_time_on_windows
        # Set a default experiment timeout of 7 days (10080 minutes) if none specified
        self.user_settings["experiment_timeout_minutes"] = int(experiment_timeout_hours * 60) \
            if experiment_timeout_hours is not None else None
        self.user_settings["experiment_exit_score"] = experiment_exit_score
        self.user_settings["enable_early_stopping"] = enable_early_stopping
        self.user_settings["blocked_models"] = blocked_models
        self.user_settings["exclude_nan_labels"] = exclude_nan_labels
        self.user_settings["verbosity"] = verbosity
        self.user_settings["enable_tf"] = enable_tf
        self.user_settings["is_timeseries"] = self.is_timeseries
        self.user_settings["model_explainability"] = model_explainability
        self.user_settings["spark_context"] = spark_context
        self.user_settings["enable_subsampling"] = kwargs.get("enable_subsampling", None)
        self.user_settings["subsample_seed"] = kwargs.get("subsample_seed", None)
        self.user_settings["enable_onnx_compatible_models"] = enable_onnx_compatible_models
        self.user_settings["enable_split_onnx_featurizer_estimator_models"] = kwargs.get(
            "enable_split_onnx_featurizer_estimator_models", False)
        self.user_settings["enable_voting_ensemble"] = enable_voting_ensemble
        self.user_settings["enable_stack_ensemble"] = enable_stack_ensemble
        self.user_settings["debug_log"] = debug_log
        self.user_settings["forecasting_parameters"] = forecasting_parameters
        if enable_local_managed:
            logging.warning("enable_local_managed is an experimental flag to enable runs to be submitted to a separate"
                            "conda or docker environment on the local machine. Disable this flag or use a remote"
                            "compute if you face any issues.")
            self.user_settings["enable_local_managed"] = enable_local_managed

        if task in constants.Tasks.ALL_DNN:
            self._validate_and_default_dnn_tasks(task)

        enable_feature_sweeping = kwargs.get("enable_feature_sweeping", True)
        if not isinstance(enable_feature_sweeping, bool):
            logging.warning("enable_feature_sweeping should be a boolean variable. By default, feature sweeping is"
                            " enabled ")
            enable_feature_sweeping = True

        self.user_settings["enable_feature_sweeping"] = enable_feature_sweeping

        # Deprecation of X and y
        if X is not None:
            logging.warning("The AutoMLConfig parameters, X and y, will soon be deprecated. "
                            "Please refer to our documentation for the latest interface: "
                            "https://aka.ms/AutoMLConfig")

        # Deprecation of sample_weight
        if sample_weight is not None:
            logging.warning("The AutoMLConfig parameter sample_weight, will soon be deprecated. "
                            "Please refer to our documentation for the latest interface: "
                            "https://aka.ms/AutoMLConfig")

        # Deprecation of X_valid and y_valid
        if X_valid is not None:
            logging.warning("The AutoMLConfig parameters, X_valid and y_valid, will soon be deprecated. "
                            "Please refer to our documentation for the latest interface: "
                            "https://aka.ms/AutoMLConfig")

        # Deprecation of sample_weight_valid
        if sample_weight_valid is not None:
            logging.warning("The AutoMLConfig parameter sample_weight_valid, will soon be deprecated. "
                            "Please refer to our documentation for the latest interface: "
                            "https://aka.ms/AutoMLConfig")

        # Deprecation of cv_splits_indices
        if cv_splits_indices is not None:
            logging.warning("The AutoMLConfig parameter cv_splits_indices, will soon be deprecated. "
                            "Please refer to our documentation for the latest interface: "
                            "https://aka.ms/AutoMLConfig")

        # Depracation of autoblacklist
        auto_blacklist = kwargs.get('auto_blacklist')
        if auto_blacklist is not None:
            logging.warning("Parameter 'auto_blacklist' will be deprecated and enabled by default moving forward.'")
            self.user_settings["auto_blacklist"] = auto_blacklist

        # Deprecation of concurrent_iterations
        try:
            concurrent_iterations = kwargs.pop('concurrent_iterations')
            logging.warning("Parameter 'concurrent_iterations' will be deprecated. Use 'max_concurrent_iterations'")
            self.user_settings["max_concurrent_iterations"] = concurrent_iterations
        except KeyError:
            pass

        # Deprecation of max_time_sec
        try:
            max_time_sec = kwargs.pop('max_time_sec')
            logging.warning("Parameter 'max_time_sec' will be deprecated. Use 'iteration_timeout_minutes'")
            self.user_settings["iteration_timeout_minutes"] = math.ceil(max_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_time_sec
        try:
            exit_time_sec = kwargs.pop('exit_time_sec')
            logging.warning("Parameter 'exit_time_sec' will be deprecated. Use 'experiment_timeout_minutes'")
            self.user_settings["experiment_timeout_minutes"] = math.ceil(exit_time_sec / 60)
        except KeyError:
            pass

        # Deprecation of exit_score
        try:
            exit_score = kwargs.pop('exit_score')
            logging.warning("Parameter 'exit_score' will be deprecated. Use 'experiment_exit_score'")
            self.user_settings["experiment_exit_score"] = exit_score
        except KeyError:
            pass

        # Deprecation of debug_log
        try:
            debug_log = kwargs.pop('debug_log')
            logging.warning("Parameter 'debug_log' will be deprecated.")
            self.user_settings["debug_log"] = debug_log
        except KeyError:
            pass

        experiment_timeout_minutes = kwargs.get('experiment_timeout_minutes')
        if experiment_timeout_minutes is not None:
            # logging.warning('Parameter `experiment_timeout_minutes` will be deprecated moving forward. ' +
            #                'Use `experiment_timeout_hours`.')
            self.user_settings["experiment_timeout_minutes"] = experiment_timeout_minutes

        # Deprecation of data_script
        try:
            data_script = kwargs.pop('data_script')
            logging.warning("Get_data scripts will be deprecated. Instead of parameter 'data_script', "
                            "please pass a Dataset object into using the 'training_data' parameter.")
            self.user_settings["data_script"] = data_script
        except KeyError:
            pass

        # Deprecation of drop_column_names
        try:
            drop_column_names = kwargs.pop('drop_column_names')
            logging.warning(
                "Parameter 'drop_column_names' will be deprecated. Please drop columns from your "
                "datasets as part of your data preparation process before providing the datasets to AutoML.")
            self.user_settings["drop_column_names"] = drop_column_names
        except KeyError:
            pass

        # Internal parameter cost_mode
        try:
            cost_mode = kwargs.pop('cost_mode')
            logging.warning("cost_mode is an internal parameter that should not be used for regular experiments.")
            self.user_settings["cost_mode"] = cost_mode
        except KeyError:
            self.user_settings["cost_mode"] = constants.PipelineCost.COST_FILTER
            pass

        # Internal parameter for curated environment scenarios
        force_curated_environment = kwargs.get('force_curated_environment',
                                               os.environ.get("FORCE_CURATED_ENVIRONMENT", False))
        try:
            scenario = kwargs.pop(EnvironmentSettings.SCENARIO)
            logging.warning("{} is an internal parameter that should not be used for regular experiments.".format(
                EnvironmentSettings.SCENARIO
            ))
            self.user_settings[EnvironmentSettings.SCENARIO] = scenario
        except KeyError:
            scenario = os.environ.get(EnvironmentSettings.SCENARIO_ENV_VAR)
            if scenario is None:
                if task in constants.Tasks.ALL_IMAGE:
                    scenario = constants.Scenarios.VISION
                elif is_prod() or force_curated_environment:
                    scenario = constants.Scenarios.SDK_COMPATIBLE
                else:
                    scenario = constants.Scenarios._NON_PROD
            self.user_settings[EnvironmentSettings.SCENARIO] = scenario

        try:
            environment_label = kwargs.pop(EnvironmentSettings.ENVIRONMENT_LABEL)
            logging.warning("{} is an internal parameter that should not be used for regular experiments.".format(
                EnvironmentSettings.ENVIRONMENT_LABEL
            ))
            self.user_settings[EnvironmentSettings.ENVIRONMENT_LABEL] = environment_label
        except KeyError:
            environment_label = os.environ.get(EnvironmentSettings.ENVIRONMENT_LABEL_ENV_VAR)
            if environment_label is not None:
                self.user_settings[EnvironmentSettings.ENVIRONMENT_LABEL] = environment_label

        try:
            save_mlflow = kwargs.pop(MLFlowSettings.ML_FLOW_ARG)
            logging.warning("{} is an internal parameter that should not be used for regular experiments.".format(
                MLFlowSettings.ML_FLOW_ARG
            ))
            self.user_settings[MLFlowSettings.ML_FLOW_ARG] = save_mlflow
        except KeyError:
            save_mlflow = os.environ.get(MLFlowSettings.ML_FLOW_ENV_VAR)
            if save_mlflow is not None:
                self.user_settings[MLFlowSettings.ML_FLOW_ARG] = save_mlflow

        # Internal parameter start_auxiliary_runs_before_parent_complete
        if 'start_auxiliary_runs_before_parent_complete' in kwargs:
            logging.warning("start_auxiliary_runs_before_parent_complete is an internal parameter "
                            "that should not be used for regular experiments.")
        elif self._is_test_run_requested():
            self.user_settings["start_auxiliary_runs_before_parent_complete"] = True

        self.user_settings["allowed_models"] = allowed_models

        self._run_configuration = self.user_settings.get('run_configuration', None)

    def _get_fit_params(
        self,
        func: 'Callable[..., Optional[Any]]' = ExperimentDriver.start
    ) -> Dict[str, Any]:
        """
        Remove fit parameters from config.

        Inspects _AzureMLClient.fit() signature and builds a dictionary
        of args to be passed in from settings, using defaults as required
        and removes these params from settings.

        :returns: The dict of key, value for func.
        """
        fit_dict = {}
        fit_signature = inspect.signature(func)
        for k, v in fit_signature.parameters.items():
            # skip parameters
            if k in ['self', 'run_configuration', 'data_script', 'show_output']:
                continue

            default_val = v.default

            # Parameter.empty is returned for any parameters without a default
            # we will require these in settings
            if default_val is inspect.Parameter.empty:
                try:
                    fit_dict[k] = self.user_settings.get(k)
                except KeyError:
                    raise ConfigException._with_error(
                        AzureMLError.create(ArgumentBlankOrEmpty, argument_name=k)
                    )
            else:
                fit_dict[k] = self.user_settings.get(k, default_val)

        # overwrite default run_config with user provided or None
        fit_dict['run_configuration'] = self._run_configuration
        return fit_dict

    def _validate_config_settings(self, workspace: Optional[Workspace] = None) -> None:
        """Validate the configuration attributes."""
        # TODO: We have duplicate code for handling run configuration; it should be refactored
        # assert we have a run_config, if not create default
        # and assume default config
        if self._run_configuration is None:
            if 'run_configuration' not in self.user_settings.keys():
                self._run_configuration = RunConfiguration()
            elif isinstance(self.user_settings['run_configuration'], str):
                path = self.user_settings.get('path', '.')
                self._run_configuration = RunConfiguration.load(path=path,
                                                                name=self.user_settings['run_configuration'])
            else:
                self._run_configuration = self.user_settings['run_configuration']

        # ensure compute target is set
        if 'compute_target' in self.user_settings and self.user_settings['compute_target'] is not None:
            self._run_configuration.target = self.user_settings['compute_target']
            if self.user_settings['compute_target'] != constants.ComputeTargets.LOCAL:
                self._run_configuration.docker.use_docker = True
        else:
            self.user_settings['compute_target'] = self._run_configuration.target

        if self._run_configuration.framework.lower() not in list(Framework.FULL_SET):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="run_configuration",
                    arguments=self._run_configuration.framework,
                    supported_values=list(Framework.FULL_SET)
                )
            )

        has_training_input_dprep_obj = False
        has_training_input_pandas_obj = False
        has_training_input_intermediate_dataset_obj = False
        # input data consists of features (X) & label columns (y)
        has_many_feature_dataset_input = False
        # input data consists of one single training_data with label_column_name specified
        has_single_feature_dataset_input = False
        has_cv_split_indices = False
        for key in ['X', 'y', 'sample_weight', 'X_valid', 'y_valid', 'sample_weight_valid',
                    'cv_splits_indices', 'training_data', 'validation_data']:
            value = self.user_settings.get(key)
            if value is not None:
                if key == 'cv_splits_indices':
                    cv_splits_indices = value
                    if not isinstance(cv_splits_indices, list):
                        raise ConfigException._with_error(
                            AzureMLError.create(
                                InvalidCVSplits, target=key,
                                reference_code=ReferenceCodes._AUTOML_CONFIG_CV_SPLITS_INDICES_LIST_TYPE
                            )
                        )
                    has_cv_split_indices = True
                    for split in cv_splits_indices:
                        if not isinstance(split, list) or len(split) != 2:
                            raise ConfigException._with_error(
                                AzureMLError.create(
                                    InvalidCVSplits, target=key,
                                    reference_code=ReferenceCodes._AUTOML_CONFIG_CV_SPLITS_INDICES_LIST_LIST_TYPE
                                )
                            )

                        for item in split:
                            if dataprep_utilities.is_dataflow(item):
                                raise ConfigException._with_error(AzureMLError.create(InvalidCVSplits, target=key))
                            else:
                                has_training_input_pandas_obj = True
                else:
                    if key in ['training_data', 'validation_data']:
                        has_single_feature_dataset_input = True
                    else:
                        has_many_feature_dataset_input = True
                    if dataprep_utilities.is_dataflow(value):
                        raise ConfigException._with_error(
                            AzureMLError.create(
                                InvalidInputDatatype, target=key, input_type="azureml.dataprep.Dataflow",
                                supported_types=", ".join(SupportedInputDatatypes.ALL)
                            )
                        )
                    elif dataset_utilities.is_dataset(value):
                        has_training_input_dprep_obj = True
                    elif has_pipeline_pkg and isinstance(value, (
                            PipelineOutputTabularDataset, OutputTabularDatasetConfig
                    )):
                        has_training_input_intermediate_dataset_obj = True
                    elif has_pipeline_pkg and isinstance(value, DatasetConsumptionConfig)\
                            and value.mode == DIRECT_MODE:
                        has_training_input_intermediate_dataset_obj = True
                    else:
                        has_training_input_pandas_obj = True

        if (has_training_input_dprep_obj or has_training_input_intermediate_dataset_obj) \
                and has_training_input_pandas_obj:
            raise ConfigException._with_error(
                AzureMLError.create(InputDataWithMixedType, target=key, input_type="azureml.dataprep.Dataflow")
            )

        # check if dataframe has attribute rdd which is a concept of spark datafrane
        if (has_training_input_pandas_obj or hasattr(value, "rdd")) \
                and self.user_settings['spark_context'] is not None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidInputDatatype, target="spark_context", input_type=", ".join(['Pandas', 'Spark Dataframe']),
                    supported_types=", ".join(SupportedInputDatatypes.REMOTE_RUN_SCENARIO)
                )
            )

        if self.user_settings.get('track_child_runs') is False and \
                (self.user_settings['spark_context'] or
                 self.user_settings['compute_target'] != constants.ComputeTargets.LOCAL):
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentMismatch, target="track_child_runs",
                    argument_names=', '.join(['track_child_runs', 'spark_context', 'compute_target']),
                    value_list=', '.join([
                        str(self.user_settings.get('track_child_runs')), str(self.user_settings.get('spark_context')),
                        str(self.user_settings.get('compute_target'))
                    ])
                )
            )

        label_column_name_param_name = 'label_column_name'
        if has_single_feature_dataset_input:
            if has_many_feature_dataset_input:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ConflictingValueForArguments, target="X/y & training_data/validation_data",
                        arguments=", ".join(["label_column_name", "weight_column_name", "cv_split_column_names"]),
                        referece_code=ReferenceCodes._AUTOML_CONFIG_BOTH_X_AND_TRAINING_DATA
                    )
                )
            if self.user_settings[label_column_name_param_name] is None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty, target="label_column_name", argument_name=label_column_name_param_name
                    )
                )
        elif has_many_feature_dataset_input:
            if self.user_settings['X'] is None and self.user_settings['y'] is not None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty, target="X", argument_name="X",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_X_MISSING
                    )
                )
            elif self.user_settings['X'] is not None and self.user_settings['y'] is None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty, target="y", argument_name="y",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_Y_MISSING
                    )
                )
            elif self.user_settings['X'] is None and self.user_settings['y'] is None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty, target="X & y", argument_name="X & y",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_X_AND_Y_MISSING
                    )
                )

        compute_target = self.user_settings['compute_target']
        # The compute target here can either be str or ComputeTarget class, need a conversion here.
        if compute_target is not None and not isinstance(compute_target, str):
            compute_target = compute_target.name

        if compute_target != constants.ComputeTargets.LOCAL:
            # todo This is likely dead code that needs to be removed
            data_script_provided = self.user_settings.get('data_script') is not None
            if not data_script_provided and \
                    not (has_training_input_dprep_obj or has_training_input_intermediate_dataset_obj):
                if self.user_settings.get('X') is not None:
                    input_type = str(self.user_settings.get('X').__class__)
                    target = "X"
                else:
                    input_type = str(self.user_settings.get('training_data').__class__)
                    target = "training_data"

                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidInputDatatype, target=target, input_type=input_type,
                        supported_types=SupportedInputDatatypes.TABULAR_DATASET
                    )
                )
            if workspace is not None and compute_target is not None:
                all_compute_targets = workspace.compute_targets
                if compute_target not in all_compute_targets:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ComputeNotFound, target=compute_target,
                            compute_name=compute_target, workspace_name=workspace.name
                        )
                    )
                elif all_compute_targets[compute_target].provisioning_state != ProvisioningState.succeeded.value:
                    raise ConfigException._with_error(
                        AzureMLError.create(ComputeNotReady, target=compute_target)
                    )
                else:
                    # ensure vm size is set
                    if self._run_configuration.framework.lower() == "pyspark":
                        self.user_settings['vm_type'] = all_compute_targets[compute_target].node_size
                    else:
                        self.user_settings['vm_type'] = all_compute_targets[compute_target].vm_size

        is_timeseries = self.user_settings['is_timeseries']

        self._validate_test_settings(is_timeseries, has_cv_split_indices, compute_target)

        if self.user_settings['task_type'] not in constants.Tasks.ALL_DNN:
            self._validate_streaming_models(is_timeseries, compute_target)

        if (self.user_settings.get('training_data', None) is not None and
            self.user_settings.get(label_column_name_param_name, None) is None) or \
                (self.user_settings.get(label_column_name_param_name, None) is not None and
                 self.user_settings.get('training_data', None) is None):
            whats_none, ref_code = ("training_data", ReferenceCodes._AUTOML_CONFIG_TRAINING_DATA_MISSING) \
                if self.user_settings.get('training_data') is None \
                else ("label_column_name", ReferenceCodes._AUTOML_CONFIG_LABEL_COL_NAME_MISSING)
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target=whats_none, argument_name=whats_none, reference_code=ref_code
                )
            )

        if self.user_settings.get('validation_data', None) is not None and \
                (self.user_settings.get('training_data', None) is None or
                 self.user_settings.get(label_column_name_param_name, None) is None):
            whats_none, ref_code = ("training_data", ReferenceCodes._AUTOML_CONFIG_TRAINING_DATA_MISSING) \
                if self.user_settings.get('training_data') is None \
                else ("label_column_name", ReferenceCodes._AUTOML_CONFIG_LABEL_COL_NAME_MISSING)
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target=whats_none, argument_name=whats_none, reference_code=ref_code
                )
            )

        # Label Column Name
        if self.user_settings.get(label_column_name_param_name) is not None:
            label_column_name_val = self.user_settings.get(label_column_name_param_name)
            # todo is there a scenario where we are accessing the label column via an integer index?
            # if not, the following should only check for string
            if not ((isinstance(label_column_name_val, int) and has_training_input_pandas_obj) or
                    isinstance(label_column_name_val, str)):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target=label_column_name_param_name,
                        argument=label_column_name_param_name, actual_type=type(label_column_name_val),
                        expected_types=", ".join(["int", "str"]),
                        reference_code=ReferenceCodes._AUTOML_CONFIG_LABEL_COL_NAME_WRONG_TYPE
                    )
                )
        # Weight Column Name
        if self.user_settings.get('weight_column_name') is not None:
            weight_column_name_val = self.user_settings.get('weight_column_name')
            if not ((isinstance(weight_column_name_val, int) and has_training_input_pandas_obj) or
                    isinstance(weight_column_name_val, str)):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target="weight_column_name",
                        argument="weight_column_name", actual_type=type(weight_column_name_val),
                        expected_types=", ".join(["int", "str"]),
                        reference_code=ReferenceCodes._AUTOML_CONFIG_SAMPLE_WEIGHT_COL_NAME_WRONG_TYPE
                    )
                )
        # CV Split Column Name
        if self.user_settings.get('cv_split_column_names') and has_many_feature_dataset_input:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="cv_split_indices", argument_name="cv_split_indices",
                    reference_code=ReferenceCodes._AUTOML_CONFIG_CV_SPLITS_INDICES_NEEDED
                )
            )
        if has_cv_split_indices and has_single_feature_dataset_input:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="cv_split_column_names", argument_name="cv_split_column_names",
                    reference_code=ReferenceCodes._AUTOML_CONFIG_CV_SPLIT_COL_NAMES_NEEDED
                )
            )
        if self.user_settings.get('cv_split_column_names'):
            cv_split_column_names_val = self.user_settings.get('cv_split_column_names', [])
            # TabularDatasets do not allow manipulating columns so input columns must be of type str
            invalid_col_type = (not isinstance(cv_split_column_names_val, list)) or any(not isinstance(
                col, str) for col in cv_split_column_names_val) and not has_training_input_pandas_obj
            if invalid_col_type:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target="cv_split_column_names",
                        argument="cv_split_column_names", actual_type=type(cv_split_column_names_val),
                        expected_types="List[str]",
                        reference_code=ReferenceCodes._AUTOML_CONFIG_CV_SPLIT_COL_NAMES_WRONG_TYPE
                    )
                )
        # Check if any of the three types of input column names overlap
        if has_single_feature_dataset_input:
            temp_label_column_name = str(self.user_settings.get('label_column_name', '')).lower()
            temp_weight_column_name = str(self.user_settings.get('weight_column_name', '')).lower() \
                if self.user_settings.get('weight_column_name') is not None else ''
            temp_cv_split_column_names = self.user_settings.get('cv_split_column_names', [])
            is_cv_name_duplicate = False
            if temp_cv_split_column_names is not None:
                is_cv_name_duplicate = (
                    any(str(x).lower() == temp_label_column_name for x in temp_cv_split_column_names) or
                    any(str(x).lower() == temp_weight_column_name for x in temp_cv_split_column_names)
                )
            if temp_label_column_name == temp_weight_column_name or is_cv_name_duplicate:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ConflictingValueForArguments, target=temp_label_column_name,
                        arguments=", ".join(["label_column_name", "weight_column_name", "cv_split_column_names"]),
                        reference_code=ReferenceCodes._AUTOML_CONFIG_DUPLICATE_COL_NAMES
                    )
                )

        _check_validation_config(
            X_valid=self.user_settings.get('X_valid', None),
            y_valid=self.user_settings.get('y_valid', None),
            sample_weight=self.user_settings.get('sample_weight', None),
            sample_weight_valid=self.user_settings.get('sample_weight_valid', None),
            cv_splits_indices=self.user_settings.get('cv_splits_indices', None),
            n_cross_validations=self.user_settings.get('n_cross_validations', None),
            validation_size=self.user_settings.get('validation_size', None),
            validation_data=self.user_settings.get('validation_data', None),
            cv_split_column_names=self.user_settings.get('cv_split_column_names', None)
        )

    @classmethod
    def get_supported_dataset_languages(cls, use_gpu: bool) -> Dict[Any, Any]:
        """
        Get supported languages and their corresponding language codes in ISO 639-3.

        :param cls: Class object of :class:`azureml.train.automl.automlconfig.AutoMLConfig`.
        :param use_gpu: boolean indicating whether gpu compute is being used or not.
        :return: dictionary of format {<language code>: <language name>}.  Language code adheres to
            ISO 639-3 standard, please refer to https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
        """
        # all supported languages if enable_dnn and (running locally or running with GPU compute)
        return TextDNNLanguages.supported if use_gpu else TextDNNLanguages.cpu_supported

    def _validate_test_settings(self,
                                is_timeseries: bool,
                                has_cv_split_indices: bool,
                                compute_target: str) -> None:
        if self.user_settings.get('test_data'):
            if self.user_settings.get('spark_context'):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_data",
                        feature_name='model test', arguments="test_data, spark_context"
                    )
                )

            if compute_target == constants.ComputeTargets.LOCAL:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_data",
                        feature_name='model test', arguments="test_data, compute_target"
                    )
                )

            label_column_name_param_name = 'label_column_name'
            if self.user_settings.get(label_column_name_param_name, None) is None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty,
                        target=label_column_name_param_name,
                        argument_name=label_column_name_param_name,
                        reference_code=ReferenceCodes._AUTOML_CONFIG_LABEL_COL_NAME_MISSING
                    )
                )

        test_size = self.user_settings.get("test_size")
        if test_size is None:
            return

        # These values match the checks which are
        # performed in the Jasmine validation service.
        min_split_size = 0.0
        max_split_size = 0.99

        if test_size > max_split_size or test_size < min_split_size:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target="test_size", argument_name="test_size",
                    min=min_split_size, max=max_split_size
                )
            )

        if test_size > 0.0:
            validation_size = self.user_settings.get("validation_size")
            if validation_size is not None:
                combined_split_size = validation_size + test_size
                if combined_split_size > max_split_size or combined_split_size < min_split_size:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ArgumentOutOfRange, target="validation_size/test_size",
                            argument_name="validation_size + test_size",
                            min=min_split_size, max=max_split_size
                        )
                    )

            if self.user_settings.get('test_data'):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_size",
                        feature_name='model test', arguments="test_size, test_data"
                    )
                )

            if self.user_settings.get('cv_split_column_names'):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_size",
                        feature_name='test split', arguments="test_size, cv_split_column_names"
                    )
                )

            if has_cv_split_indices:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_size",
                        feature_name='test split', arguments="test_size, cv_splits_indices"
                    )
                )

            if is_timeseries:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_size",
                        feature_name='forecasting', arguments="test_size"
                    )
                )

            if self.user_settings.get('spark_context'):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_size",
                        feature_name='model test', arguments="test_size, spark_context"
                    )
                )

            if compute_target == constants.ComputeTargets.LOCAL:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_size",
                        feature_name='model test', arguments="test_size, compute_target"
                    )
                )

    def _is_test_run_requested(self) -> bool:
        test_data = self.user_settings.get('test_data')
        test_run_requested = test_data is not None or self._has_valid_test_size()
        return test_run_requested

    def _has_valid_test_size(self) -> bool:
        test_size = self.user_settings.get("test_size")
        return test_size is not None and test_size > 0.0

    def _validate_streaming_models(self, is_timeseries: bool, compute_target: str) -> None:
        allowed_models = self.user_settings.get('allowed_models', [])
        blocked_models = self.user_settings.get('blocked_models', [])
        effective_models = [m.customer_model_name for m in self._get_supported_models(self.user_settings['task_type'])]
        if allowed_models:
            effective_models = allowed_models
        if blocked_models:
            effective_models = list(set(effective_models).difference(set(blocked_models)))
        if not self.user_settings.get('enable_tf'):
            effective_models = list(set(effective_models).difference({
                SupportedModels.Classification.TensorFlowDNNClassifier,
                SupportedModels.Classification.TensorFlowLinearClassifier,
                SupportedModels.Regression.TensorFlowDNNRegressor,
                SupportedModels.Regression.TensorFlowLinearRegressor}))

        streaming_supported_algorithms = {SupportedModels.Classification.AveragedPerceptronClassifier,
                                          SupportedModels.Regression.FastLinearRegressor,
                                          SupportedModels.Regression.OnlineGradientDescentRegressor}

        effective_models_all_streaming = set(effective_models).issubset(streaming_supported_algorithms)
        if effective_models_all_streaming:
            if self.user_settings.get('X') is not None \
                or self.user_settings.get('spark_context') \
                or compute_target == constants.ComputeTargets.LOCAL \
                or is_timeseries \
                or self._has_valid_test_size() \
                or self.user_settings.get("n_cross_validations") \
                or self.user_settings.get("enable_onnx_compatible_models") \
                or self.user_settings.get("enable_dnn") \
                    or self.user_settings.get("enable_subsampling"):
                raise ConfigException._with_error(
                    AzureMLError.create(LargeDataAlgorithmsWithUnsupportedArguments))

        if allowed_models:
            allowed_models_some_streaming = set(allowed_models).intersection(streaming_supported_algorithms)
            if allowed_models_some_streaming:
                if compute_target == constants.ComputeTargets.LOCAL or self.user_settings['spark_context']:
                    logger.warning('AveragedPerceptronClassifier, FastLinearRegressor, '
                                   'OnlineGradientDescentRegressor algorithms are only supported on remote compute '
                                   'target. Please review algorithms mentioned in argument: allowed_models.')
                if is_timeseries:
                    logger.warning('AveragedPerceptronClassifier, FastLinearRegressor, OnlineGradientDescentRegressor '
                                   'algorithms are not supported in Forecasting scenario. Please review algorithms '
                                   'mentioned in argument: allowed_models.')

    def _get_supported_models(self, task):
        all_models = None
        if task == constants.Tasks.CLASSIFICATION:
            all_models = SupportedModelNames.SupportedClassificationModelList
        # Forecast task.
        if self.is_timeseries and task == constants.Tasks.REGRESSION:
            all_models = SupportedModelNames.SupportedForecastingModelList
        elif task == constants.Tasks.REGRESSION:
            all_models = SupportedModelNames.SupportedRegressionModelList
        return all_models

    def _validate_and_default_dnn_tasks(self, task):
        if not self.user_settings["enable_dnn"]:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValuesForTask,
                    arguments="enable_dnn",
                    task_type=task,
                    supported_values=True
                )
            )
        if self.user_settings.get('training_data', None):
            if not hasattr(self.user_settings['training_data'], 'id') or not self.user_settings['training_data'].id:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target='training_data',
                        argument='training_data', actual_type=type(self.user_settings['training_data']),
                        expected_types="Labeled Dataset with a GUID set as id."
                    )
                )
            self.user_settings['dataset_id'] = self.user_settings['training_data'].id
        if self.user_settings.get('validation_data', None):
            if not hasattr(self.user_settings['validation_data'], 'id') or \
                    not self.user_settings['validation_data'].id:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target='validation_data',
                        argument='validation_data', actual_type=type(self.user_settings['validation_data']),
                        expected_types="Labeled Dataset with a GUID set as id."
                    )
                )
            self.user_settings['validation_dataset_id'] = self.user_settings['validation_data'].id
        if task in constants.Tasks.ALL_IMAGE or task == constants.Tasks.TEXT_NER:
            if self.user_settings.get('label_column_name', None):
                logging.warning("Parameter 'label_column_name' is ignored for DNN task types.")
            else:
                self.user_settings['label_column_name'] = 'label'

    @staticmethod
    def _is_tensorflow_module_present():
        try:
            from azureml.automl.runtime.shared import pipeline_spec
            return pipeline_spec.tf_wrappers.tf_found
        except Exception:
            return False

    @staticmethod
    def _is_xgboost_module_present():
        try:
            from azureml.automl.runtime.shared import model_wrappers
            return model_wrappers.xgboost_present
        except Exception:
            return False

    @staticmethod
    def _is_fbprophet_module_present():
        fbprophet = import_utilities.import_fbprophet(raise_on_fail=False)
        return fbprophet is not None
