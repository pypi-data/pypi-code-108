"""
Module that defines shared Exceptions between blocks.
Should be used to raise specific `sys.exit` codes as below:

![Exceptions](assets/exceptions.png)

Make use of the decorator in your `run` method to provide appropriate
standardized exit codes:

```python
@catch_exceptions(logger)
def run():
    do_stuff()
```
"""
import functools
import sys
from enum import Enum

from logging import Logger
from .logging import get_logger


class SupportedErrors(Enum):
    """
    Enumerator of standardized error codes for the UP42 platform.

    - `INPUT_PARAMETERS_ERROR` (2)
        - User provided wrong or inconsistent configuration parameters.
    - `NO_INPUT_ERROR` (3)
        - Block did not find input data, e.g. no data in the
            requested area (data block), no features in data.json (processing block).
    - `WRONG_INPUT_ERROR` (4)
        - Input data is unsuitable, e.g. a processing block
            expects 16 bit but receives 8 bit.
    - `API_CONNECTION_ERROR` (5)
        - API which is used by the block is down or changed its interface.
    - `NO_OUTPUT_ERROR` (6)
        - After applying all processing step no data results
            to be provided to the user.
    - `ERR_INCORRECT_ERRCODE` (100)
    """

    INPUT_PARAMETERS_ERROR = (
        2
        # User provided wrong or inconsistent configuration parameters.
    )
    NO_INPUT_ERROR = (
        3
        # Block did not find input data, e.g. no data in the
        # requested area (data block), no features in data.json (processing block).
    )
    WRONG_INPUT_ERROR = (
        4
        # Input data is unsuitable, e.g. a processing block
        # expects 16 bit but receives 8 bit.
    )
    API_CONNECTION_ERROR = (
        5
        # API which is used by the block is down or changed its interface.
    )
    NO_OUTPUT_ERROR = (
        6
        # After applying all processing step no data results
        # to be provided to the user.
    )
    ERR_INCORRECT_ERRCODE = 100  # No error code defined.


class UP42Error(Exception):
    """
    The UP42 error base class.
    """

    def __init__(self, error_code: SupportedErrors, message=""):
        """
        Example:
            ```python
            if not results:
                raise UP42Error(SupportedErrors.NO_OUTPUT_ERROR)
            ```

        Arguments:
            error_code: A SupportedErrors instance, i.e.
                `SupportedErrors.NO_OUTPUT_ERROR`
            message: An optional message to be logged.
        """
        # Raise a separate exception in case the error code passed isn't specified in the ErrorCodes enum
        if not isinstance(error_code, SupportedErrors):
            msg = "Error code passed in the error_code param must be of type {0}"
            raise UP42Error(SupportedErrors.ERR_INCORRECT_ERRCODE, message)

        # Storing the error code on the exception object
        self.error_code = error_code

        # storing the traceback which provides useful information about where the exception occurred
        self.traceback = sys.exc_info()

        # Prefixing the error code to the exception message
        msg = f"[{error_code.name}] {message}"

        Exception.__init__(self, msg)


# Disable unused function argument due to wrapper
# pylint: disable=unused-argument
def catch_exceptions(logger: Logger = get_logger(__name__)):
    """
    A decorator that wraps the passed in function and
    returns the appropriate exit code.

    Arguments:
        logger: A logging instance. Can be generated with
            `blockutils.logging.get_logger(__name__)`
    """

    def decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except UP42Error as e:
                if e.error_code == SupportedErrors.INPUT_PARAMETERS_ERROR:
                    log_exception(function, logger, "Incorrect input parameters.")
                    sys.exit(SupportedErrors.INPUT_PARAMETERS_ERROR.value)
                elif e.error_code == SupportedErrors.NO_INPUT_ERROR:
                    log_exception(function, logger, "No input data found.")
                    sys.exit(SupportedErrors.NO_INPUT_ERROR.value)
                elif e.error_code == SupportedErrors.WRONG_INPUT_ERROR:
                    log_exception(function, logger, "Unsuitable input data found.")
                    sys.exit(SupportedErrors.WRONG_INPUT_ERROR.value)
                elif e.error_code == SupportedErrors.API_CONNECTION_ERROR:
                    log_exception(
                        function,
                        logger,
                        "Connection error with API. Please try again later.",
                    )
                    sys.exit(SupportedErrors.API_CONNECTION_ERROR.value)
                elif e.error_code == SupportedErrors.NO_OUTPUT_ERROR:
                    log_exception(function, logger, "No output data created.")
                    sys.exit(SupportedErrors.NO_OUTPUT_ERROR.value)
                else:
                    log_exception(function, logger, "Undefined error code.")
                    sys.exit(SupportedErrors.ERR_INCORRECT_ERRCODE.value)
            except MemoryError:
                log_exception(
                    function,
                    logger,
                    "Memory limit surpassed. Please make sure to check the docs for block limitations.",
                )
                sys.exit(137)
            except Exception:  # pylint: disable=broad-except
                log_exception(function, logger)
                sys.exit(1)

        def log_exception(function, logger, err="Generic exception."):
            logger.exception(err)

        return wrapper

    return decorator
