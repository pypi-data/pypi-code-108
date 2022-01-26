from __future__ import annotations

import traceback

import asyncio
import logging
import signal
import sys
import typing as t
from contextlib import AsyncExitStack
from warnings import warn

from ._typing import _T
from .helper import Registry

log = logging.getLogger(__name__)

_T_ExceptionHandlers = t.MutableMapping[t.Tuple[t.Type[Exception], ...], t.Callable[[Exception], t.Any]]
_TaskYieldType = t.Optional[asyncio.Future]

__sentinel_tasks__ = set()
WINDOWS = sys.platform == 'win32'


class ExcInfo(t.NamedTuple):
    exc_type: t.Type[Exception] | None = None
    exc: Exception | None = None
    traceback: t.Any | None = None


def mark_sentinel_task(task):
    global __sentinel_tasks__
    __sentinel_tasks__.add(task)
    return task


def handle_exception(loop: asyncio.BaseEventLoop, context):
    # context["message"] will always be there; but context["exception"] may not
    loop.default_exception_handler(context)

    msg = context.get("tb", context["message"])
    log.error(msg)
    log.info("Shutting down...")

    additional_args = {'name': f"shutdown({context['message']})"} if sys.version_info >= (3, 8) else {}

    asyncio.create_task(shutdown(loop, context=context), **additional_args)


async def stop_task(task: asyncio.Task):
    if task is asyncio.current_task():
        raise ValueError(f"Not allowed to stop task running `stop_task`!")

    task.cancel()
    return (await asyncio.gather(task, return_exceptions=True))[0]


def setup_shutdown_handling(loop):
    _signals = (signal.SIGBREAK, signal.SIGINT) if WINDOWS else (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

    def _clear_signal_handlers():
        remove_handler = (
            lambda sig: signal.signal(sig, signal.SIG_IGN)
            if WINDOWS else
            loop.remove_signal_handler
        )
        [remove_handler(s) for s in _signals]

    def signal_handler(sig, frame):
        _clear_signal_handlers()
        kwargs = {} if sys.version_info < (3, 8) else {'name': f'shutdown({sig!r})'}
        asyncio.create_task(shutdown(loop, signal=sig, frame=frame), **kwargs)

    add_handler = (
        signal.signal
        if WINDOWS else
        loop.add_signal_handler
    )

    [add_handler(sig, signal_handler) for sig in _signals]

    if not loop.get_exception_handler():
        loop.set_exception_handler(handle_exception)


async def shutdown(loop, **kwargs):
    sig = kwargs.pop('signal', None)

    if sig:
        log.info(f"Received exit signal {sig!r}...")

    get_tasks = (lambda: [
        task_ for task_ in asyncio.all_tasks()
        if task_ is not asyncio.current_task()
    ])

    context = kwargs.pop('context', {})
    sentinel = context.get('sentinel')
    if sentinel:
        result = await stop_task(sentinel)
    else:
        filter_function = (lambda task_: task_ in __sentinel_tasks__)

        result = await asyncio.gather(
            *map(stop_task, filter(filter_function, get_tasks()))
        )
    if result:
        log.debug(f"Sentinel task[s] stopped with result {result!r}")

    tasks = get_tasks()
    log.info(f"Cancelling {len(tasks)} outstanding tasks")
    for task in tasks:
        await stop_task(task)

    loop.stop()


class TaskNursery(AsyncExitStack, Registry):
    __has_handling__: t.Set[asyncio.BaseEventLoop] = set()
    __unique_key_attr__ = 'name'

    @staticmethod
    def add_shutdown_handling(loop):
        if loop not in TaskNursery.__has_handling__:
            setup_shutdown_handling(loop)

    def stop_task(self, task):
        if task not in self._tasks:
            raise ValueError(f"{task} not contained in pending tasks of {self}")

        return stop_task(task)

    def __init__(self, name=None, loop=None):
        super().__init__()
        self._tasks: t.List[asyncio.Task] = []

        self.exception_handlers: _T_ExceptionHandlers = {}
        self.fallback_handler = log.exception
        self.loop = loop or asyncio.get_running_loop()

        # teardown behaviour
        self.push_async_callback(self._stop_all)
        self.add_shutdown_handling(self.loop)
        self.sentinel_task = mark_sentinel_task(
            self.create_task(
                self._sentinel_task(event=asyncio.Event()),  # dummy event which is never set
            )
        )
        self.sentinel_task.remove_done_callback(self._task_cb)
        self.name = name or f'TaskNursery-{len(type(self).registry)}'

    async def _sentinel_task(self, event):
        try:
            await event.wait()
        except asyncio.CancelledError:
            pass

        self._tasks.remove(self.sentinel_task)
        self.sentinel_task = None

        await self.aclose()
        return "Success"

    async def _stop_all(self):
        stoppable = [task for task in self._tasks if task is not asyncio.current_task()]
        return await asyncio.gather(*map(self.stop_task, stoppable), return_exceptions=True)

    def _task_cb(self, task: asyncio.Task):
        try:
            result = task.result()
            if task in self._tasks:
                self._tasks.remove(task)
            return result
        except asyncio.CancelledError:
            pass
        except:  # noqa
            exc_info = sys.exc_info()
            self.loop.call_exception_handler(
                {
                    'message': f'{exc_info[1]!r} from {task!r}',
                    'task': task,
                    'tb': traceback.format_exc(),
                    'sentinel': self.sentinel_task
                }
            )

    def create_task(self,
                    coro: t.Generator[_TaskYieldType, None, _T] | t.Awaitable[_T],
                    **kwargs) -> asyncio.Task[_T]:

        if sys.version_info >= (3, 8):
            if 'name' not in kwargs:
                kwargs['name'] = getattr(coro, '__name__', str(coro))
            kwargs['name'] += f":{self.__registry_key__}"
        else:
            if kwargs.pop('name', None):
                warn(f"No `name` argument in {sys.version}")

        task = self.loop.create_task(coro, **kwargs)
        task.add_done_callback(self._task_cb)
        self._tasks.append(task)
        return task
