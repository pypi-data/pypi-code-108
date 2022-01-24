# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
from typing import Any, Optional

from azureml._tracing import get_tracer
from azureml.automl.runtime._ml_engine.validation import common_data_validations
from azureml.train.automl._azure_experiment_observer import AzureExperimentObserver

from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.constants import FeaturizationRunConstants, PreparationRunTypeConstants
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime._data_transformation_utilities import (
    FeaturizationJsonParser, save_engineered_feature_names, save_feature_config)
from azureml.automl.runtime._feature_sweeped_state_container import FeatureSweepedStateContainer
from azureml.automl.runtime._runtime_params import ExperimentControlSettings, ExperimentDataSettings
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.onnx_convert import OnnxConverter
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.core import Run
from azureml.train.automl.runtime._automl_job_phases import PhaseUtil, \
    FeaturizationPhase, ExperimentPreparationPhase
from azureml.train.automl.runtime._entrypoints import entrypoint_util, featurization_entrypoint_util

from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: Optional[str],
        dataprep_json: str,
        entry_point: str,
        automl_settings: str,
        prep_type: str = PreparationRunTypeConstants.SETUP_ONLY,
        **kwargs: Any
) -> None:
    """
    Code for setup iterations for AutoML remote runs.
    """
    setup_run = Run.get_context()
    try:
        verifier = VerifierManager()
        parent_run, automl_settings_obj, cache_store = \
            entrypoint_util.init_wrapper(setup_run, automl_settings, script_directory, load_cache=False)
        experiment_observer = AzureExperimentObserver(parent_run)
        expr_store = ExperimentStore(cache_store, read_only=False)
        try:
            raw_experiment_data, feature_config_manager = \
                featurization_entrypoint_util.initialize_data(
                    setup_run, "setup", automl_settings_obj, script_directory, dataprep_json, entry_point,
                    parent_run.id, verifier)
        except Exception as e:
            # At this point, user datasets are not validated. Hence, known errors during splitting should be raised
            # with user error codes.
            common_data_validations.materialized_tabular_data_user_error_handler(e)

        featurization_entrypoint_util.cache_onnx_init_metadata(cache_store, raw_experiment_data, parent_run.id)

        feature_sweeped_state_container = ExperimentPreparationPhase.run(
            parent_run_id=parent_run.id,
            automl_settings=automl_settings_obj,
            cache_store=cache_store,
            current_run=setup_run,
            experiment_observer=experiment_observer,
            feature_config_manager=feature_config_manager,
            raw_experiment_data=raw_experiment_data,
            validate_training_data=True,
            verifier=verifier
        )

        # We will kick off a separate feature sweeping run, so we must save the artifacts necessary for that to
        # succeed.
        # These artifacts are also needed for code generation, so we need to save them even if the featurization
        # is done in the same run (if the artifacts are available).
        if feature_sweeped_state_container is not None:
            _save_setup_run_state_for_featurization_run(setup_run, feature_sweeped_state_container)

        if feature_sweeped_state_container is None or prep_type == PreparationRunTypeConstants.SETUP_ONLY:
            FeaturizationPhase.run(
                parent_run_id=parent_run.id,
                automl_settings=automl_settings_obj,
                cache_store=cache_store,
                current_run=setup_run,
                experiment_observer=experiment_observer,
                feature_config_manager=feature_config_manager,
                feature_sweeped_state_container=feature_sweeped_state_container,
                raw_experiment_data=raw_experiment_data,
                verifier=verifier
            )

            featurization_entrypoint_util._report_featurization_complete(experiment_observer, parent_run.id)

        # Write the current experiment store to the cache.
        expr_store.unload()

        parent_run_context = AzureAutoMLRunContext(parent_run)
        verifier.write_result_file(parent_run_context)
    except Exception as e:
        logger.error("AutoML setup script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(setup_run, e, update_run_properties=True)
        raise
    finally:
        # Reset the singleton for subsequent usage.
        ExperimentStore.reset()


def _save_setup_run_state_for_featurization_run(
    setup_run: Run,
    feature_sweeped_state_container: FeatureSweepedStateContainer
) -> None:
    logger.info("Saving artifacts required for separate featurization run.")

    feature_config = feature_sweeped_state_container.get_feature_config()

    save_feature_config(feature_config)
    save_engineered_feature_names(feature_sweeped_state_container.get_engineered_feature_names())

    featurization_properties = FeaturizationJsonParser._build_jsonifiable_featurization_props(
        feature_config)

    setup_run.add_properties({
        FeaturizationRunConstants.CONFIG_PROP: FeaturizationRunConstants.CONFIG_PATH,
        FeaturizationRunConstants.NAMES_PROP: FeaturizationRunConstants.NAMES_PATH,
        FeaturizationRunConstants.FEATURIZATION_JSON_PROP:
        FeaturizationRunConstants.FEATURIZATION_JSON_PATH})
    FeaturizationJsonParser.save_featurization_json(featurization_properties)
