import typing
from asyncio import iscoroutinefunction
from asyncio.coroutines import _is_coroutine  # noqa
from functools import wraps
from inspect import isasyncgenfunction, isgeneratorfunction

from typing_extensions import ParamSpec

from . import _datastructures, context

T = typing.TypeVar('T')
P = ParamSpec('P')
ClassT = typing.TypeVar('ClassT')


def _open_sync_ctx_in_sync(
    getter: _datastructures.ContextGetter,
    func,
    first_arg,
    *args,
    **kwargs,
):
    with getter.get(first_arg).open():
        return func(first_arg, *args, **kwargs)  # type: ignore


async def _open_sync_ctx_in_coro(
    getter: _datastructures.ContextGetter,
    func,
    first_arg,
    *args,
    **kwargs,
):
    with getter.get(first_arg).open():
        return await func(first_arg, *args, **kwargs)  # type: ignore


async def _open_sync_ctx_in_asyncgen(
    getter: _datastructures.ContextGetter,
    func,
    first_arg,
    *args,
    **kwargs,
):
    with getter.get(first_arg).open():
        async for item in func(first_arg, *args, **kwargs):  # type: ignore
            yield item


async def _open_async_ctx_in_coro(
    getter: _datastructures.ContextGetter,
    func,
    first_arg,
    *args,
    **kwargs,
):
    async with getter.get(first_arg).open():
        return await func(first_arg, *args, **kwargs)  # type: ignore


async def _open_async_ctx_in_async_gen(
    getter: _datastructures.ContextGetter,
    func,
    first_arg,
    *args,
    **kwargs,
):
    async with getter.get(first_arg).open():
        async for item in func(first_arg, *args, **kwargs):  # type: ignore
            yield item


def _setup_wrapper(wrapper: typing.Callable, func, context_getter):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return wrapper(context_getter, func, *args, **kwargs)

    if iscoroutinefunction(func):
        wrapped._is_coroutine = _is_coroutine
    return wrapped


def _get_sync_wrapper(func):
    inner = _open_sync_ctx_in_sync
    if isasyncgenfunction(func):
        inner = _open_sync_ctx_in_asyncgen
    elif iscoroutinefunction(func):
        inner = _open_sync_ctx_in_coro
    return inner


def _get_async_wrapper(func):
    if iscoroutinefunction(func):
        inner = _open_async_ctx_in_coro
    elif isasyncgenfunction(func):
        inner = _open_async_ctx_in_async_gen
    else:
        raise TypeError('AsyncContext cannot be used in sync function')
    return inner


def _sync_context(
    func: typing.Callable[P, T] = None,
    /,
    *,
    first_arg_type: typing.Union[
        typing.Literal['instance'],
        typing.Literal['view'],
        typing.Literal['context'],
        typing.Literal['get_context'],
    ] = 'context',
    **kwargs,
) -> typing.Union[
    typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]],
    typing.Callable[P, T],
]:
    context_getter = _datastructures.ContextGetter(
        _datastructures.ContextGetter.ArgType.get(first_arg_type),
        **kwargs,
    )

    def outer(func):
        return _setup_wrapper(_get_sync_wrapper(func), func, context_getter)

    if func:
        return outer(func)
    return outer


def _async_context(
    func: typing.Callable[P, T] = None,
    /,
    *,
    first_arg_type: typing.Union[
        typing.Literal['instance'],
        typing.Literal['view'],
        typing.Literal['context'],
        typing.Literal['get_context'],
    ] = 'context',
    **kwargs,
) -> typing.Union[
    typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]],
    typing.Callable[P, T],
]:
    context_getter = _datastructures.ContextGetter(
        _datastructures.ContextGetter.ArgType.get(first_arg_type),
        **kwargs,
    )

    def outer(func):
        return _setup_wrapper(_get_async_wrapper(func), func, context_getter)

    if func:
        return outer(func)  # type: ignore
    return outer


def _guess_context_class(
    provider_class: typing.Type[
        typing.Union[_datastructures.Provider, _datastructures.AsyncProvider]
    ]
):
    if _is_valid_async_provider(provider_class):
        return context.AsyncContext
    elif _is_valid_sync_provider(provider_class):
        return context.SyncContext
    raise TypeError(
        'provider_class must implement either _datastructures.Provider or _datastructures.AsyncProvider protocol'
    )


def _is_valid_provider(provider_class):
    has_methods = all(
        hasattr(provider_class, item)
        for item in ['state_name', 'is_closed', 'close_client', 'acquire']
    )
    methods_are_valid = isinstance(
        provider_class.state_name, str
    ) and callable(provider_class.is_closed)
    return has_methods and methods_are_valid


def _is_valid_async_provider(provider_class):
    is_valid_provider = _is_valid_provider(provider_class)
    methods_have_valid_types = iscoroutinefunction(
        provider_class.close_client
    ) and (
        (
            hasattr(provider_class.acquire, '__aenter__')
            and hasattr(provider_class.acquire, '__aexit__')
        )
        or isasyncgenfunction(provider_class.acquire.__wrapped__)
    )
    return is_valid_provider and methods_have_valid_types


def _is_valid_sync_provider(provider_class):
    is_valid_provider = _is_valid_provider(provider_class)
    methods_have_valid_types = callable(provider_class.close_client) and (
        (
            hasattr(provider_class.acquire, '__enter__')
            and hasattr(provider_class.acquire, '__exit__')
        )
        or isgeneratorfunction(provider_class.acquire.__wrapped__)
    )
    return is_valid_provider and methods_have_valid_types


class _EnsureAsyncContext:
    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['instance'],
        context_attr_name: str,
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['view'],
        _factory: _datastructures.AbstractAsyncContextFactory,
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['context'],
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['get_context'],
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        func: typing.Callable[P, T],
        /,
    ) -> typing.Callable[P, T]:
        ...

    def __call__(
        self,
        func: typing.Callable[P, T] = None,
        /,
        *,
        first_arg_type: typing.Union[
            typing.Literal['instance'],
            typing.Literal['view'],
            typing.Literal['context'],
            typing.Literal['get_context'],
        ] = 'context',
        **kwargs,
    ) -> typing.Callable[P, T]:
        wrapper = _async_context(first_arg_type=first_arg_type, **kwargs)
        if func is not None:
            return wrapper(func)
        return wrapper

    def instance(self, field: str):
        return self(first_arg_type='instance', context_attr_name=field)

    def view(
        self,
        factory: _datastructures.AbstractAsyncContextFactory,
    ):
        return self(first_arg_type='view', _factory=factory)

    def context(self):
        return self(first_arg_type='context')

    def context_class(self):
        return self(first_arg_type='get_context')


class _EnsureSyncContext:
    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['instance'],
        context_attr_name: str,
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['view'],
        _factory: _datastructures.AbstractSyncContextFactory,
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['context'],
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        *,
        first_arg_type: typing.Literal['get_context'],
    ) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
        ...

    @typing.overload
    def __call__(
        self,
        func: typing.Callable[P, T],
        /,
    ) -> typing.Callable[P, T]:
        ...

    def __call__(
        self,
        func: typing.Callable[P, T] = None,
        /,
        *,
        first_arg_type: typing.Union[
            typing.Literal['instance'],
            typing.Literal['view'],
            typing.Literal['context'],
            typing.Literal['get_context'],
        ] = 'context',
        **kwargs,
    ) -> typing.Union[
        typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]],
        typing.Callable[P, T],
    ]:
        wrapper = _sync_context(first_arg_type=first_arg_type, **kwargs)
        if func is not None:
            return wrapper(func)
        return wrapper

    def instance(self, field: str):
        return self(first_arg_type='instance', context_attr_name=field)

    def view(
        self,
        factory: _datastructures.AbstractSyncContextFactory,
    ):
        return self(first_arg_type='view', _factory=factory)

    def context(self):
        return self(first_arg_type='context')

    def context_class(self):
        return self(first_arg_type='get_context')


sync_context = _EnsureSyncContext()
async_context = _EnsureAsyncContext()

method = sync_context.context_class()
async_method = async_context.context_class()

__all__ = ['sync_context', 'async_context', 'async_method', 'method']
