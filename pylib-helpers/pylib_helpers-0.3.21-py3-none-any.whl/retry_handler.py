# StdLib
from time import sleep
from typing import Callable

from .logger import Logger


class RetryHandler:

    RETRY_ATTEMPTS: int

    def __init__(
        self, exc_types: tuple, max_retries=15, wait_time=30, err_callbacks: dict[str, tuple[Callable, dict]] = {}
    ):
        self._log = Logger()
        self._RETRIES = 0
        self._MAX_RETRIES = max_retries
        self._err_callbacks = err_callbacks
        self._exc_types = exc_types
        self._wait_time = wait_time
        self.RETRY_ATTEMPTS = 0

    def wrap(self, func):
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                self._reset_connection_retries()
                return res
            except Exception as err:
                err_callback = self._err_callbacks.get(type(err).__name__, None)
                if err_callback:
                    result = err_callback[0](error_obj=err, **err_callback[1])
                    if result and result[0]:
                        return result[1]
                self.RETRY_ATTEMPTS += 1
                self._retry_exception(err)
                return wrapper(*args, **kwargs)

        return wrapper

    def _retry_exception(self, err: Exception):
        if isinstance(err, self._exc_types):
            self._RETRIES += 1
            self._log.print_warning(f"[RetryHandler] Encountered {type(err).__name__}: {err}")
            if self._RETRIES > self._MAX_RETRIES:
                self._log.print_error("[RetryHandler] Retries exhausted. Exiting.")
                self._reset_connection_retries()
                raise err
            else:
                self._log.print_warning(f"[RetryHandler] Will retry ({self._RETRIES}/{self._MAX_RETRIES})")
                sleep(self._wait_time)

    def _reset_connection_retries(self):
        self._RETRIES = 0
