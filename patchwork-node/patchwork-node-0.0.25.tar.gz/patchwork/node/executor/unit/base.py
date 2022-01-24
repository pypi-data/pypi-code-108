# -*- coding: utf-8 -*-

import asyncio
import logging
import weakref
from collections import namedtuple
from functools import partial
from typing import Coroutine, MutableMapping, Awaitable

from patchwork.core import Component
from patchwork.core.utils import Flag, cached_property

Job = namedtuple('Job', ('task', 'coroutine'))


class ProcessingUnit(Component):

    class Config(Component.Config):
        # number of tasks which can be queued for waiting until processing unit is ready
        queue_size: int = 1

        # number of tasks which can be run concurrently on the processing unit
        concurrency: int = 1

    _processing_loop: asyncio.Future
    _in_queue: asyncio.Queue
    _available: asyncio.Event
    _busy: Flag

    def __init__(self, *, parent, **options):
        self._jobs = set()
        super().__init__(parent=parent, **options)

    @property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        return asyncio.get_running_loop()

    @cached_property
    def logger(self) -> logging.Logger:
        return logging.getLogger('patchwork.worker.unit')

    @property
    def busy(self) -> Flag:
        """
        Returns awaitable flag which is True when unit is busy (which means there is at least one task in progress).
        :return:
        """
        return self._busy

    @property
    def executor(self):
        return self.parent

    async def _start(self):
        assert self.settings.queue_size > 0, "Queue length cannot be less than 1"
        assert self.settings.concurrency > 0, "Concurrency cannot be less than 1"

        self._in_queue = asyncio.Queue(maxsize=self.settings.queue_size)
        self._available = asyncio.Event()
        self._available.set()
        self._busy = Flag(False)

    async def run(self):
        await super().run()
        self._processing_loop = asyncio.create_task(self._loop())
        self._processing_loop.add_done_callback(self._on_loop_completed)

    def _on_loop_completed(self, fut: asyncio.Future):
        if fut.cancelled():
            return

        exc = fut.exception()
        if exc is not None:
            self.logger.error(f"Processing unit crashed with exception: {exc.__class__.__name__}({exc})")

        # unit loop is not working, this unit is no longer usable
        stop = asyncio.create_task(self.terminate())

        def _cblk(f):
            if f.cancelled() or f.exception():
                # stop failed, force state flag to false so parent component can react
                self.state.set(False)
                self.logger.fatal(f"Can't stop crashed processing unit. Termination forced")

        stop.add_done_callback(_cblk)

    async def _loop(self):
        while True:
            try:
                # wait until unit is available
                await self._available.wait()

                # unit is ready, wait for task
                # fut is a Future which represents task to run, this future has been
                # returned to the callee who scheduled the coro to run
                job: Job = await self._in_queue.get()

                if job.task.cancelled():
                    # job has been cancelled in meanwhile (between scheduling and now)
                    continue

                # create async background task from given coroutine
                runner = self.event_loop.create_task(self._run_job(job.coroutine))
                self._jobs.add(job)
                self.logger.debug(f"Task `{job.coroutine.cr_code.co_name}` scheduled")

                runner_callback = partial(self._on_job_done, job=job)
                runner.add_done_callback(runner_callback)

                # when task is cancelled, remove listener which transfers result from runner to the task and
                # cancel the runner future
                job.task.add_done_callback(lambda f: runner.remove_done_callback(runner_callback) and runner.cancel())

                if len(self._jobs) == self.settings.concurrency:
                    self._available.clear()

                self._busy.set(True)

            except asyncio.CancelledError:
                return

    def _on_job_done(self, fut: asyncio.Future, job: Job):
        """
        Scheduled coroutine future callback. The main job here is to pass fut state into task.
        :param fut: Future which represents scheduled coroutine (code)
        :param job:
        :return:
        """
        if fut.cancelled():
            job.task.cancel()

        exc = fut.exception()
        if exc is not None:
            job.task.set_exception(exc)
        else:
            job.task.set_result(fut.result())

        self._jobs.remove(job)
        self._in_queue.task_done()
        if len(self._jobs) < self.settings.concurrency:
            self._available.set()

        if not self._jobs:
            self._busy.set(False)

    async def submit(self, coro: Coroutine):
        """
        Submits given coroutine to run on the worker, return a coroutine which represents submitted task.
        Result of returned coro is the same as result of submitted coro, canceling it cancels submitted task,
        however returned coro may raise more exceptions than submitted one.
        :param coro:
        :return:
        """
        fut = self.event_loop.create_future()
        await self._in_queue.put(Job(task=fut, coroutine=coro))
        return fut

    async def _stop(self):
        """
        Terminate worker.
        :return:
        """
        self.logger.debug(f"{self.__class__.__name__} received termination request, "
                          f"there is {len(self._jobs)} active tasks")

        # cancel processing unit loop
        if not self._processing_loop.done():
            self._processing_loop.cancel()

        # request cancelling of all running tasks
        for job in self._jobs:
            job.task.cancel()

        if self._jobs:
            self.logger.debug(f"Procesing unit has {len(self._jobs)} active jobs. Waiting for cancellation...")
            # wait until tasks are completed
            await asyncio.wait([job.task for job in self._jobs])

    def _run_job(self, coro: Coroutine) -> Awaitable:
        """
        Schedules given coroutine to run and returns awaitable object which represents
        coro execution.
        :param coro:
        :return:
        """
        raise NotImplementedError()

    def get_state(self) -> MutableMapping:
        """
        Returns current worker state
        :return:
        """
        return {
            'tasks': len(self._jobs)
        }

    def __repr__(self):
        res = super().__repr__()
        return f"<{res[1:-1]} [{'available' if self._available.is_set() else 'full'}, " \
               f"qsize={self.settings.queue_size}, concurrency={self.settings.concurrency}, tasks={len(self._jobs)}]>"
