# -*- coding: utf-8 -*-
import pytest

from patchwork.node.executor import BaseExecutor
from patchwork.node.executor.base import default_task_exception_handler


@pytest.mark.asyncio
async def test_no_custom_regular_exception():
    executor = BaseExecutor(parent=None)

    handlers = executor._get_exception_handler(Exception())
    assert list(handlers) == [default_task_exception_handler]


@pytest.mark.asyncio
async def test_custom_same_level_handler_regular_exception():
    executor = BaseExecutor(parent=None)

    async def handler():
        pass

    executor.add_exception_handler(Exception, handler)

    handlers = executor._get_exception_handler(Exception())
    assert list(handlers) == [handler, default_task_exception_handler]


@pytest.mark.asyncio
async def test_subclassing_order():

    executor = BaseExecutor(parent=None)

    class CustomException(Exception):
        pass

    class SubCustomException(CustomException):
        pass

    async def custom_exc_handler():
        pass

    async def generic_handler():
        pass

    executor.add_exception_handler(CustomException, custom_exc_handler)
    executor.add_exception_handler(Exception, generic_handler)

    handlers = executor._get_exception_handler(SubCustomException())

    # custom_exc_handler should be called before any handler registered for Exception, because
    # it's more specific - tied to CustomException which is better matching raised exception
    assert list(handlers) == [custom_exc_handler, generic_handler, default_task_exception_handler]
