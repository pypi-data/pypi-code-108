# -*- coding: utf-8 -*-
from dataclasses import dataclass
from unittest.mock import Mock

import betterproto
import pytest
from google.protobuf.wrappers_pb2 import StringValue
from patchwork.core import Task, AsyncSubscriber

from patchwork.node.core import TaskRouter
from patchwork.node.core.exceptions import TaskDrop
from tests.message_pb2 import Test


@pytest.mark.asyncio
async def test_task_dependency():
    router = TaskRouter()
    worker = Mock()
    router.bind(worker)

    @router.on('test')
    async def processor(task: Task):
        assert task.uuid == 'test-uuid'

    t = Task(uuid='test-uuid', task_type='test')
    r = AsyncSubscriber()
    cr = router.handle(t, r)
    await cr


@pytest.mark.asyncio
async def test_pb_payload_dependency():
    router = TaskRouter()
    worker = Mock()
    router.bind(worker)

    @router.on('test')
    async def processor(data: StringValue):
        assert data.value == 'test-string'

    t = Task(uuid='test-uuid', task_type='test')
    t.payload.Pack(StringValue(value='test-string'))
    r = AsyncSubscriber()
    cr = router.handle(t, r)
    await cr


@pytest.mark.asyncio
async def test_better_pb_payload_dependency():
    router = TaskRouter()
    worker = Mock()
    router.bind(worker)

    @dataclass
    class Test(betterproto.Message):
        """Greeting represents a message you can tell a user."""

        message: str = betterproto.string_field(1)

    @router.on('test')
    async def processor(data: Test):
        assert data.message == 'test-betterproto-message'

    t = Task(uuid='test-uuid', task_type='test')
    t.payload.value = bytes(Test(message='test-betterproto-message'))
    r = AsyncSubscriber()
    cr = router.handle(t, r)
    await cr


@pytest.mark.asyncio
async def test_better_pb_from_regular_pb_payload():
    router = TaskRouter()
    worker = Mock()
    router.bind(worker)

    @dataclass
    class BetterTest(betterproto.Message):
        """Greeting represents a message you can tell a user."""

        message: str = betterproto.string_field(1)

    @router.on('test')
    async def processor(data: BetterTest):
        assert data.message == 'test-betterproto-message'

    t = Task(uuid='test-uuid', task_type='test')
    t.payload.Pack(Test(message='test-betterproto-message'))
    r = AsyncSubscriber()
    cr = router.handle(t, r)
    await cr


@pytest.mark.asyncio
async def test_skip_unknown_task():
    router = TaskRouter(skip_unsupported_tasks=True)
    worker = Mock()
    router.bind(worker)

    t = Task(uuid='test-uuid', task_type='test')
    t.payload.Pack(Test(message='test-betterproto-message'))
    r = AsyncSubscriber()
    with pytest.raises(TaskDrop):
        cr = router.handle(t, r)
