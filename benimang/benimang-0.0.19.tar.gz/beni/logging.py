import logging
from datetime import datetime as Datetime
from functools import wraps
from pathlib import Path
from typing import Any, TextIO, cast

from colorama import Back, Fore

from beni import WrappedAsyncFunc, make_dirs
from beni.print import reset_print_color, set_print_color

_loggerName = 'beni'

_countWarning: int = 0
_countError: int = 0
_countCritical: int = 0


def init_logger(loggerName: str = '', loggerLevel: int = logging.INFO, logFile: Path | None = None):
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
                    set_print_color(Fore.LIGHTYELLOW_EX)

                elif record.levelno == logging.ERROR:
                    global _countError
                    _countError += 1
                    set_print_color(Fore.LIGHTRED_EX)
                elif record.levelno == logging.CRITICAL:
                    global _countCritical
                    _countCritical += 1
                    set_print_color(Fore.LIGHTMAGENTA_EX)
                func(msg)
                reset_print_color()
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
        make_dirs(logFile.parent)
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


def getcount_warning():
    return _countWarning


def setcount_warning(value: int):
    global _countWarning
    _countWarning = value


def getcount_error():
    return _countError


def setcount_error(value: int):
    global _countError
    _countError = value


def getcount_critical():
    return _countCritical


def setcount_critical(value: int):
    global _countCritical
    _countCritical = value


def wrapper_init_logger(loggerName: str = '', loggerLevel: int = logging.INFO, logFile: Path | None = None):
    def fun(func: WrappedAsyncFunc) -> WrappedAsyncFunc:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            startTime = Datetime.now()
            try:
                init_logger(loggerName, loggerLevel, logFile)
                return await func(*args, **kwargs)
            except BaseException as ex:
                set_print_color(Fore.LIGHTRED_EX)
                error(str(ex))
                error('执行失败')
                raise
            finally:
                if getcount_critical():
                    color = Fore.LIGHTWHITE_EX + Back.LIGHTMAGENTA_EX
                elif getcount_error():
                    color = Fore.LIGHTWHITE_EX + Back.LIGHTRED_EX
                elif getcount_warning():
                    color = Fore.BLACK + Back.LIGHTYELLOW_EX
                else:
                    color = Fore.BLACK + Back.LIGHTGREEN_EX

                set_print_color(color)
                info('-' * 75)

                msgAry = ['任务结束']
                if getcount_critical():
                    msgAry.append(f'critical({getcount_critical()})')
                if getcount_error():
                    msgAry.append(f'error({getcount_error()})')
                if getcount_warning():
                    msgAry.append(f'warning({getcount_warning()})')

                set_print_color(color)
                info(' '.join(msgAry))

                passTime = str(Datetime.now() - startTime)
                if passTime.startswith('0:'):
                    passTime = '0' + passTime
                info(f'用时: {passTime}')
        return cast(WrappedAsyncFunc, wrapper)
    return fun
