# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging
from datetime import datetime
from typing import Any, List

from azureml._tracing import get_tracer
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.core import Run
from azureml.train.automl import _logging   # type: ignore
from azureml.train.automl._constants_azureml import CodePaths
from azureml.train.automl.runtime._automl_job_phases import BatchTrainingPhase, TrainingIterationParams
from azureml.train.automl.runtime._entrypoints import entrypoint_util, training_entrypoint_util

logger = logging.getLogger(__name__)
activity_logger = TelemetryActivityLogger()
tracer = get_tracer(__name__)


def execute(
        script_directory: str,
        automl_settings: str,
        dataprep_json: str,
        child_run_ids: List[str],
        **kwargs: Any
) -> None:
    """
    Driver script that runs given child runs that contain pipelines
    """
    batch_job_run = Run.get_context()  # current batch job context

    try:
        print("{} - INFO - Beginning batch driver wrapper.".format(datetime.now().__format__('%Y-%m-%d %H:%M:%S,%f')))
        logger.info('Beginning AutoML remote batch driver for {}.'.format(batch_job_run.id))

        parent_run, automl_settings_obj, cache_store = entrypoint_util.init_wrapper(
            batch_job_run, automl_settings, script_directory, code_path=CodePaths.BATCH_REMOTE, **kwargs)

        if automl_settings_obj.enable_streaming:
            entrypoint_util.modify_settings_for_streaming(automl_settings_obj, dataprep_json)

        expr_store = ExperimentStore(cache_store, read_only=True)
        expr_store.load()
        onnx_cvt = training_entrypoint_util.load_onnx_converter(automl_settings_obj, cache_store, parent_run.id)

        # Run training for given child run IDs for this batch
        BatchTrainingPhase.run(
            automl_parent_run=parent_run,
            child_run_ids=child_run_ids,
            automl_settings=automl_settings_obj,
            onnx_cvt=onnx_cvt
        )

        # Set back child run id for logging
        _logging.set_run_custom_dimensions(
            automl_settings=automl_settings_obj,
            parent_run_id=parent_run.id,
            child_run_id=batch_job_run.id,
            code_path=CodePaths.BATCH_REMOTE
        )

        logger.info("No more training iteration task in the queue, ending the script run for {}"
                    .format(batch_job_run.id))

    except Exception as e:
        logger.error("AutoML batch_driver_wrapper script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(batch_job_run, e)
        raise
    finally:
        # Reset the singleton for subsequent usage.
        ExperimentStore.reset()
