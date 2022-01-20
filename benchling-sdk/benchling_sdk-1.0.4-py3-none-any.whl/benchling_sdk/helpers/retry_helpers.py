from dataclasses import dataclass
from http import HTTPStatus
import logging
from typing import Optional, Tuple, Union

import backoff
from typing_extensions import Literal

from benchling_sdk.errors import BenchlingError

# By default, silence all except critical logs from `backoff`.
# Otherwise, `backoff` logs an error when giving up, but this is not necessary
# because it already re-raises the `BenchlingError`.
logging.getLogger("backoff").setLevel(logging.CRITICAL)


@dataclass(frozen=True, eq=True)
class RetryStrategy(object):
    """Specify a strategy for automatically retrying failed HTTP calls."""

    # Passing in None results in unbounded retries
    max_tries: Optional[int] = 5
    # Wait time between calls is backoff_factor * 2^n, where n starts at 0
    backoff_factor: float = 0.5
    status_codes_to_retry: Tuple[HTTPStatus, ...] = (
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.BAD_GATEWAY,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    )

    @staticmethod
    def no_retries() -> "RetryStrategy":
        """Construct a noop retry strategy that will not retry."""
        return RetryStrategy(0, 0, ())


_sentinel = object()


def retry_method(f):
    """
    Decorate a function to retry wrapped method if a BenchlingError is raised.

    The wrapped method must be a method on a subclass of `BaseService`,
    because the default retry strategy is taken from the `self` argument of the method.

    The decorator also adds an additional kwarg `retry_strategy` to the method signature.
    This can be used to override the service's default retry strategy.
    """
    # Inline import to avoid circular dependency
    from benchling_sdk.services.base_service import BaseService

    def func_with_retry_strategy_arg(
        self: BaseService,
        *args,
        retry_strategy: Union[RetryStrategy, Literal[_sentinel]] = _sentinel,
        **kwargs
    ):
        if retry_strategy is _sentinel:
            retry_strategy = self.retry_strategy

        def should_retry(e: BenchlingError) -> bool:
            if retry_strategy.status_codes_to_retry is None:
                return True
            return e.status_code in retry_strategy.status_codes_to_retry

        @backoff.on_exception(
            backoff.expo,
            BenchlingError,
            max_tries=retry_strategy.max_tries,
            giveup=lambda e: not should_retry(e),
            factor=retry_strategy.backoff_factor,
        )
        def func_with_retries(*fargs, **fkwargs):
            return f(*fargs, **fkwargs)

        return func_with_retries(self, *args, **kwargs)

    return func_with_retry_strategy_arg
