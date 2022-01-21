import logging
import sys
import pathlib

LOG_PATH = pathlib.Path.home().joinpath(".net_models.log")
VERBOSITY_MAP = {
    1: logging.CRITICAL,
    2: logging.ERROR,
    3: logging.WARNING,
    4: logging.INFO,
    5: logging.DEBUG
}
def get_logger(name, verbosity=4, handle=["stderr"], with_threads=False) -> logging.Logger:
    """
    This function provides common logging facility by creating instances of `loggers` from python standard ``logging`` library.
    :param str name: Name of the logger
    :param bool DEBUG: Enables/disables debugging output
    :param list handle: Changing value of this parameter is not recommended.
    :return: Instance of logger object
    """
    global VERBOSITY_MAP
    threading_formatter_string = '[%(asctime)s] [%(levelname)s]\t[%(name)s][%(threadName)s][%(module)s][%(funcName)s]\t%(message)s'
    single_formatter_string = '[%(asctime)s] [%(levelname)s]\t[%(name)s][%(module)s][%(funcName)s]\t%(message)s'

    formatter_string = threading_formatter_string if with_threads else single_formatter_string

    logfile_path = LOG_PATH
    formatter = logging.Formatter(formatter_string)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    file_handler = logging.FileHandler(logfile_path, delay=True)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    handlers = []
    if "stderr" in handle:
        handlers.append(stderr_handler)
    if "stdout" in handle:
        handlers.append(stdout_handler)


    for handler in handlers:
        handler.setFormatter(formatter)
        try:
            handler.setLevel(VERBOSITY_MAP[verbosity])
        except KeyError:
            handler.setLevel(logging.INFO)

    root = logging.getLogger(name)
    root.propagate = 0
    root.setLevel(logging.DEBUG)
    if verbosity == 0:
        root.disabled = True
    has_handler = {"file_handler": False, "stderr_handler": False, "stdout_handler": False}
    for handler in root.handlers:
        if isinstance(handler, logging.FileHandler):
            has_handler["file_handler"] = True
        if isinstance(handler, logging.StreamHandler):
            has_handler["stderr_handler"] = True
    if not has_handler["file_handler"]:
        root.addHandler(file_handler)
    if not has_handler["stderr_handler"]:
        root.addHandler(stderr_handler)

    return root