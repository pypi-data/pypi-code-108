import operator
from collections.abc import Iterable, Sequence
from functools import partial
from inspect import BoundArguments
from typing import Any, Callable, Dict

IS_NONE = partial(operator.is_, None)


IS_TRUTHY = operator.truth
IS_FALSY = operator.not_


IS_CALLABLE = callable


def IS_NOT_CALLABLE(value: Any) -> bool:
    return not IS_CALLABLE(value)


def IS_DICT(value: Any) -> bool:
    return isinstance(value, dict)


def IS_DICT_MISSING_KEY(value: Dict[str, Any], key: str) -> bool:
    return key not in value


def IS_DICTVALUE_NOT_CALLABLE(value: Dict[str, Any], key: str) -> bool:
    return IS_NOT_CALLABLE(value[key])


def IS_NOT_DICT(value: Any) -> bool:
    return not IS_DICT(value)


def IS_STR(value: Any) -> bool:
    return isinstance(value, str)


def IS_NOT_STR(value: Any) -> bool:
    return not IS_STR(value)


def IS_TYPE(value: Any) -> bool:
    return isinstance(value, type)


def IS_NOT_TYPE(value: Any) -> bool:
    return not IS_TYPE(value)


def IS_LIST(value: Any) -> bool:
    return isinstance(value, list)


def IS_NOT_LIST(value: Any) -> bool:
    return not IS_LIST(value)


def IS_LIST_OF_CALLABLE(value: Any) -> bool:
    return IS_LIST(value) and all(map(IS_CALLABLE, value))


def IS_NOT_LIST_OF_CALLABLE(value: Any) -> bool:
    return not IS_LIST_OF_CALLABLE(value)


def IS_LIST_OF_DICT(value: Any) -> bool:
    if IS_LIST(value):
        for listitem in value:
            if IS_NOT_DICT(listitem):
                return False
        return True
    else:
        return False


def IS_NOT_LIST_OF_DICT(value: Any) -> bool:
    if IS_LIST(value):
        for listitem in value:
            if IS_NOT_DICT(listitem):
                return True
        return False
    else:
        return True


def IS_ITERABLE(value: Any) -> bool:
    return isinstance(value, Iterable)


Predicate = Callable[[Any], bool]


def AND(*predicates: Predicate) -> Predicate:
    def wrapper(value: Any) -> bool:
        for predicate in predicates:
            if not predicate(value):
                return False

        return True

    return wrapper


def OR(*predicates: Predicate) -> Predicate:
    def wrapper(value: Any) -> bool:
        for predicate in predicates:
            if predicate(value):
                return True

        return False

    return wrapper


def NOT(predicate: Predicate) -> Predicate:
    def wrapper(value: Any) -> bool:
        return not predicate(value)

    return wrapper


def IS_NONEMPTY_BOUND_ARGUMENTS(bound_arguments: BoundArguments) -> bool:
    return bool(bound_arguments.args or bound_arguments.kwargs)


def IS_EMPTY_BOUND_ARGUMENTS(bound_arguments: BoundArguments) -> bool:
    return not IS_NONEMPTY_BOUND_ARGUMENTS(bound_arguments)


def IS_SEQUENCE(value: Any):
    if IS_STR(value):
        return False
    return isinstance(value, Sequence)
