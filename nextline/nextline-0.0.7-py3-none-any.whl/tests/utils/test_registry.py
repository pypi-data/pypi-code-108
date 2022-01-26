import sys
import asyncio

import pytest

from nextline.utils import Registry

##__________________________________________________________________||
nitems = [0, 1, 2, 50]
nsubscribers = [0, 1, 2, 70]


@pytest.mark.skipif(sys.version_info < (3, 9), reason="asyncio.to_thread() ")
@pytest.mark.parametrize("nitems", nitems)
@pytest.mark.parametrize("nsubscribers", nsubscribers)
@pytest.mark.parametrize("thread", [True, False])
@pytest.mark.parametrize("close_register", [True, False])
@pytest.mark.asyncio
async def test_one(close_register, thread, nsubscribers, nitems):
    async def subscribe(registry, register_key):
        ret = []
        async for y in registry.subscribe(register_key):
            ret.append(y)
        return ret

    def register(registry, register_key, items):
        registry.open_register(register_key)
        assert registry.get(register_key) is None
        for item in items:
            registry.register(register_key, item)
            assert registry.get(register_key) == item
        if close_register:
            registry.close_register(register_key)

    async def aregister(registry, register_key, items):
        return register(registry, register_key, items)

    registry = Registry()

    register_key = "item"
    items = [f"{register_key}-{i+1}" for i in range(nitems)]

    # subscribe
    tasks_subscribe = []
    for i in range(nsubscribers):
        task = asyncio.create_task(subscribe(registry, register_key))
        tasks_subscribe.append(task)

    # register
    if thread:
        coro = asyncio.to_thread(register, registry, register_key, items)
    else:
        coro = aregister(registry, register_key, items)
    task_register = asyncio.create_task(coro)

    await asyncio.gather(task_register)

    task_close = asyncio.create_task(registry.close())

    results = await asyncio.gather(*tasks_subscribe, task_close)
    expected = items
    actuals = results[:nsubscribers]
    for actual in actuals:
        assert actual == expected


##__________________________________________________________________||
nitems = [0, 1, 2, 10]
nsubscribers = [0, 1, 2, 70]


@pytest.mark.skipif(sys.version_info < (3, 9), reason="asyncio.to_thread() ")
@pytest.mark.parametrize("nitems", nitems)
@pytest.mark.parametrize("nsubscribers", nsubscribers)
@pytest.mark.parametrize("thread", [True, False])
@pytest.mark.parametrize("close_register", [True, False])
@pytest.mark.asyncio
async def test_list(close_register, thread, nsubscribers, nitems):
    async def subscribe(registry, register_key):
        ret = []
        async for y in registry.subscribe(register_key):
            ret.append(y)
        return ret

    def register(registry, register_key, items):
        registry.open_register_list(register_key)
        assert registry.get(register_key) == []
        for i, item in enumerate(items):
            registry.register_list_item(register_key, item)
            assert registry.get(register_key) == items[: i + 1]
        for i, item in enumerate(items):
            registry.deregister_list_item(register_key, item)
            assert registry.get(register_key) == items[i + 1 :]
        if close_register:
            registry.close_register(register_key)

    async def aregister(registry, register_key, items):
        return register(registry, register_key, items)

    registry = Registry()

    register_key = "item"
    items = [f"{register_key}-{i+1}" for i in range(nitems)]

    # subscribe
    tasks_subscribe = []
    for i in range(nsubscribers):
        task = asyncio.create_task(subscribe(registry, register_key))
        tasks_subscribe.append(task)

    # register
    if thread:
        coro = asyncio.to_thread(register, registry, register_key, items)
    else:
        coro = aregister(registry, register_key, items)
    task_register = asyncio.create_task(coro)

    await asyncio.gather(task_register)

    task_close = asyncio.create_task(registry.close())

    results = await asyncio.gather(*tasks_subscribe, task_close)
    expected = [items[: i + 1] for i in range(len(items))]
    expected.extend([items[i + 1 :] for i in range(len(items))])
    actuals = results[:nsubscribers]
    for actual in actuals:
        assert actual == expected


##__________________________________________________________________||
