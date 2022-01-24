# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Server for handling logging from multiple processes."""
from typing import Any, Optional
from unittest import mock
from .._logging.log_server import (
    add_handler,
    remove_handler,
    install_handler,
    enable_telemetry,
    set_log_file,
    set_verbosity,
    update_custom_dimension,
    update_custom_dimensions,
    new_log_context,
    verbosity,
    logger_names,
    handlers,
    custom_dimensions,
    lock,
    DEFAULT_VERBOSITY,
    DEBUG_MODE,
    ROOT_LOGGER,
    DelegateHandler,
)


HOST_ENV_NAME = "AUTOML_LOG_HOST"
PORT_ENV_NAME = "AUTOML_LOG_PORT"
server = mock.MagicMock()  # type: Optional[Any]
client = mock.MagicMock()  # type: Optional[Any]
server_host = "localhost"
server_port = 31337


LogRecordStreamHandler = mock.MagicMock()
LogServer = mock.MagicMock()
AutoMLSocketHandler = DelegateHandler


def install_sockethandler(name: str, host: Optional[str] = None, port: Optional[int] = None) -> None:
    """
    Install a DelegateHandler for the logger corresponding to the given namespace.

    The logger will have log propagation automatically disabled.

    :param name: the name of the logger
    :param host: unused
    :param port: unused
    :return:
    """
    install_handler(name)
