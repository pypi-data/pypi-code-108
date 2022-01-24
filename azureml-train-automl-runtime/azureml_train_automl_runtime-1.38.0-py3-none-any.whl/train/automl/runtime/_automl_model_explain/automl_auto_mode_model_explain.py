# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

import logging
import json

from azureml._common._error_definition import AzureMLError
from azureml.automl.core import package_utilities
from azureml.automl.core._experiment_observer import ExperimentStatus, NullExperimentObserver
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.console_interface import ConsoleInterface
from azureml.automl.core._run import RunType
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.core import Run
from azureml.train.automl._azure_experiment_observer import ExperimentObserver
from azureml.train.automl.exceptions import ConfigException, ClientException
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver import (
    AutoMLModelExplainDriver)
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_driver_factory import (
    AutoMLModelExplainDriverFactory)
from azureml.train.automl.runtime._automl_model_explain.automl_model_explain_helper import (
    _check_model_explain_packages, _should_query_for_best_run, _log_blackbox_explainer_replication_measure)
from azureml.train.automl.runtime.automl_explain_utilities import (
    ModelExplanationRunId, ModelExplanationBestRunChildId, ModelExpDebugPkgList,
    _get_user_friendly_surrogate_model_name, EngineeredExpFolderName, RawExpFolderName)
from azureml.train.automl.runtime.run import AutoMLRun

logger = logging.getLogger(__name__)


class ModelExplainParams:
    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.model_explainability = automl_settings.model_explainability
        self.task_type = automl_settings.task_type
        self.is_timeseries = automl_settings.is_timeseries
        self.enable_streaming = automl_settings.enable_streaming
        self.max_cores_per_iteration = automl_settings.max_cores_per_iteration
        self.label_column_name = automl_settings.label_column_name


class AutoMLModelExplainTelemetryStrings:
    """
    Strings for capturing telemetry around the number of explanation runs.

    These strings shouldn't be changed. If these are changed, then the jarvis dashboard for tracking
    the telemetry for explanations also needs to be changed accordingly.
    """
    REMOTE_BEST_RUN_MODEL_EXPLAIN_START_STR = 'Beginning best run remote model explanations for run {}.'
    REMOTE_ON_DEMAND_RUN_MODEL_EXPLAIN_START_STR = 'Beginning on-demand remote model explanations for run {}.'
    REMOTE_BEST_RUN_MODEL_EXPLAIN_ERROR_STR = "Error in best run model explanations computation."
    REMOTE_ON_DEMAND_RUN_MODEL_EXPLAIN_ERROR_STR = "Error in on-demand model explanations computation."


def _automl_perform_best_run_explain_model(parent_run: AutoMLRun,
                                           model_explain_params: ModelExplainParams,
                                           compute_target: Optional[str] = None,
                                           current_run: Optional[Run] = None,
                                           experiment_observer: Optional[ExperimentObserver] = None,
                                           console_interface: Optional[ConsoleInterface] = None) -> None:
    """
    Explain the best model in the training stage and store the explanation in that child run.

    :param parent_run: The automated ML parent run.
    :type parent_run: azureml.train.automl.run.AutoMLRun
    :param model_explain_params: Automated ML run settings.
    :type model_explain_params: ModelExplainParams
    :param compute_target: Local/ADB/Remote
    :type compute_target: str
    :param current_run: Current run for computing model explanations.
    :param current_run: azureml.core.Run
    :param experiment_observer: The experiment observer.
    :type experiment_observer: azureml.train.automl._azure_experiment_observer.ExperimentObserver
    :param console_interface: The console interface to write the status of model explanation run.
    :type console_interface: azureml.automl.core.console_interface.ConsoleInterface
    :return: None
    """
    try:
        if parent_run._has_cached_output() or _should_query_for_best_run(parent_run):
            best_run = parent_run.get_best_child()
            logger.info("Computing model explanations for best run {0} on {1}".format(best_run.id,
                                                                                      compute_target))
            if current_run is not None:
                best_run.set_tags({ModelExplanationRunId: str(current_run.id)})

            if experiment_observer is not None and console_interface is not None:
                console_interface.print_section_separator()

            # Get the model explain driver class for explaining this model
            _explain_run(best_run, model_explain_params, experiment_observer)

            if experiment_observer is not None and console_interface is not None:
                console_interface.print_section_separator()

            parent_run.tag(ModelExplanationBestRunChildId, best_run.id)
        else:
            logger.warning("Skipping computing model explanation on best run because some artifacts are missing")
            raise ClientException._with_error(AzureMLError.create(
                AutoMLInternal, target="model_explainability",
                reference_code=ReferenceCodes._MODEL_EXPLAIN_INSUFFICIENT_CHILD_RUN_METRICS,
                error_details='Not all child run metrics found')
            )
    except Exception as e:
        logging_utilities.log_traceback(e, logger, is_critical=False)
        logger.warning(
            "Failed model explanation for best run on {0}.".format(compute_target)
        )
        failure_msg = None
        if isinstance(e, ConfigException):
            failure_msg = e.message
        if experiment_observer is not None:
            experiment_observer.report_status(
                ExperimentStatus.FailedModelExplanations,
                "Failed to explain best model" if failure_msg is None else failure_msg
            )
            if console_interface is not None:
                console_interface.print_section_separator()
        raise


def _automl_auto_mode_explain_model(automl_model_explain_driver: AutoMLModelExplainDriver,
                                    experiment_observer: Optional[ExperimentObserver] = None) -> None:
    """
    Explain the model in the fit stage and store the explanation in child_run.

    :param automl_model_explain_driver: Model explain data object.
    :type automl_model_explain_driver: azureml.train.automl.runtime._automl_model_explain.AutoMLModelExplainDriver
    :param experiment_observer: The experiment observer.
    :type experiment_observer: ExperimentObserver

    :return: None
    """
    # Log the versions for relevant packages for model explainability
    all_dependencies_pkg_versions = package_utilities._all_dependencies()
    model_exp_pkg_versions = {package: all_dependencies_pkg_versions[package]
                              for package in ModelExpDebugPkgList if package in all_dependencies_pkg_versions}
    logger.info('The dependent model explainability packages are:- ' + json.dumps(model_exp_pkg_versions))

    # Check if the dependent packages are available. If not then raise exception
    _check_model_explain_packages()

    experiment_observer = experiment_observer or NullExperimentObserver()

    from azureml.interpret.mimic_wrapper import MimicWrapper

    experiment_observer.report_status(ExperimentStatus.BestRunExplainModel,
                                      "Best run model explanations started")

    logger.info("[RunId:{}]Start auto mode model explanations".format(
        automl_model_explain_driver._automl_child_run.id))

    # Get the model exp run object if available
    model_exp_run_id = automl_model_explain_driver._automl_child_run.tags.get(
        ModelExplanationRunId)
    if model_exp_run_id is not None:
        model_exp_run = Run(experiment=automl_model_explain_driver._automl_child_run.experiment,
                            run_id=model_exp_run_id)
        user_sdk_dependencies_property = {'dependencies_versions': json.dumps(
            package_utilities.get_sdk_dependencies())}
        model_exp_run.add_properties(user_sdk_dependencies_property)
    else:
        model_exp_run = None

    # Setup data and feature names for explanations
    automl_model_explain_driver.setup_model_explain_data()

    # Log stats about explanation data
    AutoMLModelExplainDriver.log_explanation_data_stats(automl_model_explain_driver)

    # Validate the explanation data
    AutoMLModelExplainDriver.validate_model_explain_driver(automl_model_explain_driver)

    experiment_observer.report_status(ExperimentStatus.ModelExplanationDataSetSetup,
                                      "Model explanations data setup completed")
    experiment_observer.report_status(
        ExperimentStatus.PickSurrogateModel,
        "Choosing {0} as the surrogate model for explanations".format(
            _get_user_friendly_surrogate_model_name(
                automl_model_explain_driver._automl_explain_config_obj.surrogate_model)))

    explainer = MimicWrapper(
        workspace=automl_model_explain_driver._automl_child_run.experiment.workspace,
        model=automl_model_explain_driver._automl_explain_config_obj.automl_estimator,
        explainable_model=automl_model_explain_driver._automl_explain_config_obj.surrogate_model,
        init_dataset=automl_model_explain_driver._automl_explain_config_obj.X_transform,
        run=automl_model_explain_driver._automl_child_run,
        features=automl_model_explain_driver._automl_explain_config_obj.engineered_feature_names,
        feature_maps=automl_model_explain_driver._automl_explain_config_obj.feature_map,
        classes=automl_model_explain_driver._automl_explain_config_obj.classes,
        explainer_kwargs=automl_model_explain_driver._automl_explain_config_obj.surrogate_model_params)

    experiment_observer.report_status(ExperimentStatus.EngineeredFeaturesExplanations,
                                      "Computation of engineered features started")

    _log_blackbox_explainer_replication_measure(
        mimic_explainer=explainer,
        training_data=automl_model_explain_driver._automl_explain_config_obj.X_test_transform,
        run_algorithm=automl_model_explain_driver._automl_child_run.properties.get('run_algorithm'))

    # Compute the engineered explanations
    eng_explanation = explainer.explain(
        explanation_types=['local', 'global'],
        eval_dataset=automl_model_explain_driver._automl_explain_config_obj.X_test_transform,
        top_k=automl_model_explain_driver._automl_explain_config_obj._top_k,
        true_ys=automl_model_explain_driver._automl_explain_config_obj._y_test_raw)

    if model_exp_run is not None:
        model_exp_run.add_properties({EngineeredExpFolderName: str(eng_explanation.id)})
    logger.info("Computation of engineered feature importance completed.")

    experiment_observer.report_status(ExperimentStatus.EngineeredFeaturesExplanations,
                                      "Computation of engineered features completed")

    experiment_observer.report_status(ExperimentStatus.RawFeaturesExplanations,
                                      "Computation of raw features started")

    if automl_model_explain_driver.should_upload_raw_dataset():
        raw_eval_dataset = automl_model_explain_driver._automl_explain_config_obj.X_test_raw
    else:
        raw_eval_dataset = None

    # Compute the raw explanations
    raw_explanation = explainer._automl_aggregate_and_upload(
        eng_explanation=eng_explanation,
        raw_feature_names=automl_model_explain_driver._automl_explain_config_obj.raw_feature_names,
        top_k=automl_model_explain_driver._automl_explain_config_obj._top_k,
        raw_eval_dataset=raw_eval_dataset,
        true_ys=automl_model_explain_driver._automl_explain_config_obj._y_test_raw)
    if model_exp_run is not None:
        model_exp_run.add_properties({RawExpFolderName: str(raw_explanation.id)})

    experiment_observer.report_status(ExperimentStatus.RawFeaturesExplanations,
                                      "Computation of raw features completed")
    logger.info("Computation of raw feature importance completed.")

    logger.info("[RunId:{}]End auto mode model explanation".format(automl_model_explain_driver._automl_child_run.id))

    experiment_observer.report_status(ExperimentStatus.BestRunExplainModel,
                                      "Best run model explanations completed")


def _explain_run(child_run: RunType,
                 model_explain_params: ModelExplainParams,
                 experiment_observer: Optional[ExperimentObserver] = None) -> None:
    """
    Execute the model explain run.

    :param child_run: The explain run
    :param model_explain_params: ModelExplainParams for the parent run.
    :param experiment_observer: The ExperimentObserver used to track model explanations
    :return:
    """
    # Get the model explain driver class for explaining this model
    automl_model_explain_driver = AutoMLModelExplainDriverFactory._get_model_explain_driver(
        automl_child_run=child_run,
        task_type=model_explain_params.task_type,
        is_timeseries=model_explain_params.is_timeseries,
        enable_streaming=model_explain_params.enable_streaming,
        max_cores_per_iteration=model_explain_params.max_cores_per_iteration,
        label_column_name=model_explain_params.label_column_name)
    _automl_auto_mode_explain_model(automl_model_explain_driver, experiment_observer)
