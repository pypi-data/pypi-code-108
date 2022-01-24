# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
import os
import logging


# Clearing this environment variable avoids periodic calls from
# dprep log uploading to Run.get_context() and cause RH throttling
# when running at scale. It looks like this logging path repeatedly uploads timespan
# tracing data to the PRS step itself from each worker.
os.environ["AZUREML_OTEL_EXPORT_RH"] = ""

# Batch / flush metrics in the many models scenario
os.environ["AZUREML_METRICS_POLLING_INTERVAL"] = '30'

# Once the metrics service has uploaded & queued metrics for processing, we don't
# need to wait for those metrics to be ingested on flush.
os.environ['AZUREML_FLUSH_INGEST_WAIT'] = ''


from azureml.automl.core.shared import logging_utilities  # noqa: E402
from azureml.core import Run  # noqa: E402

import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru  # noqa: E402
import azureml.train.automl._hts.hts_client_utilities as cu  # noqa: E402
from azureml.train.automl.constants import HTSConstants  # noqa: E402
from azureml.train.automl.runtime._hts.hts_automl_train import HTSAutoMLTrain  # noqa: E402
from azureml.automl.core.shared._diagnostics.automl_events import RunSucceeded, RunFailed  # noqa: E402
from azureml.automl.core._logging.event_logger import EventLogger  # noqa: E402
from azureml.automl.core._run import run_lifecycle_utilities  # noqa: E402
from azureml.train.automl.runtime._hts.hts_graph import Graph  # noqa: E402
import azureml.train.automl.runtime._hts.hts_automl_train as hat  # noqa: E402


logger = logging.getLogger(__name__)

current_step_run = None
event_logger = None
settings = None
graph = None
arguments_dict = None
# Whether or not this driver has been initialized
driver_initialized = False
custom_dim = {}
runtime_wrapper = None


def get_current_step_run(stagger=True):
    global current_step_run
    if current_step_run is None:
        if stagger:
            hru.stagger_randomized_secs(arguments_dict)
        current_step_run = Run.get_context()
    return current_step_run


def _initialize_driver():
    global arguments_dict
    global graph
    global settings
    global event_logger
    global custom_dim

    try:
        working_dir = Path(__file__).parent.absolute()
        arguments_dict = hru.get_arguments_dict(HTSConstants.STEP_AUTOML_TRAINING, True)
        custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_AUTOML_TRAINING)
        step_run = get_current_step_run(True)
        hru.init_logger(
            path=str(working_dir), handler_name=__name__, custom_dimensions=custom_dim,
            run=step_run
        )
        event_logger = EventLogger(run=current_step_run)
        event_log_dim = hru.get_event_logger_additional_fields(
            custom_dim, current_step_run.parent.id, script_type="init",
            should_emit=arguments_dict.get(HTSConstants.ENABLE_EVENT_LOGGER, "False"))
        print("AutoML training wrapper init started.")
        graph = Graph.get_graph_from_file(arguments_dict[HTSConstants.HTS_GRAPH])

        settings = cu.get_settings_dict(working_dir)

        print("AutoML training wrapper init completed.")
        event_logger.log_event(RunSucceeded(current_step_run.id, event_log_dim))
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        # we should let PRS to handle the run failure in this case.
        if event_logger is None:
            event_logger = EventLogger(current_step_run)
        error_code, error_str = run_lifecycle_utilities._get_error_code_and_error_str(e)
        event_logger.log_event(RunFailed(current_step_run.id, error_code, error_str, event_log_dim))
        raise


def run(mini_batches):
    # Initiailze the driver when the first mini batch runs.
    # (This is done because the initialize call requires a sleep call to stagger new traffic ramp-up (refer to
    # the initialize method for more info). There can be a large time gap between calls to the PRS in-built init()
    # methods and the in-built run methods. For example, for large datasets, it seems possible for PRS to invoke
    # the init() methods of all workers, and then 15 minutes later, invoke the run methods of all workers. Given that,
    # the sleep call to stagger traffic ramp-up won't work as expected if invoked in the PRS in-built init() method.)
    global runtime_wrapper
    global driver_initialized
    try:
        if runtime_wrapper is None:
            runtime_wrapper = hat.HTSAutoMLTrainWrapper(Path(__file__).parent.absolute())
            runtime_wrapper.init_prs()
        result_list = runtime_wrapper.run_prs(mini_batches)
        print("AutoML train step init is done.")
        return result_list
    except AttributeError:
        logger.warning("Failed to use the new script, fall back to the old one now.")
        if not driver_initialized:
            _initialize_driver()
            driver_initialized = True

        event_log_dim = hru.get_event_logger_additional_fields(
            custom_dim, current_step_run.parent.id, script_type="run",
            should_emit=arguments_dict.get(HTSConstants.ENABLE_EVENT_LOGGER, "False"))

        hts_automl_train = HTSAutoMLTrain(
            get_current_step_run(False), Path(__file__).parent.absolute(), settings,
            arguments_dict, event_log_dim, graph
        )

        try:
            result_list = hts_automl_train.run(mini_batches)
            event_logger.log_event(RunSucceeded(current_step_run.id, event_log_dim))
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            error_code, error_str = run_lifecycle_utilities._get_error_code_and_error_str(e)
            event_logger.log_event(RunFailed(current_step_run.id, error_code, error_str, event_log_dim))
            raise

        return result_list
