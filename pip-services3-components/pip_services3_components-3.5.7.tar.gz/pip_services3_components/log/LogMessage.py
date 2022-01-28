# -*- coding: utf-8 -*-
"""
    pip_services3_components.logs.LogMessage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Log message implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import datetime
from typing import Optional

from pip_services3_commons.errors import ErrorDescription

from pip_services3_components.log import LogLevel


class LogMessage:
    """
    Data object to store captured log messages. This object is used by :class:`CachedLogger <pip_services3_components.log.CachedLogger.CachedLogger>`.
    """

    def __init__(self, level: LogLevel = None, source: str = None, correlation_id: Optional[str] = None,
                 error: ErrorDescription = None, message: str = None):
        """
        Creates log message

        :param level: a log level.

        :param source: the source (context name)

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param error: an error object associated with this message.

        :param message: a human-readable message to log.
        """
        # The time then message was generated
        self.time: datetime.datetime = datetime.datetime.utcnow()
        # This log level
        self.level: LogLevel = level
        # The source (context name)
        self.source: str = source
        # The transaction id to trace execution through call chain.
        self.correlation_id: Optional[str] = correlation_id
        # The description of the captured error
        self.error: ErrorDescription = error
        # The human-readable message
        self.message: str = message
