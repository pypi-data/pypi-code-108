# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Any, Dict, Optional

from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime import fit_pipeline as fit_pipeline_helper
from azureml.automl.runtime._runtime_params import ExperimentControlSettings, ExperimentResourceSettings, \
    ExperimentOrchestrationSettings, PipelineSelectionSettings, ExperimentDataSettings
from azureml.automl.runtime.automl_pipeline import AutoMLPipeline
from azureml.automl.runtime.automl_run_context import AutoMLAbstractRunContext
from azureml.automl.runtime.fit_output import FitOutput
from azureml.automl.runtime.onnx_convert import OnnxConverter
from azureml.core import Run
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings

logger = logging.getLogger(__name__)


class TrainingIterationParams:

    def __init__(self, automl_settings: AzureAutoMLSettings):
        self.n_cross_validations = automl_settings.n_cross_validations

        self.control_settings = ExperimentControlSettings(automl_settings)
        self.data_settings = ExperimentDataSettings(automl_settings)
        self.resource_settings = ExperimentResourceSettings(automl_settings)
        self.pipeline_selection_settings = PipelineSelectionSettings(automl_settings)
        self.orchestration_settings = ExperimentOrchestrationSettings(automl_settings)


class TrainingIterationPhase:
    """Iteration that outputs a fully trained ML model."""

    @staticmethod
    def run(
        automl_parent_run: Run,
        automl_run_context: AutoMLAbstractRunContext,
        training_iteration_params: TrainingIterationParams,
        onnx_cvt: Optional[OnnxConverter],
        pipeline_id: str,
        pipeline_spec: str,
        training_percent: float,
        elapsed_time: Optional[int] = None
    ) -> FitOutput:
        """Run the training iteration."""
        logger.info('Beginning the training iteration for run {}.'.format(automl_run_context.run_id))

        automl_pipeline = AutoMLPipeline(automl_run_context, pipeline_spec, pipeline_id, training_percent / 100)

        # Dataset will have a valid value for # of CV splits if we were to do auto CV.
        # Set the value of n_cross_validations in AutoML settings if that were the case.
        # In the case of lazy data (streaming scenarios) we will return len 0.
        if training_iteration_params.n_cross_validations is None:
            expr_store = ExperimentStore.get_instance()
            n_cv = len(expr_store.data.materialized.cv_splits)
            logger.info("Number of cross-validations in dataset is {}.".format(n_cv))
            training_iteration_params.n_cross_validations = None if n_cv == 0 else n_cv

        fit_output = fit_pipeline_helper.fit_pipeline(
            automl_pipeline=automl_pipeline,
            control_settings=training_iteration_params.control_settings,
            data_settings=training_iteration_params.data_settings,
            resource_settings=training_iteration_params.resource_settings,
            pipeline_selection_settings=training_iteration_params.pipeline_selection_settings,
            orchestration_settings=training_iteration_params.orchestration_settings,
            automl_run_context=automl_run_context,
            onnx_cvt=onnx_cvt,
            elapsed_time=elapsed_time)

        if not fit_output.errors:
            primary_metric = fit_output.primary_metric
            score = fit_output.score
            duration = fit_output.actual_time
            logger.info('Child run completed with {}={} after {} seconds.'.format(primary_metric, score, duration))

        return fit_output
