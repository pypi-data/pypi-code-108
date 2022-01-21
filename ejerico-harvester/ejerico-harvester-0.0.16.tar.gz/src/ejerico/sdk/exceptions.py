"""
TODO:
"""

import logging

__all__ = [
    "Error",
    "ValidationError",
]

class Error(Exception):
    """Base class for ejerico exceptions."""

    def __init__(self, msg=None, inner_exception=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.inner_exception = inner_exception


class RuntimeError(Error):pass

class ValidationError(Error):pass

class GraphError(Error):pass