from collections.abc import Iterable, Iterator
from functools import wraps, partial
from typing import ParamSpec, TypeVar, Callable

__ALL__ = ['debug', 'debug_method']


P = ParamSpec('P')
T = TypeVar('T')
DecoratedFunc = Callable[[P], T]


def debug(func: DecoratedFunc | None = None, *,
          is_method: bool = False,
          intercept_iterators: bool = True) -> DecoratedFunc | Callable[[DecoratedFunc, bool, bool], DecoratedFunc]:

    if func is None:
        return partial(debug, is_method=is_method, intercept_iterators=intercept_iterators)

    @wraps(func)
    def wrapper(*args, **kwargs):
        output_args = f'({", ".join(map(repr, args if not is_method else args[1:]))}, ' \
                      f'{", ".join(f"{k}={v!r}" for k, v in kwargs.items())})'
        print(f'Called: {func.__qualname__}({output_args})')

        result = func(*args, **kwargs)
        print(f'{func.__qualname__} returned: {result!r}', flush=True)

        if intercept_iterators:
            if isinstance(result, Iterator):
                while True:
                    try:
                        next_result = next(result)
                        print(f'{func.__qualname__} yielded: {next_result!r}')
                        yield next_result
                    except StopIteration as e:
                        print(f'{func.__qualname__} finished yielding: {e.value!r}')
                        return e.value
            elif isinstance(result, Iterable):
                output = list(result)
                print(f"{func.__qualname__}:: returned: iter([{', '.join(repr(i) for i in output)}])")
                return iter(output)
        else:
            return result

    return wrapper


debug_method = partial(debug, is_method=True)
