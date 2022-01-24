# -*- coding: utf-8 -*-
import asyncio

import pytest

from patchwork.node.executor.unit import InlineUnit


@pytest.fixture
async def unit():
    unit = InlineUnit(parent=None)
    await unit.run()
    yield unit
    await unit.terminate()


@pytest.mark.asyncio
async def test_usecase(unit):

    assert unit.is_running
    assert not unit.busy.value

    event = asyncio.Event()
    task_entered = asyncio.Event()

    async def task():
        task_entered.set()
        await event.wait()

    await unit.submit(task())

    # await until processing unit starts task processing
    await task_entered.wait()

    assert unit.busy.value
    event.set()

    # await until processing completes
    await unit.busy.wait_for(False)

    assert not unit.busy.value


@pytest.mark.asyncio
async def test_task_result(unit):
    class Result:
        pass

    async def task(arg):
        return arg

    fut = await unit.submit(task(Result))
    await fut

    assert fut.done()
    assert fut.result() == Result


@pytest.mark.asyncio
async def test_task_exception(unit):

    class CustomException(Exception):
        pass

    async def task():
        raise CustomException()

    fut = await unit.submit(task())

    with pytest.raises(CustomException):
        await fut
