import asyncio
from concurrent.futures import Future
import logging
from threading import Thread
from typing import Any, Coroutine

from .logging_utils import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class EventLoop:
    """Asyncio event loop manager for worker thread loop."""

    def __init__(self):
        """Initializes an EventLoop instance."""
        logger.debug("Starting event loop in a worker thread.")
        self.loop = asyncio.new_event_loop()
        self.loop_thread = Thread(target=self.run_loop, daemon=True)

        self.loop_thread.start()

    def run_loop(self):
        """Runs the asyncio event loop."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def create_task(self, coro: Coroutine) -> Future:
        """Schedule a coroutine without waiting for result.

        Args:
            coro (Coroutine): Coroutine to schedule.

        Returns:
            Future: Future object to wait for the result of the coroutine.
        """
        future = asyncio.run_coroutine_threadsafe(coro=coro, loop=self.loop)
        return future

    def run_coroutine(self, coro: Coroutine) -> Any:
        """Runs a coroutine in the worker thread loop and await result.

        Args:
            coro (Coroutine): Coroutine to execute

        Returns:
            Any: Coroutine return value
        """
        future = self.create_task(coro)

        return future.result()
