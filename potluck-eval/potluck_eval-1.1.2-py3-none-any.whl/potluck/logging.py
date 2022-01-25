"""
Logging support.

logging.py
"""

# For Python2 cross-compatibility
from __future__ import print_function

import sys, traceback

LOG_TO = sys.stdout
"""
Where log messages go (file-like).
"""

DEBUG = False
"""
Whether or not to actually show debugging messages.
"""


def set_log_target(stream):
    """
    Sets up logging messages to go to the specified stream (must be a
    file-like object.
    """
    global LOG_TO
    LOG_TO = stream


def log(*args, **kwargs):
    """
    For now, nothing fancy: logging == printing.
    """
    kwargs['file'] = LOG_TO
    print(*args, **kwargs)


def debug_msg(*args, **kwargs):
    """
    Works like print, except it doesn't actually generate output unless
    DEBUG is set to True.
    """
    if DEBUG:
        kwargs['file'] = LOG_TO
        print(*args, **kwargs)


def log_current_exception():
    """
    Formatted logging of the currently-being-handled exception.
    """
    traceback.print_exc(file=LOG_TO)
