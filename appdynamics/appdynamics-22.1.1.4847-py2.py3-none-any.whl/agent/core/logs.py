# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals

import copy
import logging
import logging.handlers
import os
import os.path
import re
import threading
from datetime import datetime

from appdynamics import config
from appdynamics._vendor.structlog import wrap_logger
from appdynamics._vendor.structlog.processors import (
    TimeStamper,
    StackInfoRenderer,
    JSONRenderer,
)
from appdynamics._vendor.structlog.stdlib import (
    BoundLogger,
    LoggerFactory,
    PositionalArgumentsFormatter,
    add_logger_name,
)
from appdynamics.lang import map
from appdynamics.lib import structlog_formatter, default_log_formatter, mkdir

LOGGING_MAX_BYTES = 20000000
LOGGING_MAX_NUM_FILES = 5


class WorkerInfo(object):
    """Adds thread and process ids to log message."""

    def __call__(self, logger, log_method, event_dict):

        event_dict.update({
            'worker-info': {
                'thread-id': threading.current_thread().ident,
                'process-id': os.getpid(),
            },
            'agent-info': {
                'app': config.AGENT_APPLICATION_NAME,
                'tier': config.AGENT_TIER_NAME,
                'node': config.AGENT_NODE_NAME,
                'dir': config.AGENT_BASE_DIR,
            },
        })
        return event_dict


class LogRateLimiter(logging.Filter):
    """Logging filter for limiting log rates
    ------------
    Log rates are monitored using threshold and interval
    If the count of logs in <interval>seconds goes above the <threshold> limit, logs are suppressed.
    """
    def __init__(self, threshold, interval):
        super(LogRateLimiter, self).__init__()

        self.threshold = threshold
        self.interval = interval
        self._reset()

    def _reset(self):
        self.last_reset = datetime.now()
        self.count = 0

    def filter(self, record):
        if (datetime.now() - self.last_reset).total_seconds() >= self.interval:
            self._reset()
        if self.count >= self.threshold:
            return False
        else:
            self.count += 1
            return True


STRUCTLOG_PROCESSOR_CONFIG = lambda: dict(
    processors=[
        add_logger_name,
        PositionalArgumentsFormatter(),  # to render format strings from log messages inline
        WorkerInfo(),  # adds thread and process id to log messages
        TimeStamper(),
        StackInfoRenderer(),
        JSONRenderer(
            indent=2,
            sort_keys=True,
        ),
    ],
    context_class=dict,
    cache_logger_on_first_use=True,
    logger_factory=LoggerFactory(),
    wrapper_class=BoundLogger,
)


def setup_logger(logger_name, processor_config=None):
    """ Setup a standard library logger with `name` param and wrap it with a
        structlog logger.

        NOTE: Logger caching is required so that we return the same LoggerProxy for multiple
            setup_logger calls with the same name. This helps mimick the behavior of std lib logger.

    Parameters
    ----------
    logger_name: str
        Name for the logger instance being created.

    processor_config: dict
        structlog processors configuration dictionary. This is needed to
        configure structlog logger instance with appropriate processors that
        are applied to each log statement.

    Returns
    -------
    logger: structlog logger object if format is specified as 'structlog' else stdlib logger

    ***IMPORTANT*** If `LOG_FORMAT` is ever set to 'structlog' and later reset to `''` the return type will be
         structlog.stdlib._FixedFindCallerLogger which is a light-weight wrapper around logging.getLogger
        with extra methods such as `bind` `unbind` etc.
    """
    if config.LOG_FORMAT == 'structlog':
        processor_config = STRUCTLOG_PROCESSOR_CONFIG() if not processor_config else processor_config
        return wrap_logger(logging.getLogger(logger_name), **processor_config)
    return logging.getLogger(logger_name)


def resolve_formatter():
    return structlog_formatter if config.LOG_FORMAT == 'structlog' else default_log_formatter


def get_log_level():
    default_logging_level = logging.WARNING
    allowed_logging_levels = {'WARNING': logging.WARNING, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG}

    level = config.LOGGING_LEVEL.upper()
    return allowed_logging_levels.get(level, default_logging_level)


def get_log_filename():
    non_alphanumeric = re.compile(r'\W+')
    sanitize = lambda x: non_alphanumeric.sub('_', x)
    nodename = config.AGENT_REUSE_NODE_NAME_PREFIX if config.AGENT_REUSE_NODE_NAME else config.AGENT_NODE_NAME

    # filename is truncated as linux restricts filename to <= 255 characters.
    filename = \
        '-'.join(map(sanitize, [config.AGENT_APPLICATION_NAME, nodename]))[:config.LOG_FILENAME_MAX_SIZE - 4] + '.log'

    return os.path.join(config.LOGS_DIR, filename)


def debug_enabled(logger):
    """Return True if debugging has been enabled for this logger.

    """
    # Note: we can't just check that the level is DEBUG, since that can be
    # True without config.DEBUG_LOG being True.
    for handler in logger.handlers:
        if handler.__class__ is logging.StreamHandler:
            return True
    return False


def enable_debug(logger):
    """Enable debug mode for this logger.

    This sets the log level to DEBUG and enables a stream handler to stdout.

    """
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(resolve_formatter())
    logger.addHandler(stream_handler)


def enable_log_rate_limiting(logger):
    """Enable log rate limiting for this logger.

    This limits the logger so that logging is suppressed if the total count goes
    over config.LOG_LIMIT_THRESHOLD(600) logs in config.LOG_LIMIT_INTERVAL(60) seconds

    """
    rate_limiting_filter = LogRateLimiter(config.LOG_LIMIT_THRESHOLD, config.LOG_LIMIT_INTERVAL)
    logger.addFilter(rate_limiting_filter)


def disable_debug(logger):
    """Disable debug mode for this logger.

    This removes any stream handlers from the logger and returns the log level
    to the value specified in the agent config.

    """

    level = get_log_level()
    logger.setLevel(level)

    for handler in copy.copy(logger.handlers):
        if handler.__class__ is logging.StreamHandler:
            logger.removeHandler(handler)
        else:
            handler.setLevel(level)


def configure_logging():
    """Configure the appdynamics agent logger.

    By default, we configure 6 log files of 20MB each.
    Also, logs are limited to a threshold of 600 for 60s

    """
    try:
        logger = logging.getLogger('appdynamics.agent')
        logger.propagate = False

        level = get_log_level()
        logger.setLevel(level)

        path = get_log_filename()
        mkdir(os.path.dirname(path))
        if config.LOG_FORMAT == 'structlog':
            logger = wrap_logger(
                logger,
                **STRUCTLOG_PROCESSOR_CONFIG()
            )
        rotating_file_handler = logging.handlers.RotatingFileHandler(path, maxBytes=LOGGING_MAX_BYTES,
                                                                     backupCount=LOGGING_MAX_NUM_FILES - 1)

        rotating_file_handler.setLevel(level)
        rotating_file_handler.setFormatter(resolve_formatter())
        logger.addHandler(rotating_file_handler)

        if not (config.DEBUG_LOG or config.LOGGING_LEVEL == 'debug'):
            enable_log_rate_limiting(logger)

        if config.DEBUG_LOG:
            enable_debug(logger)

    except:
        logging.getLogger('appdynamics.agent').exception('Logging configuration failed.')
