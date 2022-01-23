from contextlib import asynccontextmanager, contextmanager

from .client import MockClient


class MockProvider:
    state_name = "mock_provider"

    def is_closed(self, client: MockClient):
        return client.is_closed

    def close_client(self, client: MockClient):
        return client.close()

    @contextmanager
    def acquire(self):
        client = MockClient(False)
        yield client
        self.close_client(client)


class MockAsyncProvider:
    state_name = "mock_async_provider"

    def is_closed(self, client: MockClient):
        return client.is_closed

    async def close_client(self, client: MockClient):
        return client.close()

    @asynccontextmanager
    async def acquire(self):
        client = MockClient(False)
        yield client
        await self.close_client(client)
