# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility module for logging."""
import contextlib
import functools
import json
import logging
import os
import sys
import sysconfig
import traceback
from types import ModuleType
from typing import Any, Callable, cast, Dict, Iterator, List, Optional, Tuple, Union

from azureml._common.exceptions import AzureMLException
from azureml.automl.core.shared.exceptions import AutoMLException, ErrorTypes, NON_PII_MESSAGE
from azureml.automl.core.shared.fake_traceback import FakeTraceback
from azureml.automl.core.shared.telemetry_activity_logger import TelemetryActivityLogger

logger = logging.getLogger(__name__)


allowed_paths = set()

# Note: These are now all disabled since it seems there's edge cases that we can't necessarily account for.
allowed_exception_types = {
    # 5.2 Concrete exceptions
    # These act on user data and so should be tested
    # AttributeError,
    # ImportError,
    # IndexError,
    # RecursionError,
    # ReferenceError,
    # TypeError,
    # ZeroDivisionError,
    # These are all issues with source code
    # NameError,
    # NotImplementedError,
    # SyntaxError,
    # IndentationError,
    # TabError,
    # UnboundLocalError,
    # Temporarily disabling these until we have a good way to check for PII leakage
    # AssertionError,
    # EOFError,
    # FloatingPointError,
    # OverflowError,
    # 5.2.1 OS exceptions
    # BlockingIOError,
    # ChildProcessError,
    # ConnectionError,
    # BrokenPipeError,
    # ConnectionAbortedError,
    # ConnectionRefusedError,
    # ConnectionResetError,
    # InterruptedError,
    # ProcessLookupError,
    # TimeoutError
}


activity_logger = TelemetryActivityLogger()


def mark_package_exceptions_as_loggable(module: ModuleType) -> None:
    try:
        paths = cast(Any, module).__path__
        for path in paths:
            # Any path in __path__ that is relative could be user code, don't allow it
            if os.path.commonprefix([".", path]) == "":
                allowed_paths.add(path)
    except AttributeError:
        pass


def mark_path_as_loggable(path: str) -> None:
    allowed_paths.add(path)


def mark_path_as_not_loggable(path: str) -> None:
    allowed_paths.remove(path)


def is_non_automl_exception_allowed(exception: BaseException) -> bool:
    # Use direct type check instead of isinstance, because we should be subclassing AutoMLException instead of
    # those types and that is handled via a different path
    if type(exception) not in allowed_exception_types:
        return False

    frames = traceback.extract_tb(exception.__traceback__)
    if len(frames) == 0:
        return True
    exception_path = frames[-1].filename
    return is_path_allowed(exception_path)


def is_path_allowed(exception_path: str) -> bool:
    for path in allowed_paths:
        if exception_path.startswith(path):
            return True
    return False


def is_stdlib_module(exception_path: str) -> bool:
    """
    Determine whether this is a module shipped with Python.

    :param exception_path:
    :return:
    """
    stdlib_dir = sysconfig.get_path("stdlib")
    if stdlib_dir is None:
        return False

    stdlib_dir = os.path.normpath(stdlib_dir)
    stdlib_dir = os.path.normcase(stdlib_dir)

    module_directory = os.path.dirname(exception_path)
    module_directory = os.path.normpath(module_directory)
    module_directory = os.path.normcase(module_directory)

    if "site-packages" in module_directory.lower():
        return False
    try:
        if os.path.commonpath([module_directory, stdlib_dir]) != stdlib_dir:
            return False
    except ValueError:
        # Can occur when one of the paths is relative, or if the paths are on different drive letters.
        return False
    return True


def is_exception_stacktrace_loggable() -> bool:
    if os.environ.get("AUTOML_MANAGED_ENVIRONMENT") == "1":
        return True
    return False


def _get_pii_free_message(exception: BaseException) -> str:
    if isinstance(exception, AutoMLException):
        return exception.get_pii_free_exception_msg_format()
    elif is_non_automl_exception_allowed(exception):
        return str(exception)
    else:
        return NON_PII_MESSAGE


def _get_null_logger(name: str = "null_logger") -> logging.Logger:
    null_logger = logging.getLogger(name)
    null_logger.addHandler(logging.NullHandler())
    null_logger.propagate = False
    return null_logger


NULL_LOGGER = _get_null_logger()


def log_traceback(
    exception: BaseException,
    logger: Optional[Union[logging.Logger, logging.LoggerAdapter]],
    override_error_msg: Optional[str] = None,
    is_critical: Optional[bool] = True,
    tb: Optional[Any] = None,
) -> None:
    """
    Log exception traces.

    :param exception: The exception to log.
    :param logger: The logger to use.
    :param override_error_msg: The message to display that will override the current error_msg.
    :param is_critical: If is_critical, the logger will use log.critical, otherwise log.error.
    :param tb: The traceback to use for logging; if not provided, the one attached to the exception is used.
    """
    # There's not really a good place to put this code other than here, because it will cause a circular import
    # if it runs when this file is imported.
    # noinspection PyUnresolvedReferences
    import azureml

    mark_package_exceptions_as_loggable(azureml)

    if logger is None:
        logger = NULL_LOGGER

    if override_error_msg is not None:
        error_msg = override_error_msg
    else:
        error_msg = str(exception)

    error_code, error_type, exception_target = _get_error_details(exception, logger)

    # Some exceptions may not have a __traceback__ attr
    traceback_obj = tb or exception.__traceback__ if hasattr(exception, "__traceback__") else None or sys.exc_info()[2]
    traceback_msg = _CustomStackSummary.get_traceback_message(traceback_obj, remove_pii=False)

    exception_class_name = exception.__class__.__name__

    # User can see original log message in their log file
    message = [
        "Type: {}".format(error_code),
        "Class: {}".format(exception_class_name),
        "Message: {}".format(error_msg),
        "Traceback:",
        traceback_msg,
        "ExceptionTarget: {}".format(exception_target),
    ]

    # Marking extra properties to be PII free since azureml-telemetry logging_handler is
    # not updating the extra properties after formatting.
    # Get PII free exception_message
    error_msg_without_pii = _get_pii_free_message(exception)
    # Get PII free exception_traceback
    traceback_msg_without_pii = _CustomStackSummary.get_traceback_message(traceback_obj)
    # Get PII free exception_traceback
    extra = {
        "properties": {
            "error_code": error_code,
            "error_type": error_type,
            "exception_class": exception_class_name,
            "exception_message": error_msg_without_pii,
            "exception_traceback": traceback_msg_without_pii,
            "exception_target": exception_target,
        },
        "exception_tb_obj": traceback_obj,
    }
    if is_critical:
        logger.critical("\n".join(message), extra=extra)
    else:
        logger.error("\n".join(message), extra=extra)


def _get_error_details(
    exception: BaseException, logger: Union[logging.Logger, logging.LoggerAdapter]
) -> Tuple[str, str, str]:
    """
    Extracts the error details from the base exception.
    For exceptions outside AzureML (e.g. Python errors), all properties are set as 'Unclassified'

    :param exception: The exception from which to extract the error details
    :param logger: The logger object to log to
    :return: An error code, error type (i.e. UserError or SystemError) and exception's target
    """
    default_target = "Unspecified"

    if isinstance(exception, AutoMLException):
        return exception.error_code, exception.error_type, (exception.target or default_target)

    if isinstance(exception, AzureMLException):
        try:
            serialized_ex = json.loads(exception._serialize_json())
            error = serialized_ex.get(
                "error", {"code": ErrorTypes.Unclassified, "inner_error": {}, "target": default_target}
            )

            # This would be the complete hierarchy of the error
            error_code = str(error.get("inner_error", ErrorTypes.Unclassified))

            # This is one of 'UserError' or 'SystemError'
            error_type = error.get("code")

            exception_target = error.get("target")
            return error_code, error_type, exception_target
        except Exception:
            logger.warning(
                "Failed to parse error details while logging traceback from exception of type {}".format(exception)
            )
            # revert to defaults

    # Defaults
    error_code = ErrorTypes.Unclassified
    error_type = ErrorTypes.Unclassified
    exception_target = default_target
    return error_code, error_type, exception_target


def get_logger(
    namespace: Optional[str] = None,
    filename: Optional[str] = None,
    verbosity: int = logging.DEBUG,
    extra_handlers: Optional[List[logging.Handler]] = None,
    component_name: Optional[str] = None,
) -> logging.Logger:
    """
    Create the logger with telemetry hook.

    :param namespace: The namespace for the logger
    :param filename: log file name
    :param verbosity: logging verbosity
    :param extra_handlers: any extra handlers to attach to the logger
    :param component_name: component name
    :return: logger if log file name and namespace are provided otherwise null logger
    """
    logger = logging.getLogger(namespace)
    return logger


def function_debug_log_wrapped(log_level: int = logging.DEBUG) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Add logs wrapper around transformer class function."""

    def wrapper(f: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(f)
        def debug_log_wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
            my_logger = logging.getLogger(f.__module__)
            my_logger.log(log_level, "Starting {} operation of {}.".format(f.__name__, self.__class__.__name__))
            r = f(self, *args, **kwargs)
            my_logger.log(log_level, "{} {} operation complete.".format(self.__class__.__name__, f.__name__))
            return r

        return debug_log_wrapped

    return wrapper


BLOCKLISTED_LOGGING_KEYS = [
    "path",
    "resource_group",
    "workspace_name",
    "data_script",
    "_debug_log",
    "label_column_name",
    "weight_column_name",
    "cv_split_column_names",
    "time_column_name",
    "grain_column_names",
    "drop_column_names",
    "compute_target",
    "featurization",
    "y_min",
    "y_max",
    "name",
    "project_name",
    "experiment_name",
    "resource_group_name",
    "location",
]


def remove_blacklisted_logging_keys_from_dict(dict_obj: Dict[str, Any]) -> None:
    """Recursively remove the key from a dict."""
    keys = [k for k in dict_obj.keys()]
    blocklisted_keys = set(BLOCKLISTED_LOGGING_KEYS)
    for k in keys:
        if k in blocklisted_keys:
            del dict_obj[k]
        else:
            values = [dict_obj[k]]  # type: List[Any]
            while len(values) > 0:
                v = values.pop()
                # Check if the dictionary is stored as a string such as
                # "{'task_type':'classification','primary_metric':'AUC_weighted','debug_log':'classification.log'}"
                if isinstance(v, str) and v.startswith("{") and v.endswith("}"):
                    try:
                        v = eval(v)
                        remove_blacklisted_logging_keys_from_dict(v)
                        dict_obj[k] = str(v)
                    except Exception:
                        pass
                elif isinstance(v, list):
                    values.extend(v)
                elif isinstance(v, dict):
                    remove_blacklisted_logging_keys_from_dict(v)


def remove_blacklisted_logging_keys_from_json_str(json_str: str) -> str:
    """Recursively remove the key from a json str and return a json str."""
    try:
        dict_obj = json.loads(json_str)
        remove_blacklisted_logging_keys_from_dict(dict_obj)
        return json.dumps(dict_obj)
    except Exception:
        # Delete the whole string since it cannot be parsed properly
        return "***Information Scrubbed For Logging Purposes***"


def log_system_info(logger: logging.Logger, prefix_message: str = "") -> None:
    """
    Log cpu, memory and OS info.

    :param logger: logger object
    :param prefix_message: string that in the prefix in the log
    :return: None
    """
    if prefix_message is None:
        prefix_message = ""

    try:
        import psutil

        cpu_count, logical_cpu_count = psutil.cpu_count(logical=False), psutil.cpu_count()
        virtual_memory, swap_memory = psutil.virtual_memory().total, psutil.swap_memory().total
        extra_info = {
            "properties": {
                "CPUCount": cpu_count,
                "LogicalCPUCount": logical_cpu_count,
                "VirtualMemory": virtual_memory,
                "SwapMemory": swap_memory,
            }
        }
        logger.info(
            "{}CPU logical cores: {}, CPU cores: {}, virtual memory: {}, swap memory: {}.".format(
                prefix_message, logical_cpu_count, cpu_count, virtual_memory, swap_memory
            ),
            extra=extra_info,
        )
    except Exception:
        logger.warning("Failed to log system info using psutil.")

    import platform

    logger.info("{}Platform information: {}.".format(prefix_message, platform.system()))


def _found_handler(logger: logging.Logger, handle_name: Any) -> bool:
    """
    Check logger with the given handler and return the found status.

    :param logger: Logger
    :param handle_name: handler name
    :return: boolean: True if found else False
    """
    for log_handler in logger.handlers:
        if isinstance(log_handler, handle_name):
            return True

    return False


@contextlib.contextmanager
def log_activity(
    logger: logging.Logger,
    activity_name: str,
    activity_type: Optional[str] = None,
    custom_dimensions: Optional[Dict[str, Any]] = None,
) -> Iterator[Optional[Any]]:
    """
    Log the activity status with duration.

    :param logger: logger
    :param activity_name: activity name
    :param activity_type: activity type
    :param custom_dimensions: custom dimensions
    """
    return activity_logger._log_activity(logger, activity_name, activity_type, custom_dimensions)


class _CustomStackSummary(traceback.StackSummary):
    """Subclass of StackSummary."""

    def format(self: traceback.StackSummary) -> List[str]:
        """Format the stack ready for printing.

        Returns a list of strings ready for printing.  Each string in the
        resulting list corresponds to a single frame from the stack.
        Each string ends in a newline; the strings may contain internal
        newlines as well, for those items with source text lines.
        """
        result = []
        for frame in self:
            row = ['  File "{}", line {}, in {}\n'.format(os.path.basename(frame.filename), frame.lineno, frame.name)]
            if frame.line:
                row.append("    {}\n".format(frame.line.strip()))
            if frame.locals:
                for name, value in sorted(frame.locals.items()):
                    row.append("    {name} = {value}\n".format(name=name, value=value))
            result.append("".join(row))
        return result

    def format_allowed_paths(self: traceback.StackSummary) -> List[str]:
        """Format the traceback, removing any unallowed paths."""
        result = []
        for frame in self:
            path = os.path.dirname(frame.filename)
            if is_path_allowed(path) or is_stdlib_module(frame.filename):
                row = [
                    '  File "{}", line {}, in {}\n'.format(os.path.basename(frame.filename), frame.lineno, frame.name)
                ]
                if frame.line:
                    row.append("    {}\n".format(frame.line.strip()))
                if frame.locals:
                    for name, value in sorted(frame.locals.items()):
                        row.append("    {name} = {value}\n".format(name=name, value=value))
            else:
                row = [
                    '  File "{}", line {}, in {}\n'.format("[Non-AutoML file]", frame.lineno, "[Non-AutoML function]")
                ]
            result.append("".join(row))
        return result

    @staticmethod
    def get_traceback_message(traceback_obj: Any, remove_pii: bool = True) -> str:
        traceback_not_available_msg = "Not available (exception was not raised but was returned directly)"
        if traceback_obj is None:
            return traceback_not_available_msg

        # traceback.extract_tb expects a TracebackType, but we're smuggling a duck-typed FakeTraceback
        # so a cast is required
        if isinstance(traceback_obj, dict):
            ft = cast(Any, FakeTraceback.deserialize(traceback_obj))
        else:
            ft = traceback_obj
        stack_summary = traceback.extract_tb(ft)

        if is_exception_stacktrace_loggable() or not remove_pii:
            return "".join(_CustomStackSummary.format(stack_summary))

        return "".join(_CustomStackSummary.format_allowed_paths(stack_summary))
