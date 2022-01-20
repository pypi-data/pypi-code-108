from functools import partial
from inspect import isclass
from typing import Any, Callable, Dict, Type

from streamlined.common.predicates import IS_CALLABLE

from ..common import (
    ACTION,
    AND,
    DEFAULT_KEYERROR,
    IS_DICT,
    IS_DICT_MISSING_KEY,
    IS_NOT_CALLABLE,
    NOOP,
    TAUTOLOGY,
    WHEN,
)
from ..services import Scoped
from .action import Action
from .middleware import Context, Middleware

EXCEPTION = "exception"
CAUGHT_EXCEPTION = "caught_exception"

_MISSING_EXCEPTION = partial(IS_DICT_MISSING_KEY, key=EXCEPTION)
_MISSING_WHEN = partial(IS_DICT_MISSING_KEY, key=WHEN)
_MISSING_ACTION = partial(IS_DICT_MISSING_KEY, key=ACTION)


def _IS_EXCEPTION_CLASS(value: Any) -> bool:
    return isclass(value) and issubclass(value, Exception)


def _TRANSFORM_WHEN_IS_EXCEPTION_CLASS(value: Type[Exception]) -> Dict[str, Type[Exception]]:
    return {EXCEPTION: value}


def _TRANSFORM_WHEN_IS_CALLABLE(
    value: Callable[[Exception], bool]
) -> Dict[str, Callable[[Exception], bool]]:
    return {WHEN: value}


def _TRANSFORM_WHEN_MISSING_EXCEPTION(value: Dict[str, Any]) -> Dict[str, Any]:
    value[EXCEPTION] = Exception
    return value


def _TRANSFORM_WHEN_MISSING_ACTION(value: Dict[str, Any]) -> Dict[str, Any]:
    value[ACTION] = NOOP
    return value


def _TRANSFORM_WHEN_MISSING_WHEN(value: Dict[str, Any]) -> Dict[str, Any]:
    value[WHEN] = TAUTOLOGY
    return value


class Suppress(Middleware):
    @classmethod
    def verify(cls, value: Any) -> None:
        super().verify(value)

        if not IS_DICT(value):
            raise TypeError(f"{value} should be dict")

        if _MISSING_EXCEPTION(value):
            raise DEFAULT_KEYERROR(value, EXCEPTION)
        elif not _IS_EXCEPTION_CLASS(value[EXCEPTION]):
            raise ValueError(
                f"{EXCEPTION} should be a subclass of Exception, received {value[EXCEPTION]} instead"
            )

        if _MISSING_WHEN(value):
            raise DEFAULT_KEYERROR(value, WHEN)
        elif IS_NOT_CALLABLE(value[WHEN]):
            raise ValueError(f"{WHEN} should be a callable, received {value[WHEN]} instead")

        if _MISSING_ACTION(value):
            raise DEFAULT_KEYERROR(value, ACTION)
        elif IS_NOT_CALLABLE(value[ACTION]):
            raise ValueError(f"{ACTION} should be a callable, received {value[ACTION]} instead")

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        # `{'suppress': <exception>}` -> `{'suppress': {EXCEPTION: <exception>}}`
        self.simplifications.append((_IS_EXCEPTION_CLASS, _TRANSFORM_WHEN_IS_EXCEPTION_CLASS))

        # `{'suppress': <callable>}` -> `{'suppress': {WHEN: <callable>}}`
        self.simplifications.append((IS_CALLABLE, _TRANSFORM_WHEN_IS_CALLABLE))

        # `{'suppress': {WHEN: ..., ACTION: ...}}` -> `{'suppress': {WHEN: ..., ACTION: ..., EXCEPTION: Exception}}`
        self.simplifications.append(
            (AND(IS_DICT, _MISSING_EXCEPTION), _TRANSFORM_WHEN_MISSING_EXCEPTION)
        )

        # `{'suppress': {WHEN: ..., EXCEPTION: ...}}` -> `{'suppress': {WHEN: ..., ACTION: NOOP, EXCEPTION: ...}}`
        self.simplifications.append(
            (AND(IS_DICT, _MISSING_ACTION), _TRANSFORM_WHEN_MISSING_ACTION)
        )

        # `{'suppress': {ACTION: ..., EXCEPTION: ...}}` -> `{'suppress': {WHEN: RETURN_TRUE, ACTION: ..., EXCEPTION: ...}}`
        self.simplifications.append((AND(IS_DICT, _MISSING_WHEN), _TRANSFORM_WHEN_MISSING_WHEN))

    def _do_parse(self, value: Dict[str, Any]) -> Dict[str, Any]:
        self.verify(value)

        return {
            EXCEPTION: value[EXCEPTION],
            WHEN: value[WHEN],
            ACTION: Action(value[ACTION]),
        }

    async def _do_apply(self, context: Context) -> Scoped:
        expected_exception: Type[Exception] = getattr(self, EXCEPTION)
        context.scoped.setmagic(EXCEPTION, expected_exception)

        suppress_when: Callable[[Exception], bool] = getattr(self, WHEN)
        context.scoped.setmagic(WHEN, suppress_when)

        action: Action = getattr(self, ACTION)

        try:
            await context.next()
        except expected_exception as exception:
            if suppress_when(exception):
                context.scoped.setmagic(CAUGHT_EXCEPTION, exception)
                await action.apply_into(context.replace_with_void_next())
            else:
                raise

        return context.scoped


SUPPRESS = Suppress.get_name()
