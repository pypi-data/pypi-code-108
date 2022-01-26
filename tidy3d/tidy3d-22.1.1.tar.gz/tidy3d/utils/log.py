import sys
import logging as lg

# Hard-coded user-facing log file path
LOGFILE = 'output/tidy3d.log'
# Server-side temporary logs
LOGFILE_CPU = 'output/tidy3d_cpu.log'
LOGFILE_SOLVER = 'output/tidy3d_solver.log'

class Tidy3DError(Exception):
    """Base class for our custom errors.
    This can also be used to pass a pre/post-processing error to the user.
    """


class DivergenceError(Tidy3DError):
    pass


class MonitorError(Tidy3DError):
    pass


class SourceError(Tidy3DError):
    pass


class StructureError(Tidy3DError):
    pass


class LessThanFilter(lg.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0


class MoreThanFilter(lg.Filter):
    def __init__(self, exclusive_minimum, name=""):
        super(MoreThanFilter, self).__init__(name)
        self.min_level = exclusive_minimum

    def filter(self, record):
        # non-zero return means we log this message
        return 1 if record.levelno > self.min_level else 0


def _level_str(level):
    """String to logging level."""
    if level.lower() == "debug":
        return lg.DEBUG
    elif level.lower() == "info":
        return lg.INFO
    elif level.lower() == "warning":
        return lg.WARNING
    elif level.lower() == "error":
        return lg.ERROR
    elif level.lower() == "critical":
        return lg.CRITICAL
    else:
        raise ValueError(f"Unrecognized level '{level}'.")


def log_and_raise(err_msg, exc_type):
    """Log an erorr and raise an exception."""
    lg.error("!!!!!!!!!!")
    lg.error(err_msg)
    raise exc_type(err_msg)


def logging_default():
    """Set the default logging configuration. File logging is reset.
    INFO and DEBUG level messages are redirected to stdout. WARNING and above
    go to stderr as usual.
    """
    logger = lg.getLogger()
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    logger.setLevel(lg.NOTSET)
    formatter = lg.Formatter("%(levelname)s: %(message)s")

    logging_handler_err = lg.StreamHandler(sys.stderr)
    logging_handler_err.setLevel(lg.WARNING)
    logging_handler_err.addFilter(MoreThanFilter(lg.INFO))
    logging_handler_err.setFormatter(formatter)
    logger.addHandler(logging_handler_err)

    logging_handler_out = lg.StreamHandler(sys.stdout)
    logging_handler_out.setLevel(lg.INFO)
    logging_handler_out.addFilter(LessThanFilter(lg.WARNING))
    logger.addHandler(logging_handler_out)


def logging_level(level):
    """Set the lowest severity level to print to the console, as per the
    python logger. This sets the level for both stdout and stderr output.

    Parameters
    ----------
    level : str
        One of ``['debug', 'info', 'warning', 'error', 'critical']``.
    """
    logger = lg.getLogger()
    lg_level = _level_str(level)
    for handler in logger.handlers:
        handler.setLevel(lg_level)


def logging_file(fname, filemode="w", level="debug"):
    """Set a file to write log to, independently from the stdout and stderr
    output chosen using :meth:`logging_level`.

    Parameters
    ----------
    fname : str
        File name to direct the output to.
    filemode : str, optional
        'w' or 'a', defining if the file should be overwritten or appended.
    level : str
        One of 'debug', 'info', 'warning', 'error', 'critical'. This is
        set for the file independently of the console output level set by
        :meth:`logging_level`.
    """

    logger = lg.getLogger()
    file_handler = lg.FileHandler(fname, filemode)
    file_handler.setLevel(_level_str(level))
    formatter = lg.Formatter("%(levelname)s: %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
