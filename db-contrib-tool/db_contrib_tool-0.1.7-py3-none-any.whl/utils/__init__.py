"""Helper functions."""

import sys


def is_windows():
    """Return True if Windows."""
    return sys.platform.startswith("win32") or sys.platform.startswith("cygwin")
