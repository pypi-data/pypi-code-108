import asyncio
import logging
from asyncio.tasks import Task
from contextlib import suppress
from inspect import isasyncgenfunction
from signal import SIGINT, SIGTERM
from typing import Any, AsyncIterator, Callable, Final, Mapping, Optional

__all__ = ('ContextFunction', 'Runner')

ContextFunction = Callable[..., AsyncIterator[None]]

logger = logging.getLogger('runner')


class Runner:

    def __init__(
        self, context_function: ContextFunction, debug: bool = False,
        **kwargs: Any
    ) -> None:
        if not isasyncgenfunction(context_function):
            raise RuntimeError('Argument is not async generator')
        self._context_function: Final[ContextFunction] = context_function
        self._kwargs: Final[Mapping[str, Any]] = kwargs
        self._debug: Final[bool] = debug
        self._wait_task: Optional[Task[None]] = None
        self._started: bool = False
        self._stopped: bool = False

    async def _run(self) -> None:
        assert not self._started
        assert not self._stopped
        self._started = True
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(SIGINT, self._signal_handler, SIGINT.name)
        loop.add_signal_handler(SIGTERM, self._signal_handler, SIGTERM.name)
        logger.debug('Enter wait loop')
        iterator = self._context_function(self, **self._kwargs).__aiter__()
        await iterator.__anext__()
        self._wait_task = asyncio.create_task(self._wait())
        with suppress(asyncio.CancelledError):
            await self._wait_task
        logger.debug('Waiting finished')
        try:
            await iterator.__anext__()
        except StopAsyncIteration:
            pass
        else:
            raise RuntimeError(f'{iterator!r} has more than one \'yield\'')

    async def _wait(self) -> None:
        assert self._started
        assert not self._stopped
        while not self._stopped:
            await asyncio.sleep(3600)

    def _signal_handler(self, signal_name: str) -> None:
        logger.debug('Received signal %s', signal_name)
        self.stop()

    def stop(self) -> None:
        if not self._started:
            raise RuntimeError('Not started')
        if self._stopped:
            raise RuntimeError('Already stopped')
        if self._wait_task is None:
            raise RuntimeError('Wait task not spawned')
        self._stopped = True
        self._wait_task.cancel()

    def run(self) -> None:
        if self._started:
            raise RuntimeError('Already started')
        asyncio.run(self._run(), debug=self._debug)
