# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
from typing import Any, Dict, Optional

from azureml._tracing import get_tracer
from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.train.automl._azure_experiment_observer import AzureExperimentObserver
from azureml.automl.runtime.data_context import DataContextParams

from azureml.automl.core._experiment_observer import ExperimentObserver
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.constants import FeaturizationRunConstants
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime import data_transformation, faults_verifier
from azureml.automl.runtime._data_transformation_utilities import FeaturizationJsonParser
from azureml.automl.runtime._feature_sweeped_state_container import FeatureSweepedStateContainer
from azureml.automl.runtime._runtime_params import ExperimentControlSettings, ExperimentDataSettings
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.core import Run
from azureml.train.automl._automl_feature_config_manager import AutoMLFeatureConfigManager
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases import FeaturizationPhase, PhaseUtil
from azureml.train.automl.runtime._entrypoints import entrypoint_util, featurization_entrypoint_util

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: Optional[str],
        dataprep_json: str,
        entry_point: str,
        automl_settings: str,
        setup_container_id: str,
        featurization_json: str,
        **kwargs: Any) -> None:
    """
    Code for featurization part of setup iterations for AutoML remote runs.
    """
    featurization_run = Run.get_context()
    try:
        parent_run, automl_settings_obj, cache_store = entrypoint_util.init_wrapper(
            featurization_run, automl_settings, script_directory)
        expr_store = ExperimentStore(cache_store, read_only=False)
        expr_store.load()
        property_dict = featurization_run.get_properties()
        featurization_entrypoint_util.transfer_files_from_setup(
            featurization_run, setup_container_id,
            property_dict.get(FeaturizationRunConstants.CONFIG_PROP,
                              FeaturizationRunConstants.CONFIG_PATH),
            property_dict.get(FeaturizationRunConstants.NAMES_PROP,
                              FeaturizationRunConstants.NAMES_PATH))
        experiment_observer = AzureExperimentObserver(parent_run)
        raw_experiment_data, feature_config_manager = \
            featurization_entrypoint_util.initialize_data(
                featurization_run, "featurization", automl_settings_obj, script_directory, dataprep_json,
                entry_point, parent_run.id)
        # The setup run has produced information about the featurizers that will be run on the dataset.
        # This information is encapsulated in FeatureSweepedStateContainer. We need to
        # rehyrdrate a FeatureSweepedStateContainer from state saved by the setup run.
        feature_sweeped_state_container = _build_feature_sweeped_state_container(
            parent_run, featurization_json, raw_experiment_data, automl_settings_obj, feature_config_manager,
            cache_store, experiment_observer)
        verifier = faults_verifier.VerifierManager()
        FeaturizationPhase.run(
            parent_run_id=parent_run.id,
            automl_settings=automl_settings_obj,
            cache_store=cache_store,
            current_run=featurization_run,
            experiment_observer=experiment_observer,
            feature_config_manager=feature_config_manager,
            feature_sweeped_state_container=feature_sweeped_state_container,
            raw_experiment_data=raw_experiment_data,
            verifier=verifier
        )
        # Write the current experiment store to the cache and reset the singleton for subsequent usage.
        expr_store.unload()
        featurization_entrypoint_util._report_featurization_complete(experiment_observer, parent_run.id)
    except Exception as e:
        logger.error("AutoML featurization script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(featurization_run, e, update_run_properties=True)
        raise
    finally:
        ExperimentStore.reset()


def _build_feature_sweeped_state_container(
        parent_run: Run,
        featurization_json: str,
        raw_experiment_data: RawExperimentData,
        automl_settings: AzureAutoMLSettings,
        feature_config_manager: AutoMLFeatureConfigManager,
        cache_store: CacheStore,
        experiment_observer: ExperimentObserver,
) -> FeatureSweepedStateContainer:
    featurizer_container = FeaturizationJsonParser.parse_featurizer_container(featurization_json)
    raw_data_context = PhaseUtil.build_raw_data_context(raw_experiment_data, DataContextParams(automl_settings))
    feature_sweeping_config = feature_config_manager.get_feature_sweeping_config(
        enable_feature_sweeping=automl_settings.enable_feature_sweeping,
        parent_run_id=parent_run.id,
        task_type=automl_settings.task_type)
    feature_sweeped_state_container = data_transformation.build_feature_sweeped_state_container(
        raw_data_context,
        cache_store=cache_store,
        is_onnx_compatible=automl_settings.enable_onnx_compatible_models,
        experiment_observer=experiment_observer,
        enable_feature_sweeping=automl_settings.enable_feature_sweeping,
        feature_sweeping_config=feature_sweeping_config,
        enable_dnn=automl_settings.enable_dnn,
        force_text_dnn=automl_settings.force_text_dnn,
        featurizer_container=featurizer_container,
        enable_categorical_indicators=automl_settings.enable_categorical_indicators)
    return feature_sweeped_state_container
