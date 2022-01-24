# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Server for handling logging from multiple processes."""
from typing import Any, Callable, Dict, Iterator, Optional, Tuple
from types import TracebackType
from contextlib import contextmanager
import atexit
import copyreg
import logging
import logging.handlers
import os
import platform
import threading

from azureml.telemetry import get_telemetry_log_handler
from azureml.telemetry.contracts import RequiredFieldKeys, StandardFieldKeys
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import logging_fields
from azureml.automl.core.shared.fake_traceback import FakeTraceback
from azureml.automl.core.shared.telemetry_formatter import AppInsightsPIIStrippingFormatter


# allow tracebacks to go through custom serializer
def _reduce_traceback(
    traceback: TracebackType
) -> Tuple["Callable[..., Optional[FakeTraceback]]", Tuple[Optional[Dict[str, Any]]]]:
    serialized = FakeTraceback.serialize_traceback(traceback)
    return FakeTraceback.deserialize, (serialized,)


copyreg.pickle(TracebackType, _reduce_traceback)  # type: ignore


LOGFILE_ENV_NAME = "AUTOML_LOG_FILE"
TELEMETRY_ENV_NAME = "AUTOML_INSTRUMENTATION_KEY"
VERBOSITY_ENV_NAME = "AUTOML_LOG_VERBOSITY"
DEFAULT_VERBOSITY = logging.INFO
DEBUG_MODE = False
ROOT_LOGGER = logging.getLogger()

telemetry_keys = set()

verbosity = DEFAULT_VERBOSITY
logger_names = set()
handlers = {}  # type: Dict[str, logging.Handler]
custom_dimensions = {
    "app_name": constants.DEFAULT_LOGGING_APP_NAME,
    "automl_client": None,
    "automl_sdk_version": None,
    "child_run_id": None,
    "common_core_version": None,
    "compute_target": None,
    "experiment_id": None,
    "os_info": platform.system(),
    "parent_run_id": None,
    "region": None,
    "service_url": None,
    "subscription_id": None,
    "task_type": None,
    logging_fields.camel_to_snake_case(
        RequiredFieldKeys.COMPONENT_NAME_KEY
    ): logging_fields.TELEMETRY_AUTOML_COMPONENT_KEY,
    logging_fields.camel_to_snake_case(StandardFieldKeys.CLIENT_OS_KEY): platform.system(),
}  # type: Dict[str, Any]

lock = threading.RLock()
log_file_name = None  # type: Optional[str]


class DelegateHandler(logging.Handler):
    """
    Class that delegates logging calls to a set of underlying handlers.
    """

    def flush(self) -> None:
        with lock:
            for handler in handlers.values():
                handler.flush()

    def emit(self, record: logging.LogRecord) -> None:
        # Add the process ID to the record
        setattr(record, "pid", os.getpid())

        # Add the custom dimensions to the record
        new_properties = getattr(record, "properties", {})
        with lock:
            cust_dim_copy = custom_dimensions.copy()
            cust_dim_copy.update(new_properties)
            setattr(record, "properties", cust_dim_copy)

            for handler in handlers.values():
                handler.emit(record)


def install_handler(name: str) -> None:
    """
    Install handler for the logger corresponding to the given namespace.

    The logger will have log propagation automatically disabled.

    :param name: the name of the logger
    :return:
    """
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(verbosity)

    logger.addHandler(DelegateHandler())
    logger_names.add(name)


def add_handler(name: str, handler: Optional[logging.Handler], overwrite: bool = True) -> None:
    """
    Add a handler to the handler dict to be used when logging LogRecords.

    Can be used to capture all logs from AutoML by simply passing in a new handler object to intercept logs.

    :param name: name of the handler
    :param handler: the handler object. If None, disables the handler.
    :param overwrite: if set to True, always overwrite the existing handler. Otherwise, only set handler if it doesn't
    already exist.
    :return:
    """
    with lock:
        if handler is None and name in handlers:
            del handlers[name]
        elif handler is not None:
            if name not in handlers or overwrite:
                handlers[name] = handler


def remove_handler(name: str) -> None:
    """
    Remove a handler from the handler dict.

    If the handler with the given name doesn't exist, this function is a no-op.

    :param name: name of the handler
    :return:
    """
    with lock:
        if name in handlers:
            del handlers[name]


def enable_telemetry(key: Optional[str]) -> None:
    """
    Enable telemetry using the specified key or keys.

    :param key: list of app insights keys, separated by commas if there are multiple
    :return:
    """
    if not key:
        if not DEBUG_MODE:
            logging.warning("Instrumentation key was blank. Telemetry will not work.")
    else:
        for telemetry_key in key.split(","):
            handler = get_telemetry_log_handler(
                instrumentation_key=telemetry_key, component_name=logging_fields.TELEMETRY_AUTOML_COMPONENT_KEY
            )
            handler.setFormatter(AppInsightsPIIStrippingFormatter())
            telemetry_keys.add(telemetry_key)
            add_handler("telemetry-{}".format(telemetry_key), handler)
        os.environ[TELEMETRY_ENV_NAME] = ",".join(telemetry_keys)


def set_log_file(path: Optional[str]) -> None:
    """
    Specify the log file to write logs to.

    :param path: path of the log file. If None, disables logging to file.
    :return:
    """
    global log_file_name
    with lock:
        if path is None:
            if "file" in handlers:
                handlers["file"].flush()
                handlers["file"].close()
                del handlers["file"]
            return
        handler = handlers.get("file", None)
        path = os.path.abspath(path)
        if isinstance(handler, logging.FileHandler):
            if os.path.abspath(handler.baseFilename) == path:
                return
        log_file_name = path
        os.environ[LOGFILE_ENV_NAME] = path
        handler = logging.FileHandler(path)
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(pid)d - %(name)s.%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        add_handler("file", handler)


@atexit.register
def _cleanup_logging():
    with lock:
        for handler in handlers.values():
            try:
                handler.flush()
                handler.close()
            except Exception:
                pass
        handlers.clear()


def set_verbosity(new_verbosity: int) -> None:
    """
    Set verbosity on all attached loggers.

    :param new_verbosity:
    :return:
    """
    with lock:
        global verbosity
        verbosity = new_verbosity
        os.environ[VERBOSITY_ENV_NAME] = str(new_verbosity)
        for logger_name in logger_names:
            logger = logging.getLogger(logger_name)
            logger.setLevel(verbosity)


def update_custom_dimensions(new_dimensions: Dict[str, Any]) -> None:
    """
    Update the custom dimensions used during logging.

    :param new_dimensions: the new custom dimensions
    :return:
    """
    with lock:
        custom_dimensions.update(new_dimensions)


def update_custom_dimension(**kwargs: Any) -> None:
    """
    Update the custom dimensions used during logging.

    :param kwargs: the new custom dimensions
    :return:
    """
    update_custom_dimensions(kwargs)


@contextmanager
def new_log_context(**kwargs: Any) -> Iterator[None]:
    """
    Create a new log context with the current custom dimensions, restoring them when the context is exited.

    :param kwargs: custom dimensions to add to the new log context
    :return:
    """
    global custom_dimensions
    with lock:
        old_dimensions = custom_dimensions.copy()
        custom_dimensions.update(kwargs)

    yield

    with lock:
        custom_dimensions = old_dimensions


if os.environ.get(LOGFILE_ENV_NAME):
    set_log_file(os.environ.get(LOGFILE_ENV_NAME))

if os.environ.get(TELEMETRY_ENV_NAME):
    enable_telemetry(os.environ.get(TELEMETRY_ENV_NAME))

if os.environ.get(VERBOSITY_ENV_NAME):
    try:
        set_verbosity(int(os.environ.get(VERBOSITY_ENV_NAME, str(logging.INFO))))
    except Exception:
        pass
