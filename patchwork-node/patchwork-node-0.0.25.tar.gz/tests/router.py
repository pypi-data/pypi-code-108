# -*- coding: utf-8 -*-
from patchwork.core import Task

from patchwork.node.core import TaskRouter
from patchwork.node.core.exceptions import TaskRetry, TaskFatal, TaskDrop, TaskControlException


class CustomException(Exception):
    pass


test_router = TaskRouter()


class UnknownTCE(TaskControlException):
    pass


@test_router.on('noop')
async def processor_noop():
    return None


@test_router.on('exception')
async def processor_exception():
    raise CustomException()


@test_router.on('retry')
async def processor_retry():
    raise TaskRetry()


@test_router.on('fatal')
async def processor_fatal():
    raise TaskFatal()


@test_router.on('drop')
async def processor_drop():
    raise TaskDrop()


@test_router.on('unknown_tce')
async def processor_drop():
    raise UnknownTCE()
