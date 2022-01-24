#  Copyright (c) 2020-2022 ETH Zurich, SIS ID and HVL D-ITET
#
import logging
import time
from concurrent.futures._base import Future
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Event
from typing import Callable, Optional

from ..utils.typing import Number

logger = logging.getLogger(__name__)


class Poller:
    """
    Poller class wrapping `concurrent.futures.ThreadPoolExecutor` which enables passing
    of results and errors out of the polling thread.
    """

    def __init__(
        self,
        spoll_handler: Callable,
        polling_delay_sec: Number = 0,
        polling_interval_sec: Number = 1,
        polling_timeout_sec: Optional[Number] = None,
    ):
        """
        Initialize the polling helper.

        :param spoll_handler: Polling function.
        :param polling_delay_sec: Delay before starting the polling, in seconds.
        :param polling_interval_sec: Polling interval, in seconds.
        """

        self.spoll_handler: Callable = spoll_handler
        self.polling_delay_sec: Number = polling_delay_sec
        self.polling_interval_sec: Number = polling_interval_sec
        self.polling_timeout_sec: Optional[Number] = polling_timeout_sec
        self._polling_future: Optional[Future] = None
        self._polling_stop_event: Optional[Event] = None

    def is_polling(self) -> bool:
        """
        Check if device status is being polled.

        :return: `True` when polling thread is set and alive
        """
        return self._polling_future is not None and self._polling_future.running()

    def _if_poll_again(
        self, stop_event: Event, delay_sec: Number, stop_time: Optional[Number]
    ) -> bool:
        """
        Check if to poll again.

        :param stop_event: Polling stop event.
        :param delay_sec: Delay time (in seconds).
        :param stop_time: Absolute stop time.
        :return: `True` if another polling handler call is due, `False` otherwise.
        """
        not_stopped = not stop_event.wait(delay_sec)
        not_timeout = stop_time is None or time.time() < stop_time
        return not_stopped and not_timeout

    def _poll_until_stop_or_timeout(self, stop_event: Event) -> Optional[object]:
        """
        Thread for polling until stopped or timed-out.

        :param stop_event: Event used to stop the polling
        :return: Last result of the polling function call
        """
        start_time = time.time()
        stop_time = (
            (start_time + self.polling_timeout_sec)
            if self.polling_timeout_sec
            else None
        )
        last_result = None

        if self._if_poll_again(stop_event, self.polling_delay_sec, stop_time):
            last_result = self.spoll_handler()

        while self._if_poll_again(stop_event, self.polling_interval_sec, stop_time):
            last_result = self.spoll_handler()

        return last_result

    def start_polling(self) -> bool:
        """
        Start polling.

        :return: `True` if was not polling before, `False` otherwise
        """
        was_not_polling = not self.is_polling()

        if was_not_polling:
            logger.info("Start polling")
            self._polling_stop_event = Event()
            pool = ThreadPoolExecutor(max_workers=1)
            self._polling_future = pool.submit(
                self._poll_until_stop_or_timeout, self._polling_stop_event
            )

        return was_not_polling

    def stop_polling(self) -> bool:
        """
        Stop polling.

        Wait for until polling function returns a result as well as any exception that
        might have been raised within a thread.

        :return: `True` if was polling before, `False` otherwise, and last result of
            the polling function call.
        :raises: polling function exceptions
        """
        was_polling = self.is_polling()

        if was_polling:
            logger.info("Stop polling")
            if self._polling_stop_event is None:
                raise RuntimeError("Was polling but stop event is missing.")
            self._polling_stop_event.set()
            if self._polling_future is None:
                raise RuntimeError("Was polling but polling future is missing.")

        return was_polling

    def wait_for_polling_result(self):
        """
        Wait for until polling function returns a result as well as any exception that
        might have been raised within a thread.

        :return: polling function result
        :raises: polling function errors
        """

        return self._polling_future.result()
