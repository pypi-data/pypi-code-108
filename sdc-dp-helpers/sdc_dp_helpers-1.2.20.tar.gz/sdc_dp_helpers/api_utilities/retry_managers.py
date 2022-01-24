"""
    Retry Managers:
        - retry decorators
        - failure mode handlers
"""
import time
from functools import wraps
from random import random

from sdc_helpers.slack_helper import SlackHelper


def retry_handler(
    exceptions,
    total_tries: int = 4,
    initial_wait: float = 0.5,
    backoff_factor: int = 2,
    should_raise: bool = False,
):
    """
    Decorator - managing API failures

    args:
        exceptions (Exception): Exception instance or list of
        Exception instances to catch & retry
        total_tries (int): Total retry attempts
        initial_wait (float): initial delay between retry attempts in seconds
        backoff_factor (int): multiplier used to further randomize back off
        should_raise (bool): Raise exception after all retires fail

    return:
        wrapped function's response
    """

    def retry_decorator(function):
        @wraps(function)
        def func_with_retries(*args, **kwargs):
            """wrapper function to decorate function with retry functionality"""
            _tries, _delay = total_tries, initial_wait
            while _tries > 0:
                try:
                    print(f"Attempt {total_tries + 1 - _tries}")
                    return function(*args, **kwargs)
                except exceptions as exception:
                    # get logger message
                    if _tries == 1:
                        slack_helper = SlackHelper()
                        slack_helper.send_critical(
                            message=str(
                                f"Function: {function.__name__}\n"
                                f"Failed despite best efforts after {total_tries} tries\n"
                                f"Exception {exception}."
                            )
                        )

                        if should_raise:
                            raise exception
                    else:
                        msg = str(
                            f"Function: {function.__name__}\n"
                            f"Exception {exception}.\n"
                            f"Retrying in {_delay} seconds!"
                        )
                    # log with print
                    print(msg)
                    # decrement _tries
                    _tries -= 1
                    # pause
                    time.sleep(_delay)
                    # increase delay by backoff factor
                    _delay = _delay * backoff_factor

        return func_with_retries

    return retry_decorator


def request_handler(
    wait: float = 0, backoff_factor: float = 0.01, backoff_method: str = "random"
):
    """
    Decorator - managing API failures

    Args:
        wait (float, optional): [description].
            Defaults to 100 seconds for GoogleAnalytics.
            Initial delay between retry attempts in seconds
        backoff_factor (float, optional):
            [description]. Defaults to 0.1.
            Multiplier used to further randomize delay
        backoff_method (str, optional):
            [description]. Defaults to 'random'. hHow to apply backoff
    return:
        wrapped function's response
    """

    def retry_decorator(function):
        @wraps(function)
        def func_with_retries(*args, **kwargs):
            """wrapper function to decorate function with retry functionality"""
            if backoff_method == "random":
                _delay = wait * (1 + backoff_factor * random())
            else:
                _delay = wait

            print(f"Waiting {_delay} seconds before attempt")
            time.sleep(_delay)
            return function(*args, **kwargs)

        return func_with_retries

    return retry_decorator
