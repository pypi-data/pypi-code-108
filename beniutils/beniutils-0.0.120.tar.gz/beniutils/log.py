import logging
import os
from typing import Any, TextIO

from colorama import Fore

from beniutils import makeFolder
from beniutils.print import resetPrintColor, setPrintColor

_loggerName = 'beniutils'

_countWarning: int = 0
_countError: int = 0
_countCritical: int = 0


def initLogger(loggerName: str = "", loggerLevel: int = logging.INFO, logFile: str = ""):
    LOGGER_FORMAT = '%(asctime)s %(levelname)-1s %(message)s', '%Y-%m-%d %H:%M:%S'
    LOGGER_LEVEL_NAME = {
        logging.DEBUG: 'D',
        logging.INFO: '',
        logging.WARNING: 'W',
        logging.ERROR: 'E',
        logging.CRITICAL: 'C',
    }

    if loggerName:
        global _loggerName
        _loggerName = loggerName

    logger = logging.getLogger(_loggerName)
    logger.setLevel(loggerLevel)
    for loggingLevel, value in LOGGER_LEVEL_NAME.items():
        logging.addLevelName(loggingLevel, value)

    loggerFormatter = logging.Formatter(*LOGGER_FORMAT)

    class CustomStreamHandler(logging.StreamHandler):

        stream: TextIO

        def emit(self, record: logging.LogRecord):
            try:
                msg = self.format(record) + self.terminator
                # issue 35046: merged two stream.writes into one.
                func = self.stream.write
                if record.levelno == logging.WARNING:
                    global _countWarning
                    _countWarning += 1
                    setPrintColor(Fore.LIGHTYELLOW_EX)

                elif record.levelno == logging.ERROR:
                    global _countError
                    _countError += 1
                    setPrintColor(Fore.LIGHTRED_EX)
                elif record.levelno == logging.CRITICAL:
                    global _countCritical
                    _countCritical += 1
                    setPrintColor(Fore.LIGHTMAGENTA_EX)
                func(msg)
                resetPrintColor()
                self.flush()
            except RecursionError:  # See issue 36272
                raise
            except Exception:
                self.handleError(record)

    loggerHandler = CustomStreamHandler()
    loggerHandler.setFormatter(loggerFormatter)
    loggerHandler.setLevel(loggerLevel)
    logger.addHandler(loggerHandler)

    if logFile:
        makeFolder(os.path.dirname(logFile))
        fileLoggerHandler = logging.FileHandler(logFile, delay=True)
        fileLoggerHandler.setFormatter(loggerFormatter)
        fileLoggerHandler.setLevel(loggerLevel)
        logger.addHandler(fileLoggerHandler)


def debug(msg: str, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).debug(msg, *args, **kwargs)


def info(msg: str, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).info(msg, *args, **kwargs)


def warning(msg: str, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).warning(msg, *args, **kwargs)


def error(msg: str, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).error(msg, *args, **kwargs)


def critical(msg: str, *args: Any, **kwargs: Any):
    logging.getLogger(_loggerName).critical(msg, *args, **kwargs)


def getCountWarning():
    return _countWarning


def setCountWarning(value: int):
    global _countWarning
    _countWarning = value


def getCountError():
    return _countError


def setCountError(value: int):
    global _countError
    _countError = value


def getCountCritical():
    return _countCritical


def setCountCritical(value: int):
    global _countCritical
    _countCritical = value
