import typing

T = typing.TypeVar('T')


class _GetContext:
    def __init__(self, field: str) -> None:
        self._field = field

    def __get__(self, instance, _):
        return None if instance is None else getattr(instance, self._field)

@typing.overload
def context_class(cls: typing.Type[T], /) -> typing.Type[T]:
    ...

@typing.overload
def context_class(cls: None = None, /, field_name: str = 'context') -> typing.Callable[[typing.Type[T]], typing.Type[T]]:
    ...

def context_class(
    cls: typing.Optional[typing.Type[T]] = None, /, field_name: str = 'context'
) -> typing.Union[
    typing.Type[T], typing.Callable[[typing.Type[T]], typing.Type[T]]
]:
    def wrapper(cls: typing.Type[T]) -> typing.Type[T]:
        setattr(cls, '_get_context', _GetContext(field_name))
        setattr(cls, '__context__', True)
        return cls

    return wrapper if cls is None else wrapper(cls)
