# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A logger factory module that provides methods to log telemetry for responsible ai SDK."""
import logging
import logging.handlers
import uuid
import json
import os
import traceback
from pathlib import Path
from contextlib import contextmanager
from functools import wraps

from azureml.core.model import Model

COMPONENT_NAME = 'azureml.responsibleai'
session_id = 'l_' + str(uuid.uuid4())
instrumentation_key = ''
default_custom_dimensions = {'app_name': 'responsibleai'}
stack_trace_limit = 5
ActivityLoggerAdapter = None
AZUREML_PACKAGE_PARENT = None

try:
    from azureml.telemetry import get_telemetry_log_handler, INSTRUMENTATION_KEY, get_diagnostics_collection_info
    from azureml.telemetry.activity import log_activity as _log_activity, ActivityType, \
        ActivityLoggerAdapter as logAdapter
    from azureml.telemetry.logging_handler import AppInsightsLoggingHandler
    from azureml._base_sdk_common import _ClientSessionId
    ActivityLoggerAdapter = logAdapter
    session_id = _ClientSessionId
    telemetry_enabled, verbosity = get_diagnostics_collection_info(component_name=COMPONENT_NAME)
    instrumentation_key = INSTRUMENTATION_KEY if telemetry_enabled else ''
    DEFAULT_ACTIVITY_TYPE = ActivityType.INTERNALCALL
except Exception:
    telemetry_enabled = False
    DEFAULT_ACTIVITY_TYPE = 'InternalCall'


class _LoggerFactory:
    _core_version = None
    _responsibleai_version = None

    @staticmethod
    def get_logger(name, verbosity=logging.DEBUG):
        logger = logging.getLogger(__name__).getChild(name)
        logger.propagate = False
        logger.setLevel(verbosity)
        if telemetry_enabled:
            if not _LoggerFactory._found_handler(logger, AppInsightsLoggingHandler):
                logger.addHandler(get_telemetry_log_handler(component_name=COMPONENT_NAME))

        return logger

    @staticmethod
    def track_activity(logger, activity_name, activity_type=DEFAULT_ACTIVITY_TYPE, input_custom_dimensions=None):
        _LoggerFactory._get_version_info()

        if input_custom_dimensions is not None:
            custom_dimensions = default_custom_dimensions.copy()
            custom_dimensions.update(input_custom_dimensions)
        else:
            custom_dimensions = default_custom_dimensions
        custom_dimensions.update({
            'source': COMPONENT_NAME,
            'version': _LoggerFactory._core_version,
            'raiVersion': _LoggerFactory._responsibleai_version,
        })

        run_info = _LoggerFactory._try_get_run_info()
        if run_info is not None:
            custom_dimensions.update(run_info)

        if telemetry_enabled:
            return _log_activity(logger, activity_name, activity_type, custom_dimensions)
        else:
            return _run_without_logging(logger, activity_name, activity_type, custom_dimensions)

    @staticmethod
    def _found_handler(logger, handler_type):
        for log_handler in logger.handlers:
            if isinstance(log_handler, handler_type):
                return True
        return False

    @staticmethod
    def _get_version_info():
        if _LoggerFactory._core_version is not None and _LoggerFactory._responsibleai_version is not None:
            return

        core_ver = _get_package_version('azureml-core')
        if core_ver is None:
            # only fallback when the approach above fails, as azureml.core.VERSION has no patch version segment
            try:
                from azureml.core import VERSION as core_ver
            except Exception:
                core_ver = ''
        _LoggerFactory._core_version = core_ver

        rai_ver = _get_package_version('azureml-responsibleai')
        if rai_ver is None:
            try:
                from azureml.responsibleai import __version__ as rai_ver
            except Exception:
                rai_ver = ''
        _LoggerFactory._responsibleai_version = rai_ver

    @staticmethod
    def _try_get_run_info():
        try:
            import re
            import os
            location = os.environ.get("AZUREML_SERVICE_ENDPOINT")
            location = re.compile("//(.*?)\\.").search(location).group(1)
        except Exception:
            location = os.environ.get("AZUREML_SERVICE_ENDPOINT", "")
        return {
            "subscription": os.environ.get('AZUREML_ARM_SUBSCRIPTION', ""),
            "run_id": os.environ.get("AZUREML_RUN_ID", ""),
            "resource_group": os.environ.get("AZUREML_ARM_RESOURCEGROUP", ""),
            "workspace_name": os.environ.get("AZUREML_ARM_WORKSPACE_NAME", ""),
            "experiment_id": os.environ.get("AZUREML_EXPERIMENT_ID", ""),
            "location": location
        }


def track(get_logger, custom_dimensions=None, activity_type=DEFAULT_ACTIVITY_TYPE):
    def monitor(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            with _LoggerFactory.track_activity(logger, func.__name__, activity_type, custom_dimensions) as al:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    al.activity_info["exception_type"] = str(type(e))
                    al.activity_info["filtered_stacktrace"] = "\n".join(
                        _extract_and_filter_stack(traceback.extract_stack(limit=stack_trace_limit)))
                    raise

        return wrapper

    return monitor


def _extract_and_filter_stack(traces):
    ret = []
    global AZUREML_PACKAGE_PARENT
    if AZUREML_PACKAGE_PARENT is None:
        AZUREML_PACKAGE_PARENT = _get_azureml_package_parent_dir()

    for trace in traces:
        if os.path.join("site-packages", "azureml") in trace.filename:
            fullpath_parts = Path(trace.filename).parts
            partial_path = os.path.sep.join(fullpath_parts[fullpath_parts.index(AZUREML_PACKAGE_PARENT):])
            ret.append("{} line {} in {}".format(partial_path, trace.lineno, trace.line))
        else:
            ret.append("< External code >")

    return ret


def _get_azureml_package_parent_dir():
    from azureml.core import __file__
    path_parts = Path(__file__).parts
    return path_parts[path_parts.index("__init__.py") - 3]


def trace(logger, message, custom_dimensions=None):
    import azureml.core
    core_version = azureml.core.VERSION

    payload = dict(core_sdk_version=core_version)
    payload.update(custom_dimensions or {})

    if ActivityLoggerAdapter:
        activity_logger = ActivityLoggerAdapter(logger, payload)
        activity_logger.info(message)
    else:
        logger.info('Message: {}\nPayload: {}'.format(message, json.dumps(payload)))


def collect_model_info(logger, message, models, custom_dimensions=None):
    def _get_model_info(model):
        try:
            if model:
                model_dto_additional_properties = Model._get(model.workspace, id=model.id).additional_properties
                return {"modelContainerId": model_dto_additional_properties["modelContainerId"]}
        except Exception as e:
            trace(logger, '_get_model_info FAILED with: ' + str(e))
            return {}

    try:
        for model in models:
            model_info = _get_model_info(model)
            model_info.update(_get_workspace_info(logger, model.workspace))
            trace(logger, message, model_info)
    except Exception as e:
        trace(logger, 'collect_model_info FAILED with: ' + str(e))


def collect_run_info(logger, message, runs, custom_dimensions=None):
    def _get_run_info(exprun):
        try:
            if exprun:
                return {"runId": exprun.get_details()["runId"]}
        except Exception as e:
            trace(logger, '_get_run_info FAILED with: ' + str(e))
            return {}

    try:
        for run in runs:
            run_info = _get_run_info(run)
            run_info.update(_get_workspace_info(logger, run.experiment.workspace))
            trace(logger, message, run_info)
    except Exception as e:
        trace(logger, 'collect_run_info FAILED with: ' + str(e))


def _get_workspace_info(logger, workspace):
    common_dimensions = {}
    try:
        if workspace:
            try:
                common_dimensions.update({
                    'subscription_id': workspace.subscription_id,
                    'resource_group_name': workspace.resource_group,
                    'workspace_name': workspace.name,
                    'location': workspace.location
                })
            except Exception:
                pass

        return common_dimensions

    except Exception as e:
        trace(logger, '_get_workspace_info FAILED with: ' + str(e))
        return common_dimensions


def _get_package_version(package_name):
    import pkg_resources
    try:
        return pkg_resources.get_distribution(package_name).version
    except Exception:
        # Azure CLI exception loads azureml-* package in a special way which makes get_distribution not working
        try:
            all_packages = pkg_resources.AvailableDistributions()  # scan sys.path
            for name in all_packages:
                if name == package_name:
                    return all_packages[name][0].version
        except Exception:
            # In case this approach is not working neither
            return None


@contextmanager
def _run_without_logging(logger, activity_name, activity_type, custom_dimensions):
    yield logger
