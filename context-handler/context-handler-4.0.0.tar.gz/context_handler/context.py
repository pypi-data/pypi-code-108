import typing
from contextlib import asynccontextmanager, contextmanager

from context_handler import _datastructures, exc

T = typing.TypeVar('T')


class SyncContext(typing.Generic[T]):
    provider = _datastructures.ImmutableWrapper(
        '_provider', _datastructures.ImmutableSyncProvider[T]
    )

    def __init__(self, provider: _datastructures.Provider[T]) -> None:
        self._provider = provider
        self._inside_ctx = False
        self._client: typing.Optional[T] = None

    def in_context(self):
        if self._client is None:
            return False
        return not self.provider.is_closed(self._client)

    @property
    def client(self) -> T:
        if self._client is None:
            raise exc.ContextNotInitializedError
        return self._client

    def _set_client(self, client: T):
        self._client = client

    def _reset_context(self):
        if self._client is None:
            return
        if not self.provider.is_closed(self._client):
            self.provider.close_client(self._client)
        self._set_client(None)
        self._inside_ctx = False

    def _open_context(self):
        error = None
        with self.provider.acquire() as client:
            self._set_client(client)
            self._inside_ctx = True
            try:
                yield
            except Exception as err:
                error = err
        self._reset_context()
        if error is not None:
            raise error

    def _begin_context(self):
        error = None
        with self.provider.acquire() as client:
            try:
                yield client
            except Exception as err:
                error = err
        if error is not None:
            raise error

    def _contexted_begin(self):
        yield self.client

    def _contexted_open(self):
        yield

    @contextmanager
    def begin(self):
        if self.in_context():
            return self._contexted_begin()
        return self._begin_context()

    @contextmanager
    def open(self):
        if self.in_context():
            return self._contexted_open()
        return self._open_context()

    def get_provider(self) -> _datastructures.ImmutableSyncProvider[T]:
        return self.provider


class AsyncContext(typing.Generic[T]):
    provider = _datastructures.ImmutableWrapper(
        '_provider', _datastructures.ImmutableAsyncProvider[T]
    )

    def __init__(self, provider: _datastructures.AsyncProvider[T]) -> None:
        self._provider = provider
        self._inside_ctx = False
        self._client: typing.Optional[T] = None

    def in_context(self):
        if self._client is None:
            return False
        return not self.provider.is_closed(self._client)

    @property
    def client(self) -> T:
        if self._client is None:
            raise exc.ContextNotInitializedError
        return self._client

    def _set_client(self, client: T):
        self._client = client

    async def _reset_context(self):
        if self._client is None:
            return
        if not self.provider.is_closed(self._client):
            await self.provider.close_client(self._client)
        self._set_client(None)
        self._inside_ctx = False

    async def _open_context(self):
        error = None
        async with self.provider.acquire() as client:
            self._set_client(client)
            self._inside_ctx = True
            try:
                yield
            except Exception as err:
                error = err
        await self._reset_context()
        if error is not None:
            raise error

    async def _begin_context(self):
        error = None
        async with self.provider.acquire() as client:
            try:
                yield client
            except Exception as err:
                error = err
        if error is not None:
            raise error

    async def _contexted_begin(self):
        yield self.client

    async def _contexted_open(self):
        yield

    @asynccontextmanager
    def begin(self):
        if self.in_context():
            return self._contexted_begin()
        return self._begin_context()

    @asynccontextmanager
    def open(self):
        if self.in_context():
            return self._contexted_open()
        return self._open_context()

    def get_provider(self) -> _datastructures.ImmutableAsyncProvider[T]:
        return self.provider
