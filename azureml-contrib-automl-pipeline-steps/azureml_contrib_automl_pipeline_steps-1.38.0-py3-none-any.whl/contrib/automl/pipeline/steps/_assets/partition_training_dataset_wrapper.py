# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import sys

from azureml.core import Run
from azureml.train.automl.constants import HTSConstants
from azureml.automl.core.shared._diagnostics.automl_events import RunSucceeded, RunFailed
from azureml.automl.core._logging.event_logger import EventLogger
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru
from azureml.automl.core._run import run_lifecycle_utilities
import azureml.train.automl.runtime._hts.tabular_dataset_partition as tdp


logger = logging.getLogger(__name__)


def partition_training_dataset_wrapper():
    """Wrapper codes for HTS partition training dataset."""
    current_step_run = Run.get_context()

    try:
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_PROPORTIONS_CALCULATION)
        arguments_dict = hru.get_arguments_dict(HTSConstants.STEP_DATASET_PARTITION)
        hru.init_logger(
            module=sys.modules[__name__], handler_name=__name__, custom_dimensions=custom_dim, run=current_step_run)
        event_logger = EventLogger(current_step_run)
        logger.info("Proportion calculation wrapper started.")
        tdp.tabular_dataset_partition(arguments_dict, event_logger, current_step_run)
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
        from azureml.train.automl.runtime._hts.tabular_dataset_partition import TabularDatasetPartitionWrapper
        runtime_wrapper = TabularDatasetPartitionWrapper(is_inference=False)
        runtime_wrapper.run()
    except ImportError:
        logger.warning("New script failed, using old script now.")
        partition_training_dataset_wrapper()
