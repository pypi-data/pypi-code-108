"""Decorator for debugging messages using the `print` statement or logging the
infomation in a .log file"""

from functools import wraps
import logging
import os


def print_debug(*, prefix: str = None):
    """You can only debug with the `print` statement, that's the only way. So
    this debugging tool tries to execute the function, but in casa there is an
    error, you can search for the `prefix` and the function name to catch the
    error.

    The function requires named arguments, not positional. If you use positons
    on a big team, they will hate you and I learned through that hate, so you
    don't have to.

    prefix -> String"""
    def decorator(function):
        msg = prefix + function.__qualname__

        @wraps(function)
        def wrapper(*args, **kwargs):
            print(msg)
            return function(*args, **kwargs)
        return wrapper
    return decorator


def __logger_object(path: str):
    """Creates and return the logger object. Requires a path because it tries
    to create the path that you put in the `logging_debug` function, if it
    isn't created, no worries, it uses it no problem."""
    logger = logging.getLogger("CSJ-CONTROL-PROCESO")
    logger.setLevel(logging.INFO)
    # checking and creating the file if it doesn't exist.
    if os.path.isfile(f"{path}"):
        pass
    else:
        head_tail = os.path.split(f"{path}")
        path_dir = head_tail[0]
        # path_file = head_tail[1]
        os.makedirs(f"{path_dir}", exist_ok=True)
        open(f"{path}", "w").close()
    # file where we are going to log
    logger_file = logging.FileHandler(f"{path}")
    # logger format
    logger_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(logger_format)
    logger_file.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(logger_file)
    return logger


def logging_debug(*, prefix: str = None, path: str = "./logs/error.log"):
    """Simple Debugger which creates the required files in the given path (It
    creates folders and files no problem) or it can use an already existing one
    without any problem.

    it ONLY uses NAMED ARGUMENTS, positional arguments are a Big NoNo, as you
    want real structure from the function callings, and those are:

    prefix -> String : The prefix that you would use to grep or search in the
                       log file.
    path -> String: The Path that you will use to store the log files that you
                    are creating. If the path doesn't exist the funcion will
                    create it for you. If no path is given it would create an
                    error.log file with the path BASE_DIR/logs/error.log"""
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            logger = __logger_object(path)
            try:
                return function(*args, **kwargs)
            except Exception:
                msg = (
                    f"{prefix} "
                    "Oh No, something happened in the function "
                    f"{function.__qualname__}"
                )
                logger.exception(msg)
                raise
        return wrapper
    return decorator
