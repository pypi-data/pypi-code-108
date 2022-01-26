from http import HTTPStatus
import logging
from typing import Optional

from .logging_utils import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class AporiaError(Exception):
    """Base class for Aporia SDK exceptions."""

    def __init__(self, short_message: str, verbose_message: Optional[str] = None):
        """Initializes an AporiaError.

        Args:
            short_message: Short error message
            verbose_message: Verbose error message. Defaults to the short message.
        """
        super().__init__(short_message)

        self.short_message = short_message
        self.verbose_message = short_message if verbose_message is None else verbose_message


class AporiaHTTPError(AporiaError):
    """Raised when an HTTP error status is returned."""

    def __init__(
        self, short_message: str, http_status: HTTPStatus, verbose_message: Optional[str] = None
    ):
        """Initializes an AporiaHTTPError.

        Args:
            short_message: Short error message
            http_status: HTTP status
            verbose_message: Verbose error message. Defaults to the short message.
        """
        super().__init__(short_message=short_message, verbose_message=verbose_message)

        self.http_status = http_status


def handle_error(
    message_format: str,
    verbose: bool,
    throw_errors: bool,
    debug: bool,
    log_level: int = logging.ERROR,
    original_exception: Optional[Exception] = None,
):
    """Handles an error with either a log or an exception.

    Args:
        message_format: Error message.
        verbose: True to display verbose error messages, False otherwise.
        throw_errors: True if exceptions should be raised
        debug: True if stack trace should be added to the log or exception.
        log_level: Log level for log messages.
        original_exception: Original exception for stack trace.
    """
    formatted_message = message_format
    if original_exception is not None:
        if verbose and isinstance(original_exception, AporiaError):
            formatted_message = message_format.format(original_exception.verbose_message)
        else:
            formatted_message = message_format.format(str(original_exception))

    if throw_errors:
        raise AporiaError(formatted_message) from original_exception
    else:
        logger.log(level=log_level, msg=formatted_message, exc_info=debug)
