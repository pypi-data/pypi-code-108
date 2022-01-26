import functools
import itertools
import logging
import time

from glibs.utils.iterutils import exponential

_logger = logging.getLogger(__name__)


def retry(
    fn,
    exceptions=Exception,
    max_tries=-1,
    delay=None,
    logger=_logger,
):
    if delay is None:
        delay = exponential()

    if isinstance(delay, (int, float)):
        delay = itertools.repeat(delay)
    else:
        delay = iter(delay)

    while True:
        try:
            return fn()
        except exceptions as e:
            max_tries -= 1
            if max_tries == 0:
                raise

            wait = next(delay)

            if logger is not None:
                logger.warning("%s, retrying in %d seconds", e, wait)

            time.sleep(wait)


def with_retry(exceptions=Exception, max_tries=-1, delay=None, logger=_logger):
    def decorator(fn):
        @functools.wraps(fn)
        def retryable(*args, **kwargs):
            return retry(
                functools.partial(fn, *args, **kwargs),
                exceptions,
                max_tries,
                delay,
                logger,
            )

        return retryable

    return decorator
