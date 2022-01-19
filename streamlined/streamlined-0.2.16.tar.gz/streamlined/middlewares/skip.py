from typing import Any, Awaitable, Dict

from ..common import (
    ACTION,
    AND,
    CONTRADICTION,
    DEFAULT_KEYERROR,
    IDENTITY_FACTORY,
    IS_DICT,
    IS_NONE,
    IS_NOT_CALLABLE,
    IS_NOT_DICT,
    NOOP,
    RETURN_FALSE,
    VALUE,
)
from ..services import Scoped
from .action import Action
from .middleware import Context, Middleware


def _TRANSFORM_WHEN_NOT_DICT(value: Any) -> Dict[str, Any]:
    return {VALUE: value}


def _MISSING_ACTION(value: Dict[str, Any]) -> bool:
    return ACTION not in value


def _TRANSFORM_WHEN_MISSING_ACTION(value: Dict[str, Any]) -> Dict[str, Any]:
    value[ACTION] = NOOP
    return value


def _MISSING_VALUE(value: Dict[str, Any]) -> bool:
    return VALUE not in value


def _TRANSFORM_WHEN_MISSING_VALUE(value: Dict[str, Any]) -> Dict[str, Any]:
    value[VALUE] = RETURN_FALSE
    return value


def _VALUE_NOT_CALLABLE(value: Dict[str, Any]) -> bool:
    return IS_NOT_CALLABLE(value[VALUE])


def _TRANSFORM_WHEN_VALUE_NOT_CALLABLE(value: Dict[str, Any]) -> Dict[str, Any]:
    value[VALUE] = IDENTITY_FACTORY(value[VALUE])
    return value


class Skip(Middleware):
    @classmethod
    def verify(cls, value: Any) -> None:
        super().verify(value)

        if not IS_DICT(value):
            raise TypeError(f"{value} should be dict")

        if _MISSING_ACTION(value):
            raise DEFAULT_KEYERROR(value, ACTION)

        if _MISSING_VALUE(value):
            raise DEFAULT_KEYERROR(value, VALUE)

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        # `{'skip': None}` -> `{'skip': False}`
        self.simplifications.append((IS_NONE, CONTRADICTION))

        # `{'skip': <bool>}` -> `{'skip': lambda: <bool>}`
        self.simplifications.append((AND(IS_NOT_DICT, IS_NOT_CALLABLE), IDENTITY_FACTORY))

        # `{'skip': <any>}` -> `{'skip': {VALUE: <any>}}`
        self.simplifications.append((IS_NOT_DICT, _TRANSFORM_WHEN_NOT_DICT))

        # `{'skip': {VALUE: ...}}` -> `{'skip': {VALUE: ..., ACTION: NOOP}}`
        self.simplifications.append(
            (AND(IS_DICT, _MISSING_ACTION), _TRANSFORM_WHEN_MISSING_ACTION)
        )

        # `{'skip': {ACTION: ...}}` -> `{'skip': {VALUE: RETURN_FALSE, ACTION: ...}}`
        self.simplifications.append((AND(IS_DICT, _MISSING_VALUE), _TRANSFORM_WHEN_MISSING_VALUE))

        # `{'skip': {VALUE: <non-callable>, ACTION: ...}}`
        self.simplifications.append(
            (AND(IS_DICT, _VALUE_NOT_CALLABLE), _TRANSFORM_WHEN_VALUE_NOT_CALLABLE)
        )

    def _do_parse(self, value: Dict[str, Any]) -> Dict[str, Middleware]:
        self.verify(value)

        return {"_should_skip": Action({ACTION: value[VALUE]}), "_when_skip": Action(value)}

    async def should_skip(self, context: Context) -> Awaitable[bool]:
        scoped: Scoped = await Middleware.apply_onto(self._should_skip, context)
        skipped = scoped.getmagic(VALUE)
        context.scoped.setmagic(SKIP, skipped)
        return skipped

    async def when_skip(self, context: Context) -> Awaitable[Scoped]:
        scoped: Scoped = await Middleware.apply_into(self._when_skip, context)
        return scoped.getmagic(VALUE)

    async def _do_apply(self, context: Context) -> Scoped:
        if await self.should_skip(context.replace_with_void_next()):
            await self.when_skip(context.replace_with_void_next())
        else:
            await context.next()
        return context.scoped


SKIP = Skip.get_name()
