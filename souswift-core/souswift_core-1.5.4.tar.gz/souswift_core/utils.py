import asyncio
import warnings
from functools import wraps
from typing import Callable, TypeVar

import pydantic
from typing_extensions import ParamSpec

from souswift_core.dtos import Model

T = TypeVar('T')
P = ParamSpec('P')
ModelT = TypeVar('ModelT', bound=Model)


def deprecated(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        warnings.warn(
            f'{func.__name__} is deprecated and can be removed without notice!',
            DeprecationWarning,
        )
        return func(*args, **kwargs)

    return inner


async def as_async(
    func: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    """Asynchronously schedule sync function to run in a separate thread"""
    return await asyncio.to_thread(func, *args, **kwargs)


def get_optional_model(model: type[ModelT], *exclude: str) -> type[ModelT]:
    edit_dto = pydantic.create_model(
        f'Optional{model.__name__}',
        __base__=model,
        __module__=model.__module__,
    )
    for field in edit_dto.__fields__.values():
        field.required = False
        field.default = None
    for field in exclude:
        edit_dto.__fields__.pop(field)
    return edit_dto
