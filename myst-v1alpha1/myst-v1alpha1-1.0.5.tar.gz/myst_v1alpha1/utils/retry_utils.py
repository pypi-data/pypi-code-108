import functools
import logging

import tenacity

# Define the default maximum number of retries to attempt for various failed function calls.
_DEFAULT_NUM_MAX_RETRIES = 4

# Define the default multipler to use when calculating random exponential backoff between retries.
_DEFAULT_BACKOFF_MULTIPLIER = 0.25

logger = logging.getLogger(__name__)


def _log_before_sleep(retry_state):
    """Logs messages before the next retry.

    Args:
        retry_state (tenacity.RetryCallState): the current retry state
    """
    logger.info(
        str.format(
            "Retrying method, attempt {attempt_number} ended with: `{outcome}`.",
            attempt_number=retry_state.attempt_number,
            outcome=retry_state.outcome.exception(),
        )
    )


def _retry_wait(multiplier=_DEFAULT_BACKOFF_MULTIPLIER):
    """This method is separated to enable mocking for tests.

    This allows for disabling sleeping, which should only be used to speed up tests. Outside of the tests,
    we wait with exponential backoff and randomness so that all services don't call simultaneously.

    Returns:
        wait_instance (tenacity.wait.wait_base): wait method instance used by tenacity

    """
    return tenacity.wait_random_exponential(multiplier=multiplier)


def retry(num_max_retries=_DEFAULT_NUM_MAX_RETRIES, retryable_exceptions=None, **kwargs):
    """A decorator to retry a method for a list of exceptions.

    Retries up to `num_max_retries` times, using exponential backoff, for any exception.

    Args:
        num_max_retries (int): the number of times to retry
        retryable_exceptions (list of Exception, optional): a list of exceptions to retry; defaults to all exceptions
        **kwargs (any): individual parameters to overwrite in the tenacity configuration

    Returns:
        decorator (function): decorator that retries function
    """
    # Default to catching all exceptions
    if retryable_exceptions is None:
        retryable_exceptions = [Exception]

    # Tenacity overrides the `__or__` conditions, so this is necessary. Any of the exceptions should get retried.
    retry_condition = functools.reduce(
        lambda a, b: a | b,
        [tenacity.retry_if_exception_type(retryable_exception) for retryable_exception in retryable_exceptions],
    )

    retry_kwargs = dict(
        stop=tenacity.stop_after_attempt(num_max_retries),
        retry=retry_condition,
        wait=_retry_wait(),
        # This causes the exception to be raised on the final call, rather than the tenacity-specific `RetryError`.
        reraise=True,
        # Write custom logging before the next retry.
        before_sleep=_log_before_sleep,
    )
    retry_kwargs.update(kwargs)

    # Because this decorator accepts arguments, we create a decorator factory that returns an argument-less
    # decorator `retry_wrapper`. This allows us to use the readable log functionality from `functools.wraps`.
    def decorator_factory(func):

        # Define the wrapper.
        @tenacity.retry(**retry_kwargs)
        @functools.wraps(func)
        def retry_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return retry_wrapper

    return decorator_factory
