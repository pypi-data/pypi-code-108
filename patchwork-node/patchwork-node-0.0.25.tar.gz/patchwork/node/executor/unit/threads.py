# -*- coding: utf-8 -*-

import weakref
from asyncio import AbstractEventLoop
from dataclasses import field

import asyncio
import multiprocessing
import random
from asyncio.futures import Future
from functools import partial
from threading import Thread
from typing import Coroutine, List, Union, Tuple, Type, Awaitable

from patchwork.core.typing import ClassPath
from .base import ProcessingUnit

DEFAULT_CONFIG = {
    'workers': multiprocessing.cpu_count(),
    'assignor': 'collage_worker.executor.slots.threads:RandomThreadAssignor'
}


class _Thread:
    """
    Represents single worker thread. Processing unit spawns multiple _Thread's, each with it's own event loop
    and assigns tasks to them.
    """

    _thread: Thread
    _future: Future

    def __init__(self, name):
        self._name = name
        self._thread_started = asyncio.Event()
        self._is_stopping = False

    def _ready(self, loop: AbstractEventLoop):
        self._loop_ref = weakref.ref(loop, self._ref_gone_callback)
        loop.call_soon_threadsafe(self._thread_started.set)

    def _ref_gone_callback(self):
        if self._is_stopping:
            # if ref gone due to thread stop, consider this as cancel
            self._future.cancel()
        else:
            # otherwise thread just completed, don't know why but thread should not complete, never
            self._future.set_exception(RuntimeError("_Thread unit completed"))

    @property
    def loop(self):
        loop = self._loop_ref()
        if loop is None or not loop.is_running():
            self._future.set_exception(RuntimeError("_Thread unit dead and event loop cannot be accessed"))
            return None
        return loop

    @staticmethod
    def _main(ready_callback):
        loop = asyncio.new_event_loop()
        ready_callback(loop)
        loop.run_forever()

    @staticmethod
    async def _worker_stop_job(loop, stop_timeout):
        # Careful, this code is running on thread event loop!

        self_task = asyncio.tasks.Task.current_task(loop=loop)

        tasks = [t for t in asyncio.Task.all_tasks(loop=loop) if not t.done() and t is not self_task]
        for task in tasks:
            task.cancel()

        done, pending = await asyncio.wait(tasks, timeout=stop_timeout)

        loop.terminate()
        return pending

    async def start(self) -> Future:
        """
        Starts worker and waits until started. Returns future which is completed when underlying worker
        thread is completed. If worker is stopped future is marked as cancelled. If worker die unexpectedly
        future has RuntimeError exception raised.
        :return:
        """
        self._future = Future()
        self._thread = Thread(target=self._main, name=self._name, daemon=True, kwargs={
            'ready_callback': self._ready
        })
        await self._thread_started.wait()

        return self._future

    async def stop(self, stop_timeout):
        """
        Stop worker and wait for all internal jobs to complete for stop_timeout period.
        Returns list of jobs which were not completed in given timeout.
        :return:
        """
        self._is_stopping = True
        pending = await self.submit(self._worker_stop_job(self.loop, stop_timeout))

        await self._future

        return pending

    def submit(self, coro: Coroutine) -> Future:
        """
        Submits given coroutine to run on worker thread event loop.
        :param coro:
        :return:
        """
        if self._is_stopping:
            raise RuntimeError("Can't schedule coroutine, worker is stopping")

        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def __bool__(self):
        """
        Returns if worker is alive and operational.
        :return:
        """
        return not self._future.done()

    def tasks(self):
        """
        Returns list of tasks which are active on the worker
        :return:
        """
        return tuple(t for t in asyncio.Task.all_tasks(loop=self.loop) if not t.done())


class AbstractAssignor:

    def __call__(self, workers: Tuple[_Thread]) -> _Thread:
        raise NotImplementedError()


class RandomAssignor(AbstractAssignor):
    """
    Randomly assigns jobs to workers
    """

    def __call__(self, workers: Tuple[_Thread]) -> _Thread:
        return random.choice(workers)


class LessTasksAssignor(AbstractAssignor):
    """
    Assigns jobs to worker which has lowest number of active tasks.
    Note: this does not mean that this worker is the most free one, there could be one heavy task
    assigned to the worker and many mostly waiting tasks assigned to other workers
    """

    def __call__(self, workers: Tuple[_Thread]) -> _Thread:
        min_tasks = None
        worker = None

        for w in workers:
            tasks = len(w.tasks())
            if min_tasks is None or tasks < min_tasks:
                min_tasks = tasks
                worker = w

        return worker


class ThreadPoolUnit(ProcessingUnit):
    """
    Run jobs in separate threads async loops to avoid blocking main thread loop
    when jobs are CPU intensive or blocking. Tasks are distributed among threads
    by assignor.
    """

    class Config(ProcessingUnit.Config):
        pass
        # use given assignor to assign tasks to thread workers
        # assignor: ClassPath = 'collage_worker.executor.workers.threads.RandomAssignor'

        # number of thread workers to spawn, by default number of CPUs
        # threads: int = field(default_factory=multiprocessing.cpu_count)

        # assignor options, depends on actual assignor, all options will be passed as __init__ arguments
        # to assignor class
        # assignor_options = field(default_factory=dict)

    _threads: List[Union[None, _Thread]]
    _assignor: AbstractAssignor

    def __repr__(self):
        res = super().__repr__()
        return f"<{res[1:-2]}, threads={self.settings.threads}, assignor={self.settings.assignor.__class__.__name__}]>"

    async def _run_job(self, coro: Coroutine) -> Awaitable:
        workers: Tuple[_Thread] = tuple(w for w in self._threads if w is not None)

        choosen_worker: _Thread = self._assignor(workers)
        return choosen_worker.submit(coro)

    async def _start(self) -> bool:
        """
        Setup worker
        :return:
        """

        self._threads: List[Union[None, _Thread]] = [None] * self.settings.threads
        try:
            assignor_cls: Type[AbstractAssignor] = self.settings.assignor
        except Exception as e:
            self.logger.error(
                f"Can't load assignor class from '{self.settings.assignor}'\nDetails:\n{type(e)}: {e}",
                exc_info=True,
                extra={
                    'assignor': self.settings.assignor
                }
            )
            return False

        try:
            self._assignor = assignor_cls(**self.settings.assignor_options)
        except Exception as e:
            self.logger.error(
                f"Can't instantiate assignor '{assignor_cls.__name__}'\nDetails:\n{type(e)}: {e}",
                exc_info=True,
                extra={
                    'assignor': self.settings.assignor
                }
            )
            return False

        self.logger.info(f"Setting up {self.settings.threads} thread workers")

        for idx in range(self.settings.threads):
            await self._spawn(idx)

        return True

    async def _spawn(self, index):
        assert self._threads[index] is None

        self._threads[index] = _Thread(name=f'unit-{index}')

        # start returns a future which represents worker thread, when done
        # it means that thread is completed
        fut = await self._threads[index].start()
        fut.add_done_callback(partial(self._on_worker_die, index=index))

    def _on_worker_die(self, fut: Future, index):
        if fut.cancelled():
            # worker has been cancelled, it's intentional "die"
            return

        exc = fut.exception()
        if exc:
            self.logger.error(f"{self.__class__.__name__} died: {exc}")
        else:
            self.logger.info(f"{self.__class__.__name__} completed with result '{fut.result()}'")

        self._threads[index] = None

        # schedule worker re-spawn
        asyncio.create_task(asyncio.ensure_future(self._spawn(index)))
