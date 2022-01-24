# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for telemetry utilities."""

import json
import logging
import logging.handlers
import uuid
from datetime import datetime

COMPONENT_NAME = 'azureml.synapse'
DEFAULT_LOGGER_NAME = 'default'

try:
    import azureml.synapse
    azureml_synapse_version = azureml.synapse.__version__
except Exception:
    azureml_synapse_version = ''

default_custom_dimensions = {
    'azureml_synapse_version': azureml_synapse_version
}

try:
    from azureml.telemetry import AML_INTERNAL_LOGGER_NAMESPACE, INSTRUMENTATION_KEY
    from azureml.telemetry.activity import ActivityLoggerAdapter
    from azureml.telemetry.logging_handler import AppInsightsLoggingHandler

    telemetry_enabled = True
except Exception:
    telemetry_enabled = False
    AML_INTERNAL_LOGGER_NAMESPACE = "root"


def set_workspace(workspace):
    """Set some default dimensions based on the given AML workspace."""
    if workspace is None:
        default_custom_dimensions.update(
            {"subscription_id": None, "resource_group": None, "workspace_name": None, "workspace_id": None,
             "location": None})
    else:
        default_custom_dimensions.update(
            {"subscription_id": workspace._subscription_id,
             "resource_group": workspace._resource_group,
             "workspace_name": workspace._workspace_name,
             "location": workspace._location})


def set_compute(synapse_workspace, sparkpool, resource_id=None):
    """Set some default dimensions based on the given Synapse workspace and Spark pool name."""
    default_custom_dimensions.update(
        {"synapse_workspace": synapse_workspace,
         "synapse_sparkpool": sparkpool,
         "synapse_resource_id": resource_id})


def set_client(client_type, client_id):
    """Set default dimensions for client_type and client_id."""
    client_type_version = ''
    try:
        if client_type == "JupyterLab":
            client_type_version = _get_jupyterlab_version()
        elif client_type == "Jupyter":
            client_type_version = _get_jupyternotebook_version()
    finally:
        default_custom_dimensions.update(
            {"client_type": client_type, "client_type_version": client_type_version, "client_id": client_id}
        )


def set_synapse_session_guid(synapse_session_guid):
    """ Set synapse session guid."""
    default_custom_dimensions.update({"synapse_session_guid": synapse_session_guid})


def remove_synapse_session_guid():
    """ Remove synapse session guid from default custom dimensions."""
    default_custom_dimensions.pop("synapse_session_guid", None)


def _get_jupyterlab_version() -> str:
    import jupyterlab
    return jupyterlab.__version__


def _get_jupyternotebook_version() -> str:
    import notebook
    return notebook.__version__


def _get_logger(name=DEFAULT_LOGGER_NAME, verbosity=logging.DEBUG):
    logger = logging.getLogger(AML_INTERNAL_LOGGER_NAMESPACE + ".synapse").getChild(name)
    # fix the bug that logging is stopped after session restart, refer
    # https://stackoverflow.com/questions/28694540/python-default-logger-disabled for detail
    logger.disabled = False
    logger.propagate = False
    logger.setLevel(verbosity)
    if telemetry_enabled:
        if not _found_handler(logger, AppInsightsLoggingHandler):
            logger.addHandler(AppInsightsLoggingHandler(INSTRUMENTATION_KEY, logger))

    return logger


def _found_handler(logger, handler_type):
    for log_handler in logger.handlers:
        if isinstance(log_handler, handler_type):
            return True

    return False


def flush(logger_name):
    """Flush logs for a given logger."""
    logger = _get_logger(logger_name)
    for log_handler in logger.handlers:
        try:
            log_handler.flush()
        except Exception:
            pass


def log_telemetry(message, custom_dimensions=None, logger_name=DEFAULT_LOGGER_NAME, is_error=False):
    """Log message or error."""
    logger = _get_logger(logger_name)
    custom_dimensions = custom_dimensions or {}
    custom_dimensions.update(default_custom_dimensions)

    if telemetry_enabled:
        if is_error:
            ActivityLoggerAdapter(logger, custom_dimensions).error(message)
        else:
            ActivityLoggerAdapter(logger, custom_dimensions).info(message)
    else:
        if is_error:
            logger.error('Message: {}\nPayload: {}'.format(message, json.dumps(custom_dimensions)))
        else:
            logger.info('Message: {}\nPayload: {}'.format(message, json.dumps(custom_dimensions)))


def _exec_fun(func, args=(), **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        raise e


def get_aml_workspace_details():
    """Get the default dimensions."""
    return default_custom_dimensions


def log_activity(activity_name, custom_dimensions=None, logger_name=DEFAULT_LOGGER_NAME, func=None, args=(), **kwargs):
    """Execute a function and log the start, complete and errors.

    :param activity_name: the name of the activity
    :param custom_dimensions: some custom dimensions included in the telemetry
    :param logger_name: name of the logger
    :param func: the function to be executed
    :param args: the args for the function
    :param kwargs: the kwargs for the function
    """
    # the log_activity decorator has some bugs in multi-threading scenario, so change to this "ugly" style
    custom_dimensions = custom_dimensions or {}
    activity_info = dict(activity_id=str(uuid.uuid4()), activity_name=activity_name)
    activity_info.update(default_custom_dimensions)
    activity_info.update(custom_dimensions)

    if callable(func):
        if not telemetry_enabled:
            try:
                _exec_fun(func, args, **kwargs)
            except Exception as e:
                raise e
        else:
            activityLogger = ActivityLoggerAdapter(_get_logger(logger_name + ".start"), activity_info)
            activityLogger.info("{}.STARTED".format(activity_name))
            start_time = datetime.utcnow()
            completion_status = "SUCCEEDED"
            exception = None
            try:
                _exec_fun(func, args, **kwargs)
            except Exception as e:
                exception = e
                completion_status = "FAILED"
                raise
            finally:
                end_time = datetime.utcnow()
                duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)
                activity_info["completionStatus"] = completion_status
                activity_info["durationMs"] = duration_ms
                activity_info.update(default_custom_dimensions)
                activityLogger = ActivityLoggerAdapter(_get_logger(logger_name + ".complete"), activity_info)
                message = "{}.{}".format(activity_name, completion_status)
                if exception:
                    message += ", Exception={}, {}".format(type(exception).__name__, exception)
                    activityLogger.error(message)
                else:
                    activityLogger.info(message)
    else:
        ActivityLoggerAdapter(_get_logger(logger_name), activity_info).info(activity_name)
