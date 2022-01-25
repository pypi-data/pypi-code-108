"""
description: this module provides constants: LOGGING_LEVEL, LOG_PATH
"""

import logging.config


class LOGGING_LEVEL:
    """
    description: the logger level.
    """

    INFO = logging.INFO
    DEBUG = logging.DEBUG
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    NOTSET = logging.NOTSET
    DUMB = logging.CRITICAL + 10


class LOG_PATH:
    """
    description: the logs path.
    """
    ECHO_AGENT = "./logs/pistar_echo_agent.log"
    PISTAR = "./logs/pistar.log"
