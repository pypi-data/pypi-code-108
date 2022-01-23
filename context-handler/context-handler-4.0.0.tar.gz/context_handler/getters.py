import typing

from context_handler import context

from . import _datastructures, factory

T = typing.TypeVar('T')


@typing.overload
def context_factory(
    provider_class: typing.Type[_datastructures.AsyncProvider[T]],
    context_class: typing.Type[_datastructures.AbstractAsyncContext[T]],
    context_state_name: typing.Optional[str] = None,
) -> _datastructures.AbstractAsyncContextFactory[T]:
    ...


@typing.overload
def context_factory(
    provider_class: typing.Type[_datastructures.Provider[T]],
    context_class: typing.Type[_datastructures.AbstractSyncContext[T]],
    context_state_name: typing.Optional[str] = None,
) -> _datastructures.AbstractSyncContextFactory[T]:
    ...


@typing.overload
def context_factory(
    provider_class: typing.Union[
        typing.Type[_datastructures.AsyncProvider[T]],
        typing.Type[_datastructures.Provider[T]],
    ],
    context_class: typing.Union[
        typing.Type[_datastructures.AbstractAsyncContext[T]],
        typing.Type[_datastructures.AbstractSyncContext[T]],
    ],
    context_state_name: typing.Optional[str] = None,
) -> typing.Union[
    _datastructures.AbstractAsyncContextFactory[T],
    _datastructures.AbstractSyncContextFactory[T],
]:
    ...


def context_factory(
    provider_class: typing.Union[
        typing.Type[_datastructures.AsyncProvider[T]],
        typing.Type[_datastructures.Provider[T]],
    ],
    context_class: typing.Union[
        typing.Type[_datastructures.AbstractAsyncContext[T]],
        typing.Type[_datastructures.AbstractSyncContext[T]],
    ],
    context_state_name: typing.Optional[str] = None,
) -> typing.Union[
    _datastructures.AbstractAsyncContextFactory[T],
    _datastructures.AbstractSyncContextFactory[T],
]:
    return factory._ContextFactory(
        provider_class, context_class, context_state_name
    )  # type:ignore


generate_state_name = factory._ContextFactory.generate_state_name


@typing.overload
def get_context(
    provider: _datastructures.Provider[T],
) -> _datastructures.AbstractSyncContext[T]:
    ...


@typing.overload
def get_context(
    provider: _datastructures.AsyncProvider[T],
) -> _datastructures.AbstractAsyncContext[T]:
    ...


def get_context(
    provider: typing.Union[
        _datastructures.AsyncProvider[T], _datastructures.Provider[T]
    ]
) -> typing.Union[
    _datastructures.AbstractAsyncContext[T],
    _datastructures.AbstractSyncContext[T],
]:
    if isinstance(provider, _datastructures.AsyncProvider):
        return context.AsyncContext(provider)
    elif isinstance(provider, context.SyncContext):
        return context.SyncContext(provider)
    raise TypeError('Invalid provider')


ArgType = _datastructures.ContextGetter.ArgType
