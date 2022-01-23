import pytest

from context_handler import AsyncContext, SyncContext, context_factory

from .mocks import has_state
from .mocks.provider import MockAsyncProvider, MockProvider


@pytest.fixture
def provider() -> MockProvider:
    return MockProvider()


@pytest.fixture(scope="function")
def async_provider() -> MockAsyncProvider:
    return MockAsyncProvider()


@pytest.fixture(scope="function")
def sync_state(provider: MockProvider):
    state_handler = has_state.HasState()
    setattr(state_handler.app.state, provider.state_name, provider)
    return state_handler


@pytest.fixture(scope="function")
def async_state(async_provider: MockAsyncProvider):
    state_handler = has_state.HasState()
    setattr(state_handler.app.state, async_provider.state_name, async_provider)
    return state_handler


@pytest.fixture(scope="function")
def sync_factory():
    return context_factory(MockProvider, SyncContext)


@pytest.fixture(scope="function")
def async_factory():
    return context_factory(MockAsyncProvider, AsyncContext)
