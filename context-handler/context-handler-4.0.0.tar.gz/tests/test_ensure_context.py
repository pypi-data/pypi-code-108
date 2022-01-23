import pytest

from context_handler import context_factory, ensure_context, exc, context_class
from context_handler._datastructures import AbstractAsyncContext, AbstractSyncContext
from context_handler.context import AsyncContext, SyncContext
from tests.mocks import client, has_state, instance, provider

sync_factory = context_factory(provider.MockProvider, SyncContext)
async_factory = context_factory(provider.MockAsyncProvider, AsyncContext)

@context_class
class MockInstanceMethod(instance.MockInstance):
    @ensure_context.method
    def instance_func(self):
        provider = self.context.get_provider()
        assert not provider.is_closed(self.context.client)

    @ensure_context.async_method
    async def async_instance_func(self):
        provider = self.context.get_provider()
        assert not provider.is_closed(self.context.client)


@ensure_context.sync_context.view(
    factory=sync_factory,
)
def view_func(request: has_state.HasState):
    context = sync_factory(request)
    provider = context.get_provider()
    assert not provider.is_closed(context.client)
    return context


@ensure_context.sync_context
def context_func(context: AbstractSyncContext[client.MockClient]):
    provider = context.get_provider()
    assert not provider.is_closed(context.client)


@ensure_context.sync_context
def err_context_func(context: AbstractSyncContext[client.MockClient]):
    raise Exception


@ensure_context.sync_context
async def aio_context_func(context: AbstractSyncContext[client.MockClient]):
    provider = context.get_provider()
    assert not provider.is_closed(context.client)


@ensure_context.sync_context
async def asyncgen_context_func(
    context: AbstractSyncContext[client.MockClient],
):
    yield
    provider = context.get_provider()
    assert not provider.is_closed(context.client)


@ensure_context.async_context.view(
    factory=async_factory,
)
async def async_view_func(request: has_state.HasState):
    context = async_factory(request)
    provider = context.get_provider()
    assert not provider.is_closed(context.client)
    return context


@ensure_context.async_context
async def async_context_func(context: AbstractAsyncContext[client.MockClient]):
    provider = context.get_provider()
    assert not provider.is_closed(context.client)


@ensure_context.async_context
async def err_async_context_func(
    context: AbstractAsyncContext[client.MockClient],
):
    raise Exception


@ensure_context.async_context
async def asyncgen_async_context_func(
    context: AbstractAsyncContext[client.MockClient],
):
    yield
    provider = context.get_provider()
    assert not provider.is_closed(context.client)


@pytest.mark.asyncio
async def test_ensure_context_sync(sync_state: has_state.HasState):
    context = sync_factory(sync_state)
    mock_instance = MockInstanceMethod(context)
    with context.open():
        assert view_func(sync_state) is context
        context_func(context)
        mock_instance.instance_func()
        await aio_context_func(context)
        async for _ in asyncgen_context_func(context):
            pass
        with pytest.raises(Exception):
            err_context_func(context)
    with pytest.raises(exc.ContextNotInitializedError):
        context.client


@pytest.mark.asyncio
async def test_ensure_context_async(async_state: has_state.HasState):
    context = async_factory(async_state)
    mock_instance = MockInstanceMethod(context)
    async with context.open():
        assert await async_view_func(async_state) is context
        await async_context_func(context)
        await mock_instance.async_instance_func()
        async for _ in asyncgen_async_context_func(context):
            pass
        with pytest.raises(Exception):
            await err_async_context_func(context)
        with pytest.raises(TypeError):

            @ensure_context._async_context
            def async_context_invalid_func(
                context: AbstractAsyncContext[client.MockClient],
            ):
                return

    with pytest.raises(exc.ContextNotInitializedError):
        context.client
