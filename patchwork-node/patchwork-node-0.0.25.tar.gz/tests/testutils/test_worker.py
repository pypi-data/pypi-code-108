# -*- coding: utf-8 -*-
import pytest
from patchwork.core import AsyncPublisher

from patchwork.node import PatchworkWorker
from patchwork.node.core import TaskRouter
from patchwork.node.core.dependencies import GetPublisher
from patchwork.node.testutils import TestWorker


@pytest.fixture
def example_app():
    app = PatchworkWorker(settings={
        'subscriber': {
            'engine': 'patchwork.core.client.local:AsyncLocalSubscriber',
            'queue_names': ['test']
        },
        'publisher': {
            'engine': 'patchwork.core.client.local:AsyncLocalPublisher'
        }
    })

    router = TaskRouter()
    app.include_router(router)

    @router.on('foo')
    async def foo(publisher: AsyncPublisher = GetPublisher()):
        await publisher.send(b'test data', task_type='bar', queue_name='test')

    @router.on('bar')
    async def bar():
        pass

    return app


@pytest.mark.asyncio
async def test_worker_single_task(example_app):
    async with TestWorker(example_app) as worker:

        async with worker.catch_tasks() as tasks:
            await worker.send(b'data', task_type='bar', queue_name='test')

        tasks.assert_count(1)
        tasks.assert_processed({
            'task_type': 'bar',
            'payload': b'data'
        })


@pytest.mark.asyncio
async def test_worker_tasks_sequence(example_app):
    async with TestWorker(example_app) as worker:

        async with worker.catch_tasks() as tasks:
            # note: foo will send a bar task
            await worker.send(b'data', task_type='foo', queue_name='test')

        tasks.assert_count(2)
        tasks.assert_processed({
            'task_type': 'foo',
            'payload': b'data'
        })
        tasks.assert_processed({
            'task_type': 'bar',
            'payload': b'test data'
        })


@pytest.mark.asyncio
async def test_wait_until(example_app):
    async with TestWorker(example_app) as worker:

        await worker.send(b'data', task_type='foo', queue_name='test')

        await worker.wait_until({
            'task_type': 'bar',
            'payload': b'test data'
        })
