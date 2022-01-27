import logging
import logging.handlers
import sys

from tcell_agent.config.configuration import get_config
from tcell_agent.loggers.tcell_log_formatter import TCellLogFormatter


_PYTHON_LOGGER = None


def get_python_logger():
    global _PYTHON_LOGGER  # pylint: disable=global-statement

    if _PYTHON_LOGGER:
        return _PYTHON_LOGGER

    stdout_logger = logging.getLogger("tcell")
    formatter = TCellLogFormatter(
        fmt="%(asctime)s [%(tcell_version)s %(process)d] %(name)s %(message)s"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    stdout_logger.setLevel(logging.ERROR)
    stdout_logger.addHandler(handler)
    stdout_logger.propagate = False

    _PYTHON_LOGGER = stdout_logger

    return _PYTHON_LOGGER


class PythonLogger(object):
    """ Logging class in case `create_agent` fails """
    def __init__(self):
        pass

    def log_message(self, level, message, module_name):
        if not get_config().enabled:
            return

        logger = get_python_logger().getChild(module_name)

        getattr(logger, level)(message)
