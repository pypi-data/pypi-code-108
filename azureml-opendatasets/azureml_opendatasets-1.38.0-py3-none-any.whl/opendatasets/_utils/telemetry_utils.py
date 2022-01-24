# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import sys

from azureml.telemetry import get_telemetry_log_handler, INSTRUMENTATION_KEY
from azureml.telemetry.loggers import Loggers as _Loggers

"""Telemetry utils."""

OPENDATASETS_LOGGER_NAMESPACE = "azureml.opendatasets"
OPENDATASETS_INSTRUMENTATION_KEY = INSTRUMENTATION_KEY
OPENDATASETS_METRICS_LABEL_ENV_VAR = 'AZUREML_OPENDATASETS_METRICS_LABEL'
INSTRUMENTATION_KEY_KEY = _Loggers.INSTRUMENTATION_KEY_KEY

WORKSPACE_ID = "workspace_id"
WORKSPACE_NAME = "workspace_name"
WORKSPACE_LOCATION = "workspace_location"
SUBSCRIPTION_ID = "subscription_id"
PIPELINE_NAME = "pipeline_name"
PIPELINE_VERSION = "pipeline_version"
RUN_ID = "runid"
RESOURCEGROUP_NAME = "ResourceGroupName"
EXPERIMENT_NAME = "ExperimentName"
METRICS_LABEL = "MetricsLabel"
IS_SUBMITTED_RUN = "IsSubmittedRun"


def add_appinsights_log_handler(logger):
    handler = get_telemetry_log_handler(
        instrumentation_key=OPENDATASETS_INSTRUMENTATION_KEY,
        component_name=OPENDATASETS_LOGGER_NAMESPACE)
    add_handler(logger, handler)


def add_console_log_handler(logger):
    handler = logging.StreamHandler(sys.stdout)
    add_handler(logger, handler)


def get_opendatasets_logger(verbosity=logging.DEBUG):
    logger = logging.getLogger(OPENDATASETS_LOGGER_NAMESPACE)
    logger.propagate = False
    logger.setLevel(verbosity)
    add_console_log_handler(logger)
    return logger


def add_handler(logger, handler):
    """
    Add a logger handler and skip if the same type already exists.

    :param logger: Logger
    :param handler: handler instance
    """
    handler_type = type(handler)
    for log_handler in logger.handlers:
        if isinstance(log_handler, handler_type):
            return
    logger.addHandler(handler)


def get_run_common_properties():
    try:
        from azureml.core.run import Run, _SubmittedRun
    except ImportError:
        print("Import error for azureml.core.run!")
    run = Run.get_context()
    metrics_label = get_opendatasets_metrics_label()
    if isinstance(run, _SubmittedRun):
        context = run._experiment.workspace.service_context
        subscription_id = context.subscription_id
        resource_group_name = context.resource_group_name
        workspace_name = context.workspace_name
        experiment_name = run._experiment.name
        run_id = run._run_id
        return {
            IS_SUBMITTED_RUN: True,
            SUBSCRIPTION_ID: subscription_id,
            RESOURCEGROUP_NAME: resource_group_name,
            WORKSPACE_NAME: workspace_name,
            WORKSPACE_ID: workspace_name,
            EXPERIMENT_NAME: experiment_name,
            RUN_ID: run_id,
            METRICS_LABEL: metrics_label
        }
    else:
        return {
            IS_SUBMITTED_RUN: False,
            METRICS_LABEL: metrics_label
        }


def get_opendatasets_metrics_label():
    value = os.environ.get(OPENDATASETS_METRICS_LABEL_ENV_VAR)
    return value
