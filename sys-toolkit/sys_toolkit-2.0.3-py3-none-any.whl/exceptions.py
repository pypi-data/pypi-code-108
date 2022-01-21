"""
Exceptions raised by OS base classes
"""


class CommandError(Exception):
    """
    Exceptions raised by shell commands
    """


class ConfigurationError(Exception):
    """
    Errors raised by configuration processing
    """


class LoggerError(Exception):
    """
    Exceptions raised by logging configuration
    """


class FileParserError(Exception):
    """
    Exceptions raised while parsing text files
    """
