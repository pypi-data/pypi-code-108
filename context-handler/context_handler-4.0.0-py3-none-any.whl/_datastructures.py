import enum
import typing

T = typing.TypeVar('T')


@typing.runtime_checkable
class Provider(typing.Protocol[T]):
    """Client Adapter Interface Accepted by SyncContext"""

    state_name: typing.ClassVar[str]

    def is_closed(self, client: T) -> bool:
        """Returns if client is closed or released"""
        ...

    def close_client(self, client: T) -> None:
        """Closes/releases client"""

    def acquire(self) -> typing.ContextManager[T]:
        """Acquires a client `T` and releases at the end"""
        ...


@typing.runtime_checkable
class AsyncProvider(typing.Protocol[T]):
    """Client Adapter Interface Accepted by AsyncContext"""

    state_name: typing.ClassVar[str]

    def is_closed(self, client: T) -> bool:
        """Returns if client is closed or released"""
        ...

    async def close_client(self, client: T) -> None:
        """Closes/releases client"""
        ...

    def acquire(self) -> typing.AsyncContextManager[T]:
        """Acquires a client `T` and releases at the end"""
        ...


class ImmutableSyncProvider(typing.Generic[T]):
    """Wrapper class to prevent mutating provider"""

    state_name = 'immutable_sync_provider'

    def __init__(self, provider: Provider[T]) -> None:
        self._provider = provider

    def __getattribute__(self, name: str) -> typing.Any:
        allowed = ['get_state_name', 'is_closed', 'close_client', 'acquire']
        if name in allowed:
            return super().__getattribute__(name)
        message = "'{}' object has no attribute '{}'"
        raise AttributeError(
            message.format(ImmutableSyncProvider.__name__, name)
        )

    def get_state_name(self):
        return super().__getattribute__('_provider').state_name

    def is_closed(self, client: T) -> bool:
        return super().__getattribute__('_provider').is_closed(client)

    def close_client(self, client: T) -> None:
        return super().__getattribute__('_provider').close_client(client)

    def acquire(self) -> typing.ContextManager[T]:
        return super().__getattribute__('_provider').acquire()


class ImmutableAsyncProvider(typing.Generic[T]):
    """Wrapper class to prevent mutating provider"""

    state_name = 'immutable_async_provider'

    def __init__(self, provider: AsyncProvider[T]) -> None:
        self._provider = provider

    def __getattribute__(self, name: str) -> typing.Any:
        allowed = ['get_state_name', 'is_closed', 'close_client', 'acquire']
        if name in allowed:
            return super().__getattribute__(name)
        message = "'{}' object has no attribute '{}'"
        raise AttributeError(
            message.format(ImmutableSyncProvider.__name__, name)
        )

    def get_state_name(self):
        return super().__getattribute__('_provider').state_name

    def is_closed(self, client: T) -> bool:
        return super().__getattribute__('_provider').is_closed(client)

    def close_client(self, client: T) -> typing.Coroutine[None, None, None]:
        return super().__getattribute__('_provider').close_client(client)

    def acquire(self) -> typing.AsyncContextManager[T]:
        return super().__getattribute__('_provider').acquire()


@typing.runtime_checkable
class AbstractSyncContext(typing.Protocol[T]):
    provider: 'ImmutableWrapper[ImmutableSyncProvider[T]]'
    _inside_ctx: bool

    def __init__(self, provider: Provider[T]) -> None:
        ...

    def in_context(self) -> bool:
        """Returns if `.open()` or `.begin()` calls where made inside an open context"""
        ...

    @property
    def client(self) -> T:
        """Returns a client instance if context is open"""
        ...

    def open(self) -> typing.ContextManager[None]:
        """Opens context"""
        ...

    def begin(self) -> typing.ContextManager[T]:
        """Returns client from open context or a independent client if no context is open."""
        ...

    def get_provider(self) -> ImmutableSyncProvider[T]:
        """Returns internal provider"""
        ...


@typing.runtime_checkable
class AbstractAsyncContext(typing.Protocol[T]):
    provider: 'ImmutableWrapper[ImmutableAsyncProvider[T]]'
    _inside_ctx: bool

    def __init__(self, provider: AsyncProvider[T]) -> None:
        ...

    def in_context(self) -> bool:
        """Returns if `.open()` or `.begin()` calls where made inside an open context"""
        ...

    @property
    def client(self) -> T:
        """Returns a client instance if context is open"""
        ...

    def open(self) -> typing.AsyncContextManager[None]:
        """Opens context"""
        ...

    def begin(self) -> typing.AsyncContextManager[T]:
        """Returns client from open context or a independent client if no context is open."""
        ...

    def get_provider(self) -> ImmutableAsyncProvider[T]:
        """Returns internal provider"""
        ...


AbstractContext = typing.TypeVar(
    'AbstractContext', AbstractSyncContext, AbstractAsyncContext
)


class _StateApp(typing.Protocol):
    state: typing.Type


class _ContextApp(typing.Protocol):
    context: typing.Type


class _CtxApp(typing.Protocol):
    ctx: typing.Type


class _HasState(typing.Protocol):
    state: typing.Type
    app: '_StateApp'


class _HasContext(typing.Protocol):
    context: typing.Type
    app: '_ContextApp'


class _HasCtx(typing.Protocol):
    ctx: typing.Type
    app: '_CtxApp'


StateApp = typing.Union[_StateApp, _ContextApp, _CtxApp]

HasState = typing.Union[_HasState, _HasContext, _HasCtx]


class StateWrapper:
    _valid_state_attrs = ['state', 'context', 'ctx']

    def __init__(self, has_state: HasState) -> None:
        self.has_state = has_state
        self._validate_instance()
        self._instance_state_attr = self._get_state_attr(self.has_state)
        self._app_state_attr = self._get_state_attr(self.has_state.app)

    def _validate_instance(self):
        if not hasattr(self.has_state, 'app'):
            raise TypeError("State Handler must have 'app' attribute")

    def _get_state_attr(
        self,
        instance: typing.Union[HasState, StateApp],
    ):
        for item in self._valid_state_attrs:
            if hasattr(instance, item):
                return item
        else:
            raise NotImplementedError(
                'State Handler does not have supported state_attrs'
            )

    @property
    def _app_state(self):
        return getattr(self.has_state.app, self._app_state_attr)

    @property
    def _instance_state(self):
        return getattr(self.has_state, self._app_state_attr)

    @staticmethod
    def _get(
        state: type, name: str, _cast: typing.Type[T]
    ) -> typing.Optional[T]:
        return getattr(state, name, None)

    @staticmethod
    def _set(state: type, name: str, val: typing.Any):
        setattr(state, name, val)

    def app_get(
        self, name: str, _cast: typing.Type[T] = typing.Any
    ) -> typing.Optional[T]:
        return self._get(self._app_state, name, _cast)

    def get(
        self, name: str, _cast: typing.Type[T] = typing.Any
    ) -> typing.Optional[T]:
        return self._get(self._instance_state, name, _cast)

    def app_set(self, name: str, val: typing.Any):
        self._set(self._app_state, name, val)

    def set(self, name: str, val: typing.Any):
        self._set(self._instance_state, name, val)


class AbstractSyncContextFactory(typing.Protocol[T]):
    """Creates a Context Factory to handle contexts inside a state"""

    _provider_class: typing.Type[Provider[T]]
    _context_class: typing.Type[AbstractSyncContext[T]]
    _state_name: typing.Optional[str]

    def _get_context(
        self, state_wrapper: StateWrapper
    ) -> AbstractSyncContext[T]:
        """Initializes Context"""
        ...

    def generate_state_name(self) -> str:
        """Returns a key name to store context in state"""
        ...

    def has_active_context(
        self, has_state: HasState
    ) -> typing.Optional[AbstractSyncContext[T]]:
        """Returns context from `has_state` if context in has_state, else None"""

    def _set_active_context(
        self, context: AbstractSyncContext[T], state_wrapper: StateWrapper
    ):
        """Sets context in state"""

    def __call__(self, has_state: HasState) -> AbstractSyncContext[T]:
        """Returns context from has_state if exists or opens new context, stores in state, and then returns state"""
        ...

    def from_provider(self, provider: typing.Type[Provider[T]]):
        """Returns context from a given provider"""


class AbstractAsyncContextFactory(typing.Protocol[T]):
    """Creates a Context Factory to handle contexts inside a state"""

    _provider_class: typing.Type[AsyncProvider[T]]
    _context_class: typing.Type[AbstractAsyncContext[T]]
    _state_name: typing.Optional[str]

    def _get_context(
        self, state_wrapper: StateWrapper
    ) -> AbstractAsyncContext[T]:
        """Initializes Context"""
        ...

    def generate_state_name(self) -> str:
        """Returns a key name to store context in state"""
        ...

    def has_active_context(
        self, has_state: HasState
    ) -> typing.Optional[AbstractAsyncContext[T]]:
        """Returns context from `has_state` if context in has_state, else None"""

    def _set_active_context(
        self, context: AbstractAsyncContext[T], state_wrapper: StateWrapper
    ):
        """Sets context in state"""

    def __call__(self, has_state: HasState) -> AbstractAsyncContext[T]:
        """Returns context from has_state if exists or opens new context, stores in state, and then returns state"""
        ...

    def from_provider(self, provider: typing.Type[AsyncProvider[T]]):
        """Returns context from a given provider"""


class ContextGetter:
    class ArgType(enum.Enum):
        INSTANCE = enum.auto()
        CONTEXT = enum.auto()
        HAS_STATE = enum.auto()
        GET_CONTEXT = enum.auto()
        VIEW = HAS_STATE

        @classmethod
        def get(cls, name: str):
            return getattr(cls, name.upper())

    def __init__(
        self,
        arg_type: ArgType,
        *,
        context_attr_name: typing.Optional[str] = None,
        _factory: typing.Optional[
            typing.Union[
                AbstractAsyncContextFactory,
                AbstractSyncContextFactory,
            ]
        ] = None,
    ) -> None:
        self.arg_type = arg_type
        self.context_attr_name = context_attr_name
        self.factory = _factory

    def _instance(self, instance):
        return getattr(instance, self.context_attr_name)  # type: ignore

    def _context(self, context):
        return context

    def _has_state(self, has_state):
        return self.factory(has_state)  # type: ignore

    def _get_context(self, instance):
        return instance._get_context

    def get(self, first_arg):
        return getattr(self, '_{}'.format(self.arg_type.name.lower()))(
            first_arg
        )


ImmutableProviderT = typing.TypeVar(
    'ImmutableProviderT', ImmutableSyncProvider, ImmutableAsyncProvider
)


class ImmutableWrapper(typing.Generic[ImmutableProviderT]):
    def __init__(
        self,
        name: str,
        immutable_provider: typing.Type[ImmutableProviderT],
    ) -> None:
        self.name = name
        self.immutable_provider = immutable_provider

    def __get__(self, instance, owner=None) -> ImmutableProviderT:
        if instance is not None:
            return self.immutable_provider(getattr(instance, self.name))
        raise AttributeError(
            f'{self.name!r} object has no attribute {owner.__name__!r}'
        )
