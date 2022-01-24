# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Optional

from azureml.automl.core.shared import constants
from azureml.automl.runtime._data_definition import RawExperimentData

from azureml.automl.core._experiment_observer import ExperimentObserver
from azureml.automl.runtime import training_utilities, data_transformation
from azureml.automl.runtime._feature_sweeped_state_container import FeatureSweepedStateContainer
from azureml.automl.runtime.data_context import DataContextParams
from azureml.automl.core._run import RunType
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.onnx_convert import OnnxConverter
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.train.automl._automl_feature_config_manager import AutoMLFeatureConfigManager
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl.runtime._automl_job_phases.featurization_phase import FeaturizationPhase
from azureml.train.automl.runtime._automl_job_phases.utilities import PhaseUtil

logger = logging.getLogger(__name__)


class ExperimentPreparationPhase:
    """
    Setup job phase for the AutoML run. The setup phase initializes state variables used during the run.

    (For instance, depending on the run, the ONNX converter, dataset to use for training, or featurization info
    may be initialized.)
    """

    @staticmethod
    def run(
        parent_run_id: str,
        automl_settings: AzureAutoMLSettings,
        cache_store: CacheStore,
        current_run: RunType,
        experiment_observer: ExperimentObserver,
        feature_config_manager: AutoMLFeatureConfigManager,
        raw_experiment_data: RawExperimentData,
        validate_training_data: bool,
        verifier: VerifierManager
    ) -> Optional[FeatureSweepedStateContainer]:
        """Run the setup phase."""
        if validate_training_data:
            ExperimentPreparationPhase._validate_training_data(raw_experiment_data, automl_settings)
        logger.info('AutoML setup phase for run {}.'.format(current_run.id))

        feature_sweeping_config = feature_config_manager.get_feature_sweeping_config(
            enable_feature_sweeping=automl_settings.enable_feature_sweeping,
            parent_run_id=parent_run_id,
            task_type=automl_settings.task_type)

        logger.info("Checking if feature sweeping is necessary.")

        raw_data_context = PhaseUtil.build_raw_data_context(raw_experiment_data,
                                                            DataContextParams(automl_settings))

        # Set feature sweeping timeout to 1/4th of Experiment timeout.
        fesweep_timeout_sec = constants.AutoMLDefaultTimeouts.DEFAULT_FEATSWEEP_TIMEOUT_SECONDS  # type: int
        if automl_settings.experiment_timeout_minutes is not None:
            fesweep_timeout_sec = int(automl_settings.experiment_timeout_minutes * 60 / 4.0)

        feature_sweeped_state_container = data_transformation.get_transformers_for_full_featurization(
            raw_data_context,
            cache_store=cache_store,
            is_onnx_compatible=automl_settings.enable_onnx_compatible_models,
            experiment_observer=experiment_observer,
            enable_feature_sweeping=automl_settings.enable_feature_sweeping,
            verifier=verifier,
            enable_streaming=automl_settings.enable_streaming,
            feature_sweeping_config=feature_sweeping_config,
            enable_dnn=automl_settings.enable_dnn,
            force_text_dnn=automl_settings.force_text_dnn,
            feature_sweeping_timeout_seconds=fesweep_timeout_sec,
            enable_categorical_indicators=automl_settings.enable_categorical_indicators
        )

        return feature_sweeped_state_container

    @staticmethod
    def _build_and_initialize_onnx_converter(
        raw_experiment_data: RawExperimentData,
        enable_onnx_compatible_models: bool,
        enable_split_onnx_featurizer_estimator_models: bool,
        parent_run_id: str
    ) -> Optional[OnnxConverter]:
        if not enable_onnx_compatible_models:
            return None
        onnx_cvt = PhaseUtil.build_onnx_converter(enable_split_onnx_featurizer_estimator_models)
        if not onnx_cvt:
            return None
        logger.info('Initialize ONNX converter from input data during setup.')
        onnx_cvt.initialize_input(X=raw_experiment_data.X,
                                  x_raw_column_names=raw_experiment_data.feature_column_names,
                                  model_name=PhaseUtil.get_onnx_model_name(parent_run_id),
                                  model_desc=PhaseUtil.get_onnx_model_desc(parent_run_id))
        return onnx_cvt

    @staticmethod
    def _validate_training_data(
        raw_experiment_data: RawExperimentData,
        automl_settings: AzureAutoMLSettings,
    ) -> None:
        logger.info('Validating training data.')
        training_utilities._validate_user_experiment_data(raw_experiment_data, automl_settings)
        logger.info('Input data successfully validated.')
