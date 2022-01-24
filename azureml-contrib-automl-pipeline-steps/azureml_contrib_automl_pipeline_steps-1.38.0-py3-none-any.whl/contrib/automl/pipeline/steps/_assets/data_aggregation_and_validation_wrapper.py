# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging  # noqa: E402
from pathlib import Path  # noqa: E402
import os
from azureml.core import Run  # noqa: E402
from azureml.automl.core.shared import logging_utilities  # noqa: E402
from azureml.train.automl.constants import HTSConstants  # noqa: E402
from azureml.train.automl.runtime._hts.hts_data_aggregation import HTSDataAggregation  # noqa: E402
from azureml.automl.core.shared._diagnostics.automl_events import RunSucceeded, RunFailed  # noqa: E402
from azureml.automl.core._logging.event_logger import EventLogger  # noqa: E402
from azureml.automl.core._run import run_lifecycle_utilities  # noqa: E402
import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru  # noqa: E402
from azureml.train.automl.runtime._hts.hts_graph import Graph  # noqa: E402
import azureml.train.automl.runtime._hts.hts_data_aggregation as hda  # noqa: E402


# Clearing this environment variable avoids periodic calls from
# dprep log uploading to Run.get_context() and cause RH throttling
# when running at scale. It looks like this logging path repeatedly uploads timespan
# tracing data to the PRS step itself from each worker.
os.environ['AZUREML_OTEL_EXPORT_RH'] = ''

# Batch / flush metrics in the many models scenario
os.environ["AZUREML_METRICS_POLLING_INTERVAL"] = '30'

# Once the metrics service has uploaded & queued metrics for processing, we don't
# need to wait for those metrics to be ingested on flush.
os.environ['AZUREML_FLUSH_INGEST_WAIT'] = ''
logger = logging.getLogger(__name__)
current_step_run = None
dstore = None
event_logger = None
settings = None
graph = None
arguments_dict = None
custom_dim = {}
runtime_wrapper = None


def get_current_step_run(stagger=True):
    global current_step_run
    global dstore
    if current_step_run is None:
        if stagger:
            hru.stagger_randomized_secs(arguments_dict)
        current_step_run = Run.get_context()
    return current_step_run


def init():
    global arguments_dict
    global graph
    global event_logger
    global dstore
    global custom_dim
    global runtime_wrapper
    try:
        runtime_wrapper = hda.HTSDataAggregationWrapper(Path(__file__).parent.absolute())
        runtime_wrapper.init_prs()
        print("Data aggregation step init is done.")
    except AttributeError:
        logger.warning("Failed to use the new script, fall back to the old one now.")
        try:
            custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_DATA_AGGREGATION_FILEDATASET)
            arguments_dict = hru.get_arguments_dict(HTSConstants.STEP_DATA_AGGREGATION, True)
            step_run = get_current_step_run(True)
            event_logger = EventLogger(run=current_step_run)
            event_log_dim = hru.get_event_logger_additional_fields(
                custom_dim, current_step_run.parent.id, script_type="init",
                should_emit=arguments_dict.get(HTSConstants.ENABLE_EVENT_LOGGER, "False"))
            print("init data aggregation for file dataset")
            hru.init_logger(
                path=str(Path(__file__).parent.absolute()), handler_name=__name__, custom_dimensions=custom_dim,
                run=step_run)
            print("Data aggregation wrapper for file dataset init started.")
            graph = Graph.get_graph_from_file(arguments_dict[HTSConstants.HTS_GRAPH])
            print("Data aggregation wrapper for file dataset init completed.")
            event_logger.log_event(RunSucceeded(current_step_run.id, event_log_dim))
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            # we should let PRS to handle the run failure in this case.
            if event_logger is None:
                event_logger = EventLogger(current_step_run)
            error_code, error_str = run_lifecycle_utilities._get_error_code_and_error_str(e)
            event_logger.log_event(RunFailed(current_step_run.id, error_code, error_str, event_log_dim))
            raise


def run(prs_input):
    global runtime_wrapper

    if runtime_wrapper is not None:
        result_list = runtime_wrapper.run_prs(prs_input)
        print("wrapper run is done.")
        return result_list
    else:
        event_log_dim = hru.get_event_logger_additional_fields(
            custom_dim, current_step_run.parent.id, script_type="run",
            should_emit=arguments_dict.get(HTSConstants.ENABLE_EVENT_LOGGER, "False"))
        hts_data_agg = HTSDataAggregation(
            get_current_step_run(False), Path(__file__).parent.absolute(), arguments_dict, event_log_dim, graph)

        try:
            logger.info("Data aggregation wrapper started.")
            result_list = hts_data_agg.run(prs_input)
            event_logger.log_event(RunSucceeded(current_step_run.id, event_log_dim))
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            error_code, error_str = run_lifecycle_utilities._get_error_code_and_error_str(e)
            event_logger.log_event(RunFailed(current_step_run.id, error_code, error_str, event_log_dim))
            raise

        return result_list
