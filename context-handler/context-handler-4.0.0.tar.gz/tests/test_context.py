import pytest

from context_handler import exc
from context_handler._datastructures import (
    AbstractAsyncContextFactory,
    AbstractSyncContextFactory,
    ImmutableAsyncProvider,
    ImmutableSyncProvider,
)
from tests.mocks import client, has_state


def test_synccontext(
    sync_state: has_state.HasState,
    sync_factory: AbstractSyncContextFactory[client.MockClient],
):
    context = sync_factory(sync_state)
    provider = context.get_provider()
    assert isinstance(provider, ImmutableSyncProvider)
    with context.open():
        with context.begin() as client:
            assert not provider.is_closed(client)
        assert not provider.is_closed(context.client)
    assert provider.is_closed(client)
    with pytest.raises(exc.ContextNotInitializedError):
        context.client
    with context.begin() as cli:
        assert not provider.is_closed(cli)
        with pytest.raises(exc.ContextNotInitializedError):
            context.client


@pytest.mark.asyncio
async def test_asynccontext(
    async_state: has_state.HasState,
    async_factory: AbstractAsyncContextFactory[client.MockClient],
):
    context = async_factory(async_state)
    provider = context.get_provider()
    assert isinstance(provider, ImmutableAsyncProvider)
    async with context.open():
        async with context.begin() as client:
            assert not provider.is_closed(client)
        assert not provider.is_closed(context.client)
    assert provider.is_closed(client)
    with pytest.raises(exc.ContextNotInitializedError):
        context.client
    async with context.begin() as cli:
        assert not provider.is_closed(cli)
        with pytest.raises(exc.ContextNotInitializedError):
            context.client
