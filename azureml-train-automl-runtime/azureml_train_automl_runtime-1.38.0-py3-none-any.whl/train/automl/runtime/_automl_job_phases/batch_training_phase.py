# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import List, Optional

from azureml._common._error_definition import AzureMLError
from azureml._restclient.constants import RunStatus
from azureml._tracing import get_tracer
from azureml.core import Run

from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import RunInterrupted
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings
from azureml.automl.core.shared.constants import TelemetryConstants
from azureml.automl.runtime.fit_output import FitOutput, _FitOutputUtils
from azureml.automl.runtime.onnx_convert import OnnxConverter
from azureml.train.automl import _logging  # type: ignore
from azureml.train.automl._azureautomlsettings import AzureAutoMLSettings
from azureml.train.automl._constants_azureml import CodePaths
from azureml.train.automl.runtime._automl_job_phases.training_iteration_phase import (
    TrainingIterationParams,
    TrainingIterationPhase,
)
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
from azureml.train.automl.runtime._code_generation.utilities import generate_model_code_and_notebook

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


class BatchTrainingPhase:
    """Batch training for child iterations"""

    @staticmethod
    def run(
        automl_parent_run: Run,
        child_run_ids: List[str],
        automl_settings: AzureAutoMLSettings,
        onnx_cvt: Optional[OnnxConverter],
    ) -> None:
        """
        BatchTrainingPhase
        Run training iterations for given child run ids
        :param automl_parent_run: AutoML parent run context
        :param child_run_ids: List of child run ids to train
        :param automl_settings: AutoMl settings for current run
        :param dataset: Dataset used for the run
        :param onnx_cvt: ONNX converter if run requires ONNX compatible model
        :return:
        """
        fit_output = None  # type: Optional[FitOutput]
        with tracer.start_as_current_span(
            TelemetryConstants.SPAN_FORMATTING.format(
                TelemetryConstants.COMPONENT_NAME, TelemetryConstants.BATCH_TRAINING
            ),
            user_facing_name=TelemetryConstants.BATCH_TRAINING_USER_FACING,
        ):
            for child_run_id in child_run_ids:
                try:
                    _logging.set_run_custom_dimensions(
                        automl_settings=automl_settings,
                        parent_run_id=automl_parent_run.id,
                        child_run_id=child_run_id,
                        code_path=CodePaths.BATCH_REMOTE,
                    )
                    child_run = Run(automl_parent_run.experiment, child_run_id)
                    logger.info("Starting child run {}".format(child_run_id))

                    child_run_status = child_run.get_status()
                    if child_run_status != RunStatus.NOT_STARTED:
                        # This could happen when the node that was processing this batch run was preempted or failed
                        # and the batch script was submitted again.
                        if child_run_status not in RunStatus.get_running_statuses():
                            # Skip all the runs that have already reached completed running
                            logger.info("Child run {} already processed, skipping the run".format(child_run_id))
                        else:
                            # Cancel the run that was in running state before node failed
                            logger.info("Marking child run {} as canceled".format(child_run_id))
                            try:
                                run_lifecycle_utilities.cancel_run(
                                    child_run, cancel_reason=AzureMLError.create(RunInterrupted).error_message
                                )
                            except Exception:
                                logger.error("Error while marking child run {} as canceled".format(child_run_id))
                        continue

                    run_lifecycle_utilities.start_run(child_run)

                    properties = child_run.get_properties()
                    pipeline_id = properties["pipeline_id"]
                    pipeline_spec = properties["pipeline_spec"]
                    training_percent = float(properties.get("training_percent") or 100)

                    automl_run_context = AzureAutoMLRunContext(child_run)
                    automl_run_context.set_local(False)

                    fit_output = TrainingIterationPhase.run(
                        automl_parent_run=automl_parent_run,
                        automl_run_context=automl_run_context,
                        training_iteration_params=TrainingIterationParams(automl_settings),
                        onnx_cvt=onnx_cvt,
                        pipeline_id=pipeline_id,
                        pipeline_spec=pipeline_spec,
                        training_percent=training_percent,
                    )

                    if automl_settings.enable_code_generation:
                        generate_model_code_and_notebook(child_run, pipeline=fit_output.fitted_pipeline)

                    logger.info("Completing child run {}".format(child_run_id))
                    _FitOutputUtils.terminate_child_run(child_run, fit_output=fit_output)
                    logger.info("Completed child run {}".format(child_run_id))
                except Exception as e:
                    if fit_output is not None and fit_output._hit_experiment_timeout:
                        run_lifecycle_utilities.cancel_run(
                            child_run, warning_string=AutoMLErrorStrings.EXPERIMENT_TIMED_OUT
                        )
                    else:
                        if child_run:
                            logger.error("Error while running child iteration {}.".format(child_run_id))
                            run_lifecycle_utilities.fail_run(child_run, e)
                        else:
                            logger.error("Failed to create a child run.")
                            logging_utilities.log_traceback(e, logger)
