from __future__ import annotations

import asyncio
from time import time_ns
from typing import Any, Awaitable, Dict, Optional, TypeVar

from anyio import Semaphore, WouldBlock, move_on_after

from .errors import MaxConcurrencyError

T = TypeVar("T")


def get_task_id() -> int:
    """Nanosecond timestamp is used as task ID. No task should be scheduled at the same nanosecond so it's safe to use."""
    return time_ns()


class TaskPool:
    """A concurrency limiter can be used to submit coroutine to the event loop while enforing a maximum number of coroutines to run at the same time"""

    def __init__(self, max_concurrency: int = 1) -> None:
        """Create a new instance of limiter"""
        self.max_concurrency = int(max_concurrency)
        self.semaphore = Semaphore(self.max_concurrency)
        self.tasks: Dict[int, asyncio.Task[Any]] = {}

    async def create_task(
        self, coro: Awaitable[T], wait: bool = True
    ) -> asyncio.Task[T]:
        """Submit a new task to the event loop.

        This function will return as soon as the task is created.
        """
        task_id = get_task_id()
        if wait:
            await self.semaphore.acquire()
        else:
            try:
                self.semaphore.acquire_nowait()
            except WouldBlock:
                raise MaxConcurrencyError(
                    f"Concurrency limit is reached (were limit={self.max_concurrency})"
                )
        task = asyncio.create_task(coro)
        self.tasks[task_id] = task
        task.add_done_callback(lambda _: self._done_cb(task_id))
        return task

    def _done_cb(self, task_id: int) -> None:
        """Callback executed after each task is finished"""
        self.semaphore.release()
        self.tasks.pop(task_id, None)

    @property
    def pending(self) -> int:
        """Return number of pending tasks"""
        return len(self.tasks)

    def cancel(self) -> None:
        """Cancel all pending tasks"""
        for task in self.tasks.values():
            task.cancel()

    async def drain(
        self, timeout: Optional[float] = None, cancel_timeout: Optional[float] = None
    ) -> None:
        """Wait for all tasks to finish. Tasks exceptions are ignored silently."""
        # If there are no running tasks simply return
        if not self.tasks:
            return

        # Wait for all tasks to finish
        _, pending = await asyncio.wait(
            list(self.tasks.values()),
            timeout=timeout,
            return_when=asyncio.ALL_COMPLETED,
        )
        # If there are remaining pending tasks
        if pending:
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            # Only wait if we got a cancel_timeout
            if cancel_timeout:
                with move_on_after(cancel_timeout):
                    # Wait a second time to give a chance to tasks to exit gracefully
                    await asyncio.wait(
                        pending,
                        timeout=cancel_timeout,
                        return_when=asyncio.ALL_COMPLETED,
                    )
            # Finally raise a TimeoutError
            raise TimeoutError(
                f"Tasks did not finish before timeout and were cancelled (timeout={timeout})"
            )
