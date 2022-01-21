from inspect import signature
from pydantic.typing import Callable

def copy_signature(source_function: Callable):
    def inner(target_function: Callable):
        target_function.__signature__ = signature(source_function)
        return target_function
    return inner
