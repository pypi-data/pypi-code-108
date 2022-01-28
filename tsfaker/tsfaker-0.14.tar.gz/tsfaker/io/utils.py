import contextlib
import logging
import os
import sys

from tsfaker.exceptions import InvalidLoggingLevel


def get_base_file_name(file_path):
    base = os.path.basename(file_path)
    base_file_name, ext = os.path.splitext(base)
    return base_file_name


@contextlib.contextmanager
def smart_open_write(filename=None):
    if filename and filename != '-':
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def replace_dash(value, replacement):
    return replacement if value == '-' else value


def get_logging_level_value(logging_level):
    logging_level_value = logging._nameToLevel.get(logging_level.upper(), None)
    if logging_level_value is None:
        raise InvalidLoggingLevel('Logging level {} is not valid. It should take one of the following values {}'
                                  .format(logging_level, list(logging._nameToLevel.keys())))
    return logging_level_value
