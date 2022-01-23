import pytest

from context_handler import (
    ImmutableAsyncProvider,
    ImmutableSyncProvider,
    StateWrapper,
    SyncContext,
)
from context_handler._datastructures import AbstractSyncContextFactory, ContextGetter
from tests.mocks.instance import MockInstance

from .mocks import has_state
from .mocks import provider as mock_provider


def make_state_wrapper_test(has_state_instance):
    state_wrapper = StateWrapper(has_state_instance)
    assert (state_wrapper.get("test"), state_wrapper.app_get("test")) == (
        None,
        None,
    )

    STATE_SENTINEL = object()
    APP_SENTINEL = object()
    state_wrapper.set("test", STATE_SENTINEL)
    state_wrapper.app_set("test", APP_SENTINEL)
    assert (state_wrapper.get("test"), state_wrapper.app_get("test")) == (
        STATE_SENTINEL,
        APP_SENTINEL,
    )


def test_state_wrapper_with_state_attr():
    make_state_wrapper_test(has_state.HasState())


def test_state_wrapper_with_context_attr():
    make_state_wrapper_test(has_state.HasContext())


def test_state_wrapper_with_ctx_attr():
    make_state_wrapper_test(has_state.HasCtx())


def test_context_getter(
    sync_state: has_state.HasState,
    sync_factory: AbstractSyncContextFactory,
):
    instance_getter = ContextGetter(
        ContextGetter.ArgType.INSTANCE, context_attr_name="context"
    )
    context_getter = ContextGetter(ContextGetter.ArgType.CONTEXT)
    state_getter = ContextGetter(
        ContextGetter.ArgType.HAS_STATE,
        _factory=sync_factory,
    )

    context = state_getter.get(sync_state)
    assert isinstance(context, SyncContext)
    assert isinstance(instance_getter.get(MockInstance(context)), SyncContext)
    assert isinstance(context_getter.get(context), SyncContext)


def test_immutable_sync_provider(provider: mock_provider.MockProvider):
    immutable_provider = ImmutableSyncProvider(provider)
    assert ImmutableSyncProvider.state_name == "immutable_sync_provider"
    with pytest.raises(AttributeError):
        immutable_provider.state_name
    with pytest.raises(AttributeError):
        immutable_provider._provider
    with immutable_provider.acquire() as client:
        assert (
            immutable_provider.is_closed(client)
            == provider.is_closed(client)
            == False
        )
    assert (
        immutable_provider.is_closed(client)
        == provider.is_closed(client)
        == True
    )
    assert immutable_provider.get_state_name() == provider.state_name


@pytest.mark.asyncio
async def test_immutable_async_provider(
    async_provider: mock_provider.MockAsyncProvider,
):
    immutable_provider = ImmutableAsyncProvider(async_provider)
    assert ImmutableAsyncProvider.state_name == "immutable_async_provider"
    with pytest.raises(AttributeError):
        immutable_provider.state_name
    with pytest.raises(AttributeError):
        immutable_provider._provider
    async with immutable_provider.acquire() as client:
        assert (
            immutable_provider.is_closed(client)
            == async_provider.is_closed(client)
            == False
        )
    assert (
        immutable_provider.is_closed(client)
        == async_provider.is_closed(client)
        == True
    )
    assert immutable_provider.get_state_name() == async_provider.state_name
