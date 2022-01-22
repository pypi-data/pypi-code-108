import logging

from functools import wraps
from typing import Tuple, Callable
import asyncio
import time


def async_retry(*exceptions: Tuple[Exception], retries: int = 3, cooldown: int = 1, verbose: bool = True) -> Callable:
    """
    Decorate an async function to execute it a few times before giving up.

    :param exceptions: One or more exceptions expected during function execution, as positional arguments.
    :param retries: Number of retries of function execution.
    :param cooldown: Seconds to wait before retry.
    :param verbose: Specifies if we should log about not successful attempts.
    """

    def wrap(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            _logger = logging.getLogger(__name__)
            retries_count = 0

            while True:
                try:
                    result = await func(*args, **kwargs)
                except exceptions as err:
                    retries_count += 1
                    message = "Exception {} during {} execution. " \
                              "{} of {} retries attempted".format(type(err), func, retries_count, retries)

                    if retries_count > retries:
                        verbose and _logger.exception(message)
                        raise RetryExhaustedError(func.__qualname__) from err
                    else:
                        verbose and _logger.warning(message)

                    if cooldown:
                        await asyncio.sleep(cooldown)
                else:
                    return result
        return inner
    return wrap


def retry(*exceptions: Tuple[Exception], retries: int = 3, cooldown: int = 1, verbose: bool = True) -> Callable:
    """
    Decorate a non-async function to execute it a few times before giving up.

    :param exceptions: One or more exceptions expected during function execution, as positional arguments.
    :param retries: Number of retries of function execution.
    :param cooldown: Seconds to wait before retry.
    :param verbose: Specifies if we should log about not successful attempts.
    """

    def wrap(func):
        @wraps(func)
        def inner(*args, **kwargs):
            _logger = logging.getLogger(__name__)
            retries_count = 0

            while True:
                try:
                    result = func(*args, **kwargs)
                except exceptions as err:
                    retries_count += 1
                    message = "Exception {} during {} execution. " \
                              "{} of {} retries attempted".format(type(err), func, retries_count, retries)

                    if retries_count > retries:
                        verbose and _logger.exception(message)
                        raise RetryExhaustedError(f'Exhausted retries of {func}') from err
                    else:
                        verbose and _logger.warning(message)

                    if cooldown:
                        time.sleep(cooldown)
                else:
                    return result
        return inner
    return wrap


class RetryExhaustedError(Exception):
    """
    Indicates that the retries have been exhausted and the decorated function has failed.
    """
    def __init__(self, msg: str) -> None:
        super().__init__(msg);
