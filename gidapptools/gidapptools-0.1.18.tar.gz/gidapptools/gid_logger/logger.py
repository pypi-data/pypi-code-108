"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
import sys
import queue
import atexit
import logging
from typing import Union, Iterable
from pathlib import Path
from logging.handlers import QueueHandler, QueueListener

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.gid_logger.enums import LoggingLevel
from gidapptools.gid_logger.handler import GidBaseRotatingFileHandler, GidBaseStreamHandler
from gidapptools.gid_logger.formatter import GidLoggingFormatter, get_all_func_names, get_all_module_names

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidLogger(logging.Logger):
    ...


def _modify_logger_name(name: str) -> str:
    if name == "__main__":
        return 'main'
    name = 'main.' + '.'.join(name.split('.')[1:])
    return name


def get_logger(name: str) -> Union[logging.Logger, GidLogger]:
    name = _modify_logger_name(name)
    return logging.getLogger(name)


def setup_main_logger(name: str, path: Path, log_level: LoggingLevel = LoggingLevel.DEBUG, formatter: Union[logging.Formatter, GidLoggingFormatter] = None, extra_logger: Iterable[str] = tuple()) -> Union[logging.Logger, GidLogger]:
    os.environ["MAX_FUNC_NAME_LEN"] = str(min([max(len(i) for i in get_all_func_names(path, True)), 20]))
    os.environ["MAX_MODULE_NAME_LEN"] = str(min([max(len(i) for i in get_all_module_names(path)), 20]))

    handler = GidBaseStreamHandler(stream=sys.stdout)

    que = queue.Queue(-1)
    que_handler = QueueHandler(que)
    listener = QueueListener(que, handler)
    formatter = GidLoggingFormatter() if formatter is None else formatter
    handler.setFormatter(formatter)
    _log = get_logger(name)
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    _log.addHandler(que_handler)
    _log.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    return _log


def setup_main_logger_with_file_logging(name: str,
                                        log_file_base_name: str,
                                        path: Path,
                                        log_level: LoggingLevel = LoggingLevel.DEBUG,
                                        formatter: Union[logging.Formatter, GidLoggingFormatter] = None,
                                        log_folder: Path = None,
                                        extra_logger: Iterable[str] = tuple(),
                                        max_func_name_length: int = None,
                                        max_module_name_length: int = None,
                                        stream=sys.stdout) -> Union[logging.Logger, GidLogger]:
    if os.getenv('IS_DEV', "false") != "false":
        log_folder = path.parent.joinpath('logs')

    os.environ["MAX_FUNC_NAME_LEN"] = str(max_func_name_length) if max_func_name_length is not None else "25"
    os.environ["MAX_MODULE_NAME_LEN"] = str(max_module_name_length) if max_module_name_length is not None else "25"

    que = queue.Queue(-1)
    que_handler = QueueHandler(que)

    formatter = GidLoggingFormatter() if formatter is None else formatter
    endpoints = []
    if stream is not None:
        handler = GidBaseStreamHandler(stream=stream)
        handler.setFormatter(formatter)
        endpoints.append(handler)

    file_handler = GidBaseRotatingFileHandler(base_name=log_file_base_name, log_folder=log_folder)
    file_handler.setFormatter(formatter)
    endpoints.append(file_handler)
    listener = QueueListener(que, *endpoints)
    _log = get_logger(name)
    log_level = LoggingLevel(log_level)
    if "py.warnings" in extra_logger:
        logging.captureWarnings(True)
    for logger in [_log] + [logging.getLogger(l) for l in extra_logger]:
        logger.addHandler(que_handler)

        logger.setLevel(log_level)
    listener.start()
    atexit.register(listener.stop)
    return _log


def get_main_logger():
    return logging.getLogger("__main__")
# region[Main_Exec]


if __name__ == '__main__':
    pass

# endregion[Main_Exec]
