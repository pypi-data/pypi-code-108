from __future__ import annotations
import typing as t
import asyncio
from contextlib import suppress, AsyncExitStack, asynccontextmanager

import pytest
from codestare.async_utils import TaskNursery, CoroutineWrapper

pytestmark = pytest.mark.asyncio


class MockWrapper(CoroutineWrapper):
    def __init__(self, range: int | None = 20):
        self.value = None
        self.range = range
        super().__init__(coroutine=self._run())

    async def _run(self):
        if self.range is not None:
            for i in range(self.range):
                self.value = i

        else:
            while True:
                self.value += 1


@pytest.fixture
async def nursery(request):
    callback_ran = False

    async def callback():
        nonlocal callback_ran
        callback_ran = True

    nursery = request.param() if hasattr(request, 'param') else TaskNursery()
    nursery.add_sentinel_callback(callback())
    yield nursery

    if any(t.cancelled() for t in nursery._tasks):
        assert callback_ran


@pytest.mark.parametrize('future', [MockWrapper()])
async def test_nursery(future, nursery):
    callback_called = False

    def callback(task):
        nonlocal callback_called
        callback_called = True
        print(f"Callback called for {task}")

    task = nursery.create_task(future)
    task.add_done_callback(callback)
    task.add_done_callback(lambda _: nursery.trigger_sentinel.set())

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task

    assert callback_called


class MockNursery(TaskNursery):
    def __init__(self):
        super().__init__()
        self.exit_stack = AsyncExitStack()
        self._task = None
        self.add_sentinel_callback(self.exit_stack.aclose())
        self._context: t.AsyncContextManager = self.__make_context()

    def run(self):
        if not self._task:
            self._task = self.create_task(MockWrapper(range=None))
            self._task.add_done_callback(lambda _: self.trigger_sentinel.set())

        return self._task

    @asynccontextmanager
    async def __make_context(self):
        task = self.run()
        yield
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    def __aenter__(self):
        return self._context.__aenter__()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        return self._context.__aexit__(exc_type, exc_val, exc_tb)


@pytest.mark.parametrize('nursery', [MockNursery], indirect=True)
async def test_exit_stack(nursery: MockNursery):
    value = None

    @asynccontextmanager
    async def test_context_manager():
        nonlocal value
        value = True
        yield
        value = False

    async with nursery:
        await nursery.exit_stack.enter_async_context(test_context_manager())

    assert nursery.run().cancelled()
    assert nursery.trigger_sentinel.is_set()
    await asyncio.sleep(0)
    assert value is not None, "context was not entered"
    assert value is False, "context was not exited"
