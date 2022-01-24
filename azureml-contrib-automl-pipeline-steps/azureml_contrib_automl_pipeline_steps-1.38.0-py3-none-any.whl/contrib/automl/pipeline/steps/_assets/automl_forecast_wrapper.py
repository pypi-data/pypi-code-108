# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from pathlib import Path
import os
from azureml.automl.core.shared import logging_utilities  # noqa: E402
from azureml.core import Run  # noqa: E402

import azureml.train.automl.runtime._hts.hts_runtime_utilities as hru  # noqa: E402
from azureml.train.automl._hts import hts_client_utilities as hcu  # noqa: E402
from azureml.train.automl.constants import HTSConstants  # noqa: E402
import azureml.train.automl.runtime._hts.hts_forecast_parallel as hfp  # noqa: E402
from azureml.train.automl.runtime._hts.hts_forecast_parallel import HTSForecastParallel  # noqa: E402
from azureml.automl.core.shared._diagnostics.automl_events import RunSucceeded, RunFailed  # noqa: E402
from azureml.automl.core._logging.event_logger import EventLogger  # noqa: E402
from azureml.automl.core._run import run_lifecycle_utilities  # noqa: E402
from azureml.train.automl.runtime._hts.hts_graph import Graph  # noqa: E402

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
logger = logging.getLogger(__name__)
current_step_run = None
arguments_dict = None
graph = None
node_columns_info = None
event_logger = None
custom_dim = {}
runtime_wrapper = None


def get_current_step_run(stagger=True):
    global current_step_run
    if current_step_run is None:
        if stagger:
            hru.stagger_randomized_secs(arguments_dict)
        current_step_run = Run.get_context()
    return current_step_run


def init():
    global arguments_dict
    global graph
    global node_columns_info
    global event_logger
    global custom_dim
    global runtime_wrapper
    print("init parallel forecast file wrapper.")
    try:
        runtime_wrapper = hfp.HTSForecastParallelWrapper(Path(__file__).parent.absolute())
        runtime_wrapper.init_prs()
        print("Forecast parallel init is done.")
    except AttributeError:
        logger.warning("Failed to use the new script, fall back to the old one now.")
        try:
            custom_dim = hru.get_additional_logging_custom_dim(HTSConstants.STEP_FORECAST)
            logger.info("Forecast parallel wrapper init started.")
            arguments_dict = hru.get_arguments_dict(HTSConstants.STEP_FORECAST, True)
            step_run = get_current_step_run()
            event_logger = EventLogger(run=current_step_run)
            event_log_dim = hru.get_event_logger_additional_fields(
                custom_dim, current_step_run.parent.id, script_type="init",
                should_emit=arguments_dict.get(HTSConstants.ENABLE_EVENT_LOGGER, "False"))
            hru.init_logger(
                path=str(Path(__file__).parent.absolute()),
                handler_name=__name__,
                custom_dimensions=custom_dim,
                verbosity=logging.WARNING,  # Set verbosity to warning as model featurization logs will be noisy
                run=step_run
            )
            # move this logic once we have a validation step on inference data.
            pipeline_run = hru.get_pipeline_run()
            training_run = hcu.get_training_run(
                arguments_dict[HTSConstants.TRAINING_RUN_ID], step_run.experiment, pipeline_run)
            pipeline_run.set_tags({HTSConstants.HTS_TAG_TRAINING_RUN_ID: training_run.id})
            logger.info("Using training run {} for inference.".format(training_run.id))
            graph = Graph.get_graph_from_artifacts(training_run, ".")
            node_columns_info = hru.get_node_columns_info_from_artifacts(training_run, ".")
            logger.info("Forecast parallel wrapper init completed.")
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
    if runtime_wrapper is not None:
        return runtime_wrapper.run_prs(prs_input)
    else:
        print(f'run method start: {__file__}, run({prs_input})')
        event_log_dim = hru.get_event_logger_additional_fields(
            custom_dim, current_step_run.parent.id, script_type="run",
            should_emit=arguments_dict.get(HTSConstants.ENABLE_EVENT_LOGGER, "False"))
        hts_forecast_parallel = HTSForecastParallel(
            get_current_step_run(False), Path(__file__).parent.absolute(), arguments_dict, event_log_dim,
            graph, node_columns_info
        )

        try:
            logger.info("Data aggregation wrapper started.")
            result_df = hts_forecast_parallel.run(prs_input)
            event_logger.log_event(RunSucceeded(current_step_run.id, event_log_dim))
        except Exception as e:
            logging_utilities.log_traceback(e, logger)
            error_code, error_str = run_lifecycle_utilities._get_error_code_and_error_str(e)
            event_logger.log_event(RunFailed(current_step_run.id, error_code, error_str, event_log_dim))
            raise

        return result_df
