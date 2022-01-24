# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A log factory module that provides methods to log telemetric data for the Dataset SDK."""
import copy
import json
import logging
import logging.handlers
import platform
import uuid
from contextlib import contextmanager
from datetime import datetime, date
from functools import wraps

from azureml import telemetry
from azureml._base_sdk_common import __version__, _ClientSessionId
from azureml.telemetry import (INSTRUMENTATION_KEY,
                               get_diagnostics_collection_info,
                               get_telemetry_log_handler)
from azureml.telemetry.activity import ActivityLoggerAdapter, ActivityType
from azureml.telemetry.activity import log_activity as _log_activity
from azureml.telemetry.contracts import (Event, ExtensionFields,
                                         RequiredFields, StandardFields)
from azureml.telemetry.logging_handler import AppInsightsLoggingHandler

from .._utils.telemetry_utils import (
    INSTRUMENTATION_KEY_KEY, SUBSCRIPTION_ID, WORKSPACE_ID, WORKSPACE_LOCATION)

COMPONENT_NAME = 'azureml.opendatasets'
session_id = 'l_' + str(uuid.uuid4())
instrumentation_key = ''
default_custom_dimensions = {'app_name': 'opendatasets'}
ActivityLoggerAdapter = None


session_id = _ClientSessionId

telemetry_enabled, verbosity = get_diagnostics_collection_info(
    component_name=COMPONENT_NAME)
instrumentation_key = INSTRUMENTATION_KEY if telemetry_enabled else ''
DEFAULT_ACTIVITY_TYPE = ActivityType.INTERNALCALL


class _LoggerFactory:
    @staticmethod
    def get_logger(name, verbosity=logging.DEBUG):
        logger = logging.getLogger(__name__).getChild(name)
        logger.propagate = False
        logger.setLevel(verbosity)
        if telemetry_enabled:
            if not _LoggerFactory._found_handler(logger, AppInsightsLoggingHandler):
                logger.addHandler(get_telemetry_log_handler(
                    component_name=COMPONENT_NAME))

        return logger

    @staticmethod
    def track_activity(logger, activity_name, activity_type=DEFAULT_ACTIVITY_TYPE, input_custom_dimensions=None):
        from pkg_resources import get_distribution
        opendatasets_version = __version__
        try:
            dataprep_version = get_distribution('azureml-dataprep').version
        except Exception:
            # it is possible to have no azureml-dataprep installed
            dataprep_version = ''

        if input_custom_dimensions is not None:
            custom_dimensions = default_custom_dimensions.copy()
            custom_dimensions.update(input_custom_dimensions)
        else:
            custom_dimensions = default_custom_dimensions
        custom_dimensions.update({
            'source': COMPONENT_NAME,
            'version': opendatasets_version,
            'dataprepVersion': dataprep_version
        })
        if telemetry_enabled:
            log_result = _log_activity(
                logger, activity_name, activity_type, custom_dimensions)
            return log_result
        else:
            return _log_local_only(logger, activity_name, activity_type, custom_dimensions)

    @staticmethod
    def _found_handler(logger, handler_type):
        for log_handler in logger.handlers:
            if isinstance(log_handler, handler_type):
                return True

        return False

    @staticmethod
    def log_event(event_name, **kwargs):
        """
        Log the event to app insights.

        :param event_name: name of the event
        :type event_name: str
        :param kwargs: a list of the key/value pairs which will be stored in event
        :type kwargs: dict
        """
        _common_logger = telemetry.get_event_logger(
            **{INSTRUMENTATION_KEY_KEY: INSTRUMENTATION_KEY})
        req = RequiredFields()
        std = StandardFields()
        dct = copy.deepcopy(kwargs)
        req.component_name = 'OpenDatasets'
        req.client_type = 'SDK'
        req.client_version = __version__
        std.client_os = platform.system()
        if WORKSPACE_ID in kwargs:
            req.workspace_id = kwargs[WORKSPACE_ID]
            dct.pop(WORKSPACE_ID)
        if SUBSCRIPTION_ID in kwargs:
            req.subscription_id = kwargs[SUBSCRIPTION_ID]
            dct.pop(SUBSCRIPTION_ID)
        if WORKSPACE_LOCATION in kwargs:
            std.workspace_region = kwargs[WORKSPACE_LOCATION]
            dct.pop(WORKSPACE_LOCATION)
        dct['sessionId'] = session_id
        for key, value in dct.items():
            if isinstance(value, datetime) or isinstance(value, date):
                dct[key] = value.strftime("%Y-%m-%dT%H:%M:%S") if value is not None else ''
            elif isinstance(value, list):
                dct[key] = ",".join(value)
        ext = ExtensionFields(**dct)
        event = Event(name=event_name, required_fields=req, standard_fields=std,
                      extension_fields=ext)
        _common_logger.log_event(event)
        _common_logger.flush()


def track(logger, custom_dimensions=None, activity_type=DEFAULT_ACTIVITY_TYPE):
    def monitor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with _LoggerFactory.track_activity(logger, func.__name__, activity_type, custom_dimensions) as al:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    al.activity_info['error_message'] = str(e)
                    if hasattr(al, 'activity_info') and hasattr(e, 'error_code'):
                        al.activity_info['error_code'] = e.error_code
                        al.activity_info['root_error'] = getattr(
                            e, 'root_error', '')
                    raise

        return wrapper

    return monitor


def trace(logger, message, custom_dimensions=None):
    import azureml.core
    core_version = azureml.core.VERSION

    payload = dict(core_sdk_version=core_version)
    payload.update(custom_dimensions or {})

    if ActivityLoggerAdapter:
        activity_logger = ActivityLoggerAdapter(logger, payload)
        activity_logger.info(message)
    else:
        logger.info('Message: {}\nPayload: {}'.format(
            message, json.dumps(payload)))


@contextmanager
def _log_local_only(logger, activity_name, activity_type, custom_dimensions):
    activity_info = dict(activity_id=str(
        uuid.uuid4()), activity_name=activity_name, activity_type=activity_type)
    custom_dimensions = custom_dimensions or {}
    activity_info.update(custom_dimensions)

    start_time = datetime.utcnow()
    completion_status = 'Success'

    message = 'ActivityStarted, {}'.format(activity_name)
    logger.info(message)
    exception = None

    try:
        yield logger
    except Exception as e:
        exception = e
        completion_status = 'Failure'
        raise
    finally:
        end_time = datetime.utcnow()
        duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)

        custom_dimensions['completionStatus'] = completion_status
        custom_dimensions['durationMs'] = duration_ms
        message = '{} | ActivityCompleted: Activity={}, HowEnded={}, Duration={} [ms], Info = {}'.format(
            start_time, activity_name, completion_status, duration_ms, repr(activity_info))
        if exception:
            message += ', Exception={}; {}'.format(
                type(exception).__name__, str(exception))
            logger.error(message)
        else:
            logger.info(message)
