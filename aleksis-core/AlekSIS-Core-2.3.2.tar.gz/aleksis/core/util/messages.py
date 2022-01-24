import logging
from typing import Any, Optional

from django.contrib import messages
from django.http import HttpRequest


def add_message(
    request: Optional[HttpRequest], level: int, message: str, **kwargs
) -> Optional[Any]:
    """Add a message.

    Add a message to either Django's message framework, if called from a web request,
    or to the default logger.

    Default to DEBUG level.
    """
    if request:
        return messages.add_message(request, level, message, **kwargs)
    else:
        return logging.getLogger(__name__).log(level, message)


def debug(request: Optional[HttpRequest], message: str, **kwargs) -> Optional[Any]:
    """Add a debug message.

    Add a message to either Django's message framework, if called from a web request,
    or to the default logger.

    Default to DEBUG level.
    """
    return add_message(request, messages.DEBUG, message, **kwargs)


def info(request: Optional[HttpRequest], message: str, **kwargs) -> Optional[Any]:
    """Add a info message.

    Add a message to either Django's message framework, if called from a web request,
    or to the default logger.

    Default to INFO level.
    """
    return add_message(request, messages.INFO, message, **kwargs)


def success(request: Optional[HttpRequest], message: str, **kwargs) -> Optional[Any]:
    """Add a success message.

    Add a message to either Django's message framework, if called from a web request,
    or to the default logger.

    Default to SUCCESS level.
    """
    return add_message(request, messages.SUCCESS, message, **kwargs)


def warning(request: Optional[HttpRequest], message: str, **kwargs) -> Optional[Any]:
    """Add a warning message.

    Add a message to either Django's message framework, if called from a web request,
    or to the default logger.

    Default to WARNING level.
    """
    return add_message(request, messages.WARNING, message, **kwargs)


def error(request: Optional[HttpRequest], message: str, **kwargs) -> Optional[Any]:
    """Add an error message.

    Add a message to either Django's message framework, if called from a web request,
    or to the default logger.

    Default to ERROR level.
    """
    return add_message(request, messages.ERROR, message, **kwargs)
