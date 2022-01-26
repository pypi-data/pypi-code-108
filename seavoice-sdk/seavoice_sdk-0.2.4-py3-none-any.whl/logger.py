# -*- coding: utf-8 -*-

"""
To warp logging module and set log format for ngChat services

Description:
Logger module for python coded services in ngchat project

History:
2020/04/14 Create Logger module by Block
2020/04/16 Modify definition from class to function by Block
    From: WSSLogger, SVCLogger
    To: get_WSSLogger, get_SVCLogger
"""

import logging
from logging import LogRecord
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from typing import Text


LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
# Example:
# asctime: 2020-04-14 12:18:06.116
# name: twilio_agent
# levelname: INFO
# message: Server listening on: http://localhost:25625


# Declare datatime format
# "%Y-%m-%d %H:%M:%S.%f" is not supported in default Formatter
# So, NGChatFormatter is implemented to support it
class NGChatFormatter(logging.Formatter):
    """Define datetime format for loggers"""

    converter = datetime.fromtimestamp

    def formatTime(
        self,
        record: LogRecord,
        datefmt: Text = None
    ):
        """Overwrite logging.Formatter.formatTime to support millisecond"""
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)
        return s


formatter = NGChatFormatter(LOG_FORMAT)


def getLevelName(level: Text) -> int:
    """
    To get the log level value from logging.getLevelName

    Refer:
        https://docs.python.org/3/library/logging.html#levels
    Args:
        level:
            Received: "NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    Return:
        integer
    """
    return logging.getLevelName(level)


def get_WSSLogger(
    service_name: Text,
    session_id: Text,
    show_level: int = logging.INFO
) -> logging.Logger:
    """Return logger for websocket session"""
    # init logger
    logging.basicConfig(
        level=show_level,
        format=LOG_FORMAT
    )

    # Setup customized logger
    logger = logging.getLogger(service_name)
    file_handler = logging.FileHandler(
        '%s-%s.log' % (service_name, session_id),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(show_level)
    return logger


def get_SVCLogger(
    service_name: Text,
    show_level: int = logging.INFO
) -> logging.Logger:
    """Return logger for services"""
    # init logger
    logging.basicConfig(
        level=show_level,
        format=LOG_FORMAT
    )

    # Setup customized logger
    logger = logging.getLogger(service_name)
    file_handler = TimedRotatingFileHandler(
        "%s.log" % service_name,
        when='midnight',
        encoding='utf-8'
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(show_level)
    return logger
