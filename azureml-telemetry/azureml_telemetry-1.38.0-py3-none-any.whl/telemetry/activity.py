# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines functionality for collecting telemetry about code.

An activity is a logical block of code that consumers want to monitor. To monitor an activity, either wrap
the logical block of code with the ``log_activity()`` method or use the ``@monitor_with_activity`` decorator.
"""

import contextlib
import functools
import logging
import uuid

from datetime import datetime


class ActivityType(object):
    """The type of activity (code) monitored.

    The default type is "PublicAPI".
    """

    PUBLICAPI = "PublicApi"  # incoming public API call (default)
    INTERNALCALL = "InternalCall"  # internal (function) call
    CLIENTPROXY = "ClientProxy"  # an outgoing service API call


class ActivityCompletionStatus(object):
    """The activity (code) completion status, success, or failure."""

    SUCCESS = "Success"
    FAILURE = "Failure"


class ActivityLoggerAdapter(logging.LoggerAdapter):
    """An adapter for loggers to keep activity contextual information in logging output.

    :param logger: The activity logger adapter.
    :type logger: logging.LoggerAdapter
    :param activity_info: The info to write to the logger.
    :type activity_info: str
    """

    def __init__(self, logger, activity_info):
        """Initialize a new instance of the class.

        :param logger: The activity logger.
        :type logger: logger
        :param activity_info: The info to write to the logger.
        :type activity_info: str
        """
        self._activity_info = activity_info
        super(ActivityLoggerAdapter, self).__init__(logger, None)

    @property
    def activity_info(self):
        """Return current activity info."""
        return self._activity_info

    def process(self, msg, kwargs):
        """
        Process the log message.

        :param msg: The log message.
        :type msg: str
        :param kwargs: The arguments with properties.
        :type kwargs: dict
        """
        if 'extra' not in kwargs:
            kwargs["extra"] = {}

        if "properties" not in kwargs["extra"]:
            kwargs["extra"]["properties"] = {}

        kwargs["extra"]["properties"].update(self._activity_info)

        return msg, kwargs


@contextlib.contextmanager
def log_activity(logger, activity_name, activity_type=ActivityType.INTERNALCALL, custom_dimensions=None):
    """Log an activity.

    An activity is a logical block of code that consumers want to monitor.
    To monitor, wrap the logical block of code with the ``log_activity()`` method. As an alternative, you can
    also use the ``@monitor_with_activity`` decorator.

    :param logger: The logger adapter.
    :type logger: logging.LoggerAdapter
    :param activity_name: The name of the activity. The name should be unique per the wrapped logical code block.
    :type activity_name: str
    :param activity_type: One of PUBLICAPI, INTERNALCALL, or CLIENTPROXY which represent an incoming API call,
        an internal (function) call, or an outgoing API call. If not specified, INTERNALCALL is used.
    :type activity_type: str
    :param custom_dimensions: The custom properties of the activity.
    :type custom_dimensions: dict
    """
    activity_info = dict(activity_id=str(uuid.uuid4()), activity_name=activity_name, activity_type=activity_type)
    custom_dimensions = custom_dimensions or {}
    activity_info.update(custom_dimensions)

    start_time = datetime.utcnow()
    completion_status = ActivityCompletionStatus.SUCCESS

    message = "ActivityStarted, {}".format(activity_name)
    activityLogger = ActivityLoggerAdapter(logger, activity_info)
    activityLogger.info(message)
    exception = None

    try:
        yield activityLogger
    except Exception as e:
        exception = e
        completion_status = ActivityCompletionStatus.FAILURE
        raise
    finally:
        end_time = datetime.utcnow()
        duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)

        activityLogger.activity_info["completionStatus"] = completion_status
        activityLogger.activity_info["durationMs"] = duration_ms
        message = "ActivityCompleted: Activity={}, HowEnded={}, Duration={} [ms]".format(
            activity_name, completion_status, duration_ms)
        if exception:
            message += ", Exception={}".format(type(exception).__name__)
            activityLogger.error(message)
        else:
            activityLogger.info(message)


def monitor_with_activity(logger, activity_name, activity_type=ActivityType.INTERNALCALL):
    """
    Add a wrapper for monitoring an activity (code).

    An activity is a logical block of code that consumers want to monitor.
    To monitor, use the ``@monitor_with_activity`` decorator. As an alternative, you can also wrap the
    logical block of code with the ``log_activity()`` method.

    :param logger: The logger adapter.
    :type logger: logging.LoggerAdapter
    :param activity_name: The name of the activity. The name should be unique per the wrapped logical code block.
    :type activity_name: str
    :param activity_type: One of PUBLICAPI, INTERNALCALL, or CLIENTPROXY which represent an incoming API call,
        an internal (function) call, or an outgoing API call. If not specified, INTERNALCALL is used.
    :type activity_type: str
    :return:
    """
    def monitor(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with log_activity(logger, activity_name, activity_type):
                return f(*args, **kwargs)

        return wrapper

    return monitor
