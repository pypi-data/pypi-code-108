"""Custom exceptions for Driver"""


class DriverError(Exception):
    """Base class for all Driver errors."""


class ConfigError(Exception):
    """Base class for all config errors."""


def __init__(self, message='', error=None):
    self.message = message
    self.error = error


def __str__(self):
    return self.message
