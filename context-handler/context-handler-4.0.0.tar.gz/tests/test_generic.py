import pytest

from context_handler import generic
from context_handler.context import AsyncContext, SyncContext
from tests.mocks import client, has_state, provider


@pytest.mark.asyncio
async def test_async_generic_factory_should_return_async_context_with_client(
    async_state: has_state.HasState,
):
    factory = generic.AsyncGenericFactory[
        provider.MockAsyncProvider, provider.MockClient
    ](async_state)

    context = factory.get()
    async with context.open():

        assert isinstance(context, AsyncContext)
        assert isinstance(context.client, client.MockClient)


def test_sync_generic_factory_should_return_sync_context_with_client(
    sync_state: has_state.HasState,
):
    factory = generic.GenericFactory[
        provider.MockProvider, provider.MockClient
    ](sync_state)

    context = factory.get()
    with context.open():

        assert isinstance(context, SyncContext)
        assert isinstance(context.client, client.MockClient)
