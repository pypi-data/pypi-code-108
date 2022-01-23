import pytest

from context_handler import AsyncContext, SyncContext, context_factory, exc
from tests.mocks import has_state, provider


def test_sync_factory(
    sync_state: has_state.HasState,
):
    sync_factory = context_factory(provider.MockProvider, SyncContext)
    assert not sync_factory.has_active_context(sync_state)
    context = sync_factory(sync_state)
    context_next_call = sync_factory(sync_state)
    assert isinstance(context, SyncContext)
    assert context is context_next_call
    assert sync_factory.has_active_context(sync_state)
    assert isinstance(
        sync_factory.from_provider(provider.MockProvider), SyncContext
    )


def test_async_factory(async_state: has_state.HasState):
    async_factory = context_factory(provider.MockAsyncProvider, AsyncContext)
    assert not async_factory.has_active_context(async_state)
    context = async_factory(async_state)
    context_next_call = async_factory(async_state)
    assert isinstance(context, AsyncContext)
    assert context is context_next_call
    assert async_factory.has_active_context(async_state)
    assert isinstance(
        async_factory.from_provider(provider.MockAsyncProvider), AsyncContext
    )


def test_factory_with_invalid_state():
    state_handler = has_state.HasState()
    async_factory = context_factory(provider.MockAsyncProvider, AsyncContext)
    sync_factory = context_factory(provider.MockProvider, SyncContext)
    for item in (sync_factory, async_factory):
        with pytest.raises(exc.NoProviderInState):
            item(state_handler)
