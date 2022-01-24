# -*- coding: utf-8 -*-
import asyncio
from unittest import mock

import pytest
from patchwork.core import Task, AsyncSubscriber

from patchwork.node.core import TaskRouter
from patchwork.node.core.exceptions import TaskRetry, TaskDrop, TaskFatal, TaskControlException
from patchwork.node.executor import BaseExecutor
from tests.router import test_router, CustomException, UnknownTCE


class WorkerMock:

    debug = True

    def __init__(self):
        self.get_publisher = mock.Mock(return_value=mock.AsyncMock())

    @property
    def event_loop(self):
        return asyncio.get_running_loop()


@pytest.fixture
async def worker_mock():
    return WorkerMock()


@pytest.fixture
async def executor(worker_mock):
    executor = BaseExecutor(parent=worker_mock)
    executor.add_router(test_router)
    await executor.run()
    yield executor
    await executor.terminate()


@pytest.fixture
def subscriber():
    return mock.AsyncMock(spec=AsyncSubscriber)


@pytest.mark.asyncio
async def test_task_success(executor, subscriber):
    task = Task(task_type='noop')
    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)
    await fut
    subscriber.commit.assert_called_once_with(task)


@pytest.mark.asyncio
async def test_task_processor_error(executor, subscriber):
    executor.retry = mock.AsyncMock()

    task = Task(task_type='exception')
    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)

    with pytest.raises(CustomException):
        await fut

    subscriber.commit.assert_called_once_with(task)
    executor.retry.assert_called_once()


@pytest.mark.asyncio
async def test_task_retry(executor, subscriber):

    task = Task(task_type='retry')
    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)

    with pytest.raises(TaskRetry):
        # exception from task processor should be passed to task future
        await fut

    subscriber.commit.assert_called_once_with(task)
    executor.worker.get_publisher.assert_called_once()


@pytest.mark.asyncio
async def test_task_drop(executor, subscriber):

    executor.retry = mock.AsyncMock()
    executor.backoff_task = mock.AsyncMock()

    task = Task(task_type='drop')
    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)

    with pytest.raises(TaskDrop):
        # exception from task processor should be passed to task future
        await fut

    subscriber.commit.assert_called_once_with(task)
    assert not executor.worker.get_publisher.called
    assert not executor.retry.called
    assert not executor.backoff_task.called


@pytest.mark.asyncio
async def test_task_fatal(executor, subscriber):

    executor.retry = mock.AsyncMock()
    executor.backoff_task = mock.AsyncMock()

    task = Task(task_type='fatal')
    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)

    with pytest.raises(TaskFatal):
        # exception from task processor should be passed to task future
        await fut

    subscriber.commit.assert_called_once_with(task)
    executor.backoff_task.assert_called_with(task, reason='Task processing fatal error')

    assert not executor.worker.get_publisher.called
    assert not executor.retry.called


@pytest.mark.asyncio
async def test_task_unknown_task_control_exc(executor, subscriber):

    executor.harakiri = mock.Mock()
    executor.retry = mock.AsyncMock()

    task = Task(task_type='unknown_tce')
    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)

    await fut

    assert not subscriber.commit.called, \
        "on executor internal error no commit should be done"

    assert not executor.retry.called, \
        "on executor internal error no retry should be done"

    executor.harakiri.assert_called_once()


@pytest.mark.asyncio
async def test_task_exc_handler_retry(executor, subscriber):
    async def custom_exc_handler(*args):
        raise TaskRetry()

    executor.retry = mock.AsyncMock()

    task = Task(task_type='exception')
    executor.add_exception_handler(CustomException, custom_exc_handler)

    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)
    with pytest.raises(CustomException):
        await fut

    executor.retry.assert_called_with(task, not_before=None)
    subscriber.commit.assert_called_once_with(task)


@pytest.mark.asyncio
async def test_task_exc_handler_fatal(executor, subscriber):
    async def custom_exc_handler(*args):
        raise TaskFatal()

    executor.backoff_task = mock.AsyncMock()

    task = Task(task_type='exception')
    executor.add_exception_handler(CustomException, custom_exc_handler)

    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)
    with pytest.raises(CustomException):
        await fut

    executor.backoff_task.assert_called_with(task, reason='Task processing fatal error')
    subscriber.commit.assert_called_once_with(task)


@pytest.mark.asyncio
async def test_task_exc_handler_drop(executor, subscriber):
    async def custom_exc_handler(*args):
        raise TaskDrop()

    task = Task(task_type='exception')
    executor.add_exception_handler(CustomException, custom_exc_handler)

    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)
    with pytest.raises(CustomException):
        await fut

    subscriber.commit.assert_called_once_with(task)


@pytest.mark.asyncio
async def test_task_exc_handler_unknown_control_exc(executor, subscriber):
    async def custom_exc_handler(*args):
        raise UnknownTCE()

    executor.harakiri = mock.Mock()
    task = Task(task_type='exception')
    executor.add_exception_handler(CustomException, custom_exc_handler)

    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)
    await fut

    executor.harakiri.assert_called_once()


@pytest.mark.asyncio
async def test_task_exc_handler_error(executor, subscriber):
    async def custom_exc_handler(*args):
        raise Exception()

    executor.harakiri = mock.Mock()

    task = Task(task_type='exception')
    executor.add_exception_handler(CustomException, custom_exc_handler)

    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)
    await fut

    executor.harakiri.assert_called_once()


@pytest.mark.asyncio
async def test_task_exc_handler_success(executor, subscriber):
    async def custom_exc_handler(*args):
        pass

    task = Task(task_type='exception')
    executor.add_exception_handler(CustomException, custom_exc_handler)

    fut = asyncio.Future()
    await executor.handle(task, subscriber, fut)
    with pytest.raises(CustomException):
        await fut

    subscriber.commit.assert_called_once_with(task)


def test_include_routers_order():
    executor = BaseExecutor(parent=worker_mock)
    routerT = TaskRouter()
    routerTa = TaskRouter()
    routerTask = TaskRouter()

    executor.add_router(routerT, prefix='T')
    executor.add_router(routerTask, prefix='Task')
    executor.add_router(routerTa, prefix='Ta')

    assert executor._routers == [
        ('Task', routerTask),
        ('Ta', routerTa),
        ('T', routerT)
    ]
