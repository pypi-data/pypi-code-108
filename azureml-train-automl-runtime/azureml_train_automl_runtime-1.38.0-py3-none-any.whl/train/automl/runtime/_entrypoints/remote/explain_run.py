# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
import sys
from typing import Any, Dict

from azureml._tracing import get_tracer
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.core import Run
from azureml.train.automl._azure_experiment_observer import AzureExperimentObserver
from azureml.train.automl.constants import ComputeTargets
from azureml.train.automl.run import AutoMLRun
from azureml.train.automl.runtime._automl_job_phases import ModelExplainPhase
from azureml.train.automl.runtime._automl_model_explain import (
    AutoMLModelExplainTelemetryStrings, ModelExplainParams)
from azureml.train.automl.runtime.automl_explain_utilities import ModelExplanationRunId
from azureml.train.automl.utilities import _get_package_version
from azureml.train.automl.runtime._entrypoints import entrypoint_util

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: str,
        automl_settings: str,
        run_id: str,
        child_run_id: str,
        dataprep_json: str,
        entry_point: str,
        **kwargs: Any
) -> Dict[str, Any]:
    """
    Compute best run model or on-demand explanations in remote runs.

    :param script_directory:
    :param automl_settings:
    :param run_id: The run id for model explanations run. This is AutoML_<GUID>_ModelExplain in case
                   of best run model explanations and <GUID> in case of on-demand explanations.
    :param child_run_id: The AutoML child run id for which to compute on-demand explanations for.
                         This is 'None' for best run model explanations and an AutoMl child run-id
                         for on-demand model explanation run.
    :param dataprep_json:
    :param entry_point:
    :param kwargs:
    :return:
    """
    model_exp_output = {}  # type: Dict[str, Any]
    current_run = Run.get_context()
    logger.info("The model explanation run-id is: " + str(current_run.id))
    if child_run_id:
        automl_run_obj = Run(current_run.experiment, child_run_id)
    else:
        automl_run_obj = current_run
    automl_settings_obj = entrypoint_util.initialize_log_server(automl_run_obj.id, automl_settings)
    pkg_ver = _get_package_version()
    logger.info('Using SDK version {}'.format(pkg_ver))
    try:
        if not child_run_id:
            parent_run_id = entrypoint_util.get_parent_run_id(run_id)
        else:
            parent_run_id = entrypoint_util.get_parent_run_id(child_run_id)
        parent_run = AutoMLRun(current_run.experiment, parent_run_id)
        use_fd_cache = False
        if hasattr(automl_settings_obj, "use_fd_cache"):
            use_fd_cache = True
        cache_store = entrypoint_util.init_cache_store(parent_run.experiment, parent_run_id, use_fd_cache=use_fd_cache)
        expr_store = ExperimentStore(cache_store, read_only=True)
        expr_store.load()

        if not child_run_id:
            logger.info(AutoMLModelExplainTelemetryStrings.REMOTE_BEST_RUN_MODEL_EXPLAIN_START_STR.format(
                parent_run_id))
            print(AutoMLModelExplainTelemetryStrings.REMOTE_BEST_RUN_MODEL_EXPLAIN_START_STR.format(
                parent_run_id))

            # Get the best run model explanation
            experiment_observer = AzureExperimentObserver(parent_run, console_logger=sys.stdout)
            ModelExplainPhase.explain_best_run(
                parent_run, ModelExplainParams(automl_settings_obj),
                compute_target=ComputeTargets.AMLCOMPUTE,
                current_run=current_run,
                experiment_observer=experiment_observer)
        else:
            logger.info(AutoMLModelExplainTelemetryStrings.REMOTE_ON_DEMAND_RUN_MODEL_EXPLAIN_START_STR.format(
                child_run_id))
            print(AutoMLModelExplainTelemetryStrings.REMOTE_ON_DEMAND_RUN_MODEL_EXPLAIN_START_STR.format(
                child_run_id))

            child_run = Run(current_run.experiment, child_run_id)
            if current_run is not None:
                child_run.set_tags({ModelExplanationRunId: str(current_run.id)})

            ModelExplainPhase.explain_run(child_run, ModelExplainParams(automl_settings_obj))
        run_lifecycle_utilities.complete_run(current_run)
    except Exception as e:
        if not child_run_id:
            logger.error(AutoMLModelExplainTelemetryStrings.REMOTE_BEST_RUN_MODEL_EXPLAIN_ERROR_STR)
        else:
            logger.error(AutoMLModelExplainTelemetryStrings.REMOTE_ON_DEMAND_RUN_MODEL_EXPLAIN_ERROR_STR)
        run_lifecycle_utilities.fail_run(current_run, e)
        raise
    finally:
        # Reset the singleton for subsequent usage.
        ExperimentStore.reset()

    return model_exp_output
