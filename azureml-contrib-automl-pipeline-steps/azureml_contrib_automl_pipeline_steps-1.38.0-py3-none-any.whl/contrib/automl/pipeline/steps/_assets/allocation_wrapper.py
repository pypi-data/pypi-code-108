# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
import logging

from azureml.core import Run
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.train.automl.runtime._hts.allocation import allocation_driver
from azureml.automl.core.shared._diagnostics.automl_events import RunSucceeded, RunFailed
from azureml.automl.core._logging.event_logger import EventLogger
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.train.automl.constants import HTSConstants


logger = logging.getLogger(__name__)


def allocation_wrapper():
    """Wrapper code for HTS allocation step."""
    current_step_run = Run.get_context()

    try:
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_ALLOCATION)
        hru.init_logger(sys.modules[__name__], __name__, custom_dimensions=custom_dim, run=current_step_run)
        arguments_dict = hru.get_arguments_dict(HTSConstants.STEP_ALLOCATION, True)
        event_logger = EventLogger(current_step_run)
        logger.info("Allocation wrapper started.")
        allocation_driver(current_step_run, arguments_dict, event_logger)
        logger.info("Allocation wrapper completed.")
        event_logger.log_event(RunSucceeded(
            current_step_run.id, hru.get_event_logger_additional_fields(custom_dim, current_step_run.parent.id)))
    except Exception as e:
        error_code, error_str = run_lifecycle_utilities._get_error_code_and_error_str(e)
        failure_event = RunFailed(
            run_id=current_step_run.id, error_code=error_code, error=error_str,
            additional_fields=hru.get_event_logger_additional_fields(custom_dim, current_step_run.parent.id))
        run_lifecycle_utilities.fail_run(current_step_run, e, failure_event=failure_event)
        raise


if __name__ == "__main__":
    try:
        from azureml.train.automl.runtime._hts.allocation import AllocationWrapper
        runtime_wrapper = AllocationWrapper()
        runtime_wrapper.run()
    except ImportError:
        logger.warning("New script failed, using old script now.")
        allocation_wrapper()
