# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import os
from typing import Any, Dict, Optional, Union

from azureml.automl.runtime._data_definition import RawExperimentData
from scipy import sparse

from azureml._tracing._tracer_factory import get_tracer
from azureml.automl.core._experiment_observer import ExperimentObserver
from azureml.automl.core._run import RunType
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants, logging_utilities, reference_codes
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime import training_utilities
from azureml.automl.runtime._feature_sweeped_state_container import FeatureSweepedStateContainer
from azureml.automl.runtime._featurization_orchestration import orchestrate_featurization
from azureml.automl.runtime._runtime_params import ExperimentControlSettings, ExperimentDataSettings
from azureml.automl.runtime.data_context import TransformedDataContext, DataContextParams
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.streaming_data_context import StreamingTransformedDataContext
from azureml.core import Run
from azureml.train.automl._automl_feature_config_manager import AutoMLFeatureConfigManager

from azureml.train.automl.runtime import _problem_info_utils
from azureml.train.automl.runtime._automl_job_phases.utilities import PhaseUtil
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class FeaturizationPhase:
    """AutoML job phase that featurizes the data."""

    @staticmethod
    def run(
        parent_run_id: str,
        automl_settings: AutoMLBaseSettings,
        cache_store: CacheStore,
        current_run: RunType,
        experiment_observer: ExperimentObserver,
        feature_config_manager: AutoMLFeatureConfigManager,
        feature_sweeped_state_container: Optional[FeatureSweepedStateContainer],
        raw_experiment_data: RawExperimentData,
        verifier: VerifierManager
    ) -> None:
        """
        Run the featurization phase. This function assumes the data (raw_experiment_data) is already validated before.

        If featurization is enabled, data will be featurized. A data snapshot is taken to be used
        as input sample for inference. Problem info is set.

        Depending on the scenario, this phase will be called from a ParentRun, SetupRun, or FeaturizationRun.

        :param parent_run_id: The id of the current_run's parent.
        :param raw_experiment_data: Data inputs to the experiment.
        :param automl_settings: Object containing AutoML settings as specified by user.
        :param cache_store: The cache store.
        :param current_run: The current run.
        :param experiment_observer: The experiment observer.
        :param feature_config_manager: The feature config manager.
        :param feature_sweeped_state_container: The feature sweeped state container.
        :param verifier: The fault verifier manager.
        :return: None
        """
        # Transform raw input and save to cache store.
        logger.info("AutoML featurization for run {}.".format(current_run.id))

        with logging_utilities.log_activity(logger=logger, activity_name="Getting transformed data context."):
            # TODO: Make the caller pass in the RawDataContext into this method.
            raw_data_context = PhaseUtil.build_raw_data_context(raw_experiment_data,
                                                                DataContextParams(automl_settings))
            logger.info("Using {} for caching transformed data.".format(type(cache_store).__name__))
            with logging_utilities.log_activity(
                logger=logger,
                activity_name="Beginning full featurization logic."
            ):
                feature_sweeping_config = feature_config_manager.get_feature_sweeping_config(
                    enable_feature_sweeping=automl_settings.enable_feature_sweeping,
                    parent_run_id=parent_run_id,
                    task_type=automl_settings.task_type
                )

                # TODO: break down featurization span more
                with tracer.start_as_current_span(
                        constants.TelemetryConstants.SPAN_FORMATTING.format(
                            constants.TelemetryConstants.COMPONENT_NAME, constants.TelemetryConstants.FEATURIZATION
                        ),
                        user_facing_name=constants.TelemetryConstants.FEATURIZATION_USER_FACING
                ):
                    td_ctx = orchestrate_featurization(
                        automl_settings.enable_streaming,
                        automl_settings.is_timeseries,
                        automl_settings.path,
                        raw_data_context,
                        cache_store,
                        verifier,
                        experiment_observer,
                        feature_sweeping_config,
                        feature_sweeped_state_container
                    )

        Contract.assert_value(
            td_ctx,
            "transformed_data_context",
            reference_code=reference_codes.ReferenceCodes._FEATURIZATION_PHASE_MISSING_TDCTX,
            log_safe=True
        )

        logger.info("Setting problem info.")
        _problem_info_utils.set_problem_info(
            td_ctx.X,
            td_ctx.y,
            enable_subsampling=automl_settings.enable_subsampling or False,
            enable_streaming=automl_settings.enable_streaming,
            current_run=current_run,
            transformed_data_context=td_ctx,
            cache_store=cache_store,
            enable_categorical_indicators=automl_settings.enable_categorical_indicators
        )

        # Hack to prevent saving data transformer for continue experiment
        # In first experiment submission tags contain one element which is 'model_explain_run':'best_run'
        # Using this as a reference to prevent exception and e2e test failure
        if len(current_run.get_tags()) <= 1:
            # save data transformer using mlflow
            FeaturizationPhase._save_data_transformer(current_run, td_ctx, automl_settings)

        return training_utilities.build_experiment_store(
            transformed_data_context=td_ctx,
            cache_store=cache_store,
            task_type=automl_settings.task_type,
            experiment_data_settings=ExperimentDataSettings(automl_settings),
            init_all_stats=False,
            keep_in_memory=False,
            experiment_control_settings=ExperimentControlSettings(automl_settings))

    @staticmethod
    def _save_data_transformer(
            parent_run: RunType,
            td_ctx: Any,
            automl_settings: AutoMLBaseSettings) -> None:
        """
        Save data transformer in experiment's parent run artifact store

        :param parent_run: parent run of experiment
        :param td_ctx: data transformer context
        :param save_as_mlflow: whether to save transformer using mlflow
        """

        # fetch transformer
        if isinstance(td_ctx, StreamingTransformedDataContext):
            data_transformer = td_ctx.get_featurization_transformer()
        elif isinstance(td_ctx, TransformedDataContext):
            data_transformer = td_ctx.transformers[constants.Transformers.X_TRANSFORMER]
        else:
            logger.info("Not a valid data transformer")
            return

        model_outputs = {constants.MLFLOW_TRANSFORMER_PATH: data_transformer}

        parent_run_context = AzureAutoMLRunContext(parent_run)
        parent_run_context.batch_save_artifacts(
            working_directory=automl_settings.path,
            input_strs={},
            model_outputs=model_outputs,
            save_as_mlflow=automl_settings.save_mlflow,
            is_transformer=True)
