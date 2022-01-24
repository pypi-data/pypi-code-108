# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
import logging

from azureml.core import Run
from azureml.automl.core._run import run_lifecycle_utilities
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.train.automl.constants import HTSConstants
from azureml.automl.core.shared._diagnostics.automl_events import RunSucceeded, RunFailed
from azureml.automl.core._logging.event_logger import EventLogger
from azureml.train.automl.runtime._hts.proportions_calculation import proportions_calculation


logger = logging.getLogger(__name__)


def proportions_calculation_wrapper():
    """Wrapper code for HTS proportions calculation."""
    current_step_run = Run.get_context()

    try:
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_PROPORTIONS_CALCULATION)
        arguments_dict = hru.get_arguments_dict(HTSConstants.STEP_PROPORTIONS_CALCULATION)
        hru.init_logger(
            module=sys.modules[__name__], handler_name=__name__, custom_dimensions=custom_dim, run=current_step_run)
        event_logger = EventLogger(current_step_run)
        logger.info("Proportion calculation wrapper started.")
        proportions_calculation(arguments_dict, event_logger, script_run=current_step_run)
        logger.info("Proportion calculation wrapper completed.")
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
        from azureml.train.automl.runtime._hts.proportions_calculation import ProportionsCalculationWrapper
        runtime_wrapper = ProportionsCalculationWrapper()
        runtime_wrapper.run()
    except ImportError as ie:
        logger.warning("New script failed, using old script now.")
        proportions_calculation_wrapper()
