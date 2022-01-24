from typing import Awaitable, Callable, TypeVar, Union

from jetpack._runtime.client import client
from jetpack._task.jetpack_function_with_client import JetpackFunctionWithClient

T = TypeVar("T")


class JetpackFunction(JetpackFunctionWithClient[T]):
    def __init__(self, func: Callable[..., Union[T, Awaitable[T]]]) -> None:
        super().__init__(client, func)
