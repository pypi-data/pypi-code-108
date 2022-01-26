import sys
import asyncio

import pytest
from unittest.mock import AsyncMock

from nextline.utils import CoroutineRunner


##__________________________________________________________________||
@pytest.fixture()
async def obj():
    y = CoroutineRunner()
    yield y


@pytest.mark.asyncio
async def test_repr(obj):
    repr(obj)


@pytest.mark.asyncio
async def test_async(obj):
    afunc = AsyncMock()
    coro = afunc()
    task = obj.run(coro)
    await task
    assert 1 == afunc.await_count


@pytest.mark.skipif(sys.version_info < (3, 9), reason="asyncio.to_thread() ")
@pytest.mark.asyncio
async def test_thread(obj):
    def run():
        afunc = AsyncMock()
        coro = afunc()
        ret = obj.run(coro)
        assert ret is None
        assert 1 == afunc.await_count

    await asyncio.to_thread(run)


##__________________________________________________________________||
