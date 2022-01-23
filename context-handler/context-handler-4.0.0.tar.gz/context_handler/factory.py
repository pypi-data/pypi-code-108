import typing

from context_handler import _datastructures, exc

T = typing.TypeVar('T')


class _ContextFactory(typing.Generic[T]):
    def __init__(
        self,
        provider_class: typing.Union[
            typing.Type[_datastructures.AsyncProvider[T]],
            typing.Type[_datastructures.Provider[T]],
        ],
        context_class: typing.Union[
            typing.Type[_datastructures.AbstractAsyncContext[T]],
            typing.Type[_datastructures.AbstractSyncContext[T]],
        ],
        context_state_name: typing.Optional[str] = None,
    ) -> None:
        self._provider_class = provider_class
        self._context_class = context_class
        self._state_name = context_state_name or self.generate_state_name(
            self._provider_class
        )

    @staticmethod
    def generate_state_name(
        provider_class: typing.Union[
            typing.Type[_datastructures.AsyncProvider[T]],
            typing.Type[_datastructures.Provider[T]],
        ]
    ):
        return provider_class.state_name.lower().replace('provider', 'context')

    def has_active_context(self, has_state: _datastructures.HasState):
        return bool(
            self._get_active_context(_datastructures.StateWrapper(has_state))
        )

    def _get_active_context(self, state_wrapper: _datastructures.StateWrapper):
        return state_wrapper.get(self._state_name, self._context_class)

    def _set_active_context(
        self,
        context: _datastructures.AbstractContext,
        state_wrapper: _datastructures.StateWrapper,
    ):
        state_wrapper.set(self._state_name, context)

    def _get_context(self, state_wrapper: _datastructures.StateWrapper):
        provider = state_wrapper.app_get(
            self._provider_class.state_name, self._provider_class
        )
        if not isinstance(
            provider, (_datastructures.AsyncProvider, _datastructures.Provider)
        ):
            raise exc.NoProviderInState(
                'State Handler does not have provider instantiated'
            )
        return self._context_class(provider)  # type: ignore

    def __call__(self, has_state: _datastructures.HasState):
        state_wrapper = _datastructures.StateWrapper(has_state)
        if (context := self._get_active_context(state_wrapper)) is not None:
            return context
        context = self._get_context(state_wrapper)
        self._set_active_context(context, state_wrapper)
        return context

    def from_provider(
        self,
        provider: typing.Union[
            typing.Type[_datastructures.AsyncProvider[T]],
            typing.Type[_datastructures.Provider[T]],
        ],
    ) -> typing.Union[
        _datastructures.AbstractAsyncContext[T],
        _datastructures.AbstractSyncContext[T],
    ]:
        return self._context_class(provider)  # type: ignore
