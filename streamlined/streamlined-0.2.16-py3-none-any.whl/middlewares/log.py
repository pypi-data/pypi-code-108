import itertools
import logging
from typing import Any, Dict

from ..common import (
    AND,
    DEFAULT_KEYERROR,
    IDENTITY_FACTORY,
    IS_CALLABLE,
    IS_DICT,
    IS_NOT_CALLABLE,
    IS_STR,
    LEVEL,
    LOGGER,
    MESSAGE,
    VALUE,
)
from ..services import Scoped
from .action import ACTION, Action
from .middleware import Context, Middleware


def _TRANSFORM_WHEN_IS_STR(value: str) -> Dict[str, Any]:
    return {MESSAGE: value}


def _MISSING_MESSAGE(value):
    return MESSAGE not in value


def _MISSING_LEVEL(value):
    return LEVEL not in value


def _TRANSFORM_WHEN_MISSING_LEVEL(value):
    value[LEVEL] = logging.DEBUG
    return value


def _MISSING_LOGGER(value):
    return LOGGER not in value


def _TRANSFORM_WHEN_MISSING_LOGGER(value):
    value[LOGGER] = logging.getLogger
    return value


def _MESSAGE_IS_STR(value: Dict[str, Any]) -> bool:
    return IS_STR(value[MESSAGE])


def _TRANSFORM_WHEN_MESSAGE_IS_STR(value: Dict[str, Any]) -> Dict[str, Any]:
    value[MESSAGE] = IDENTITY_FACTORY(value[MESSAGE])
    return value


def _LEVEL_NOT_CALLABLE(value: Dict[str, Any]) -> bool:
    return IS_NOT_CALLABLE(value[LEVEL])


def _TRANSFORM_WHEN_LEVEL_NOT_CALLABLE(value: Dict[str, Any]) -> Dict[str, Any]:
    value[LEVEL] = IDENTITY_FACTORY(value[LEVEL])
    return value


def _LOGGER_NOT_CALLABLE(value: Dict[str, Any]) -> bool:
    return IS_NOT_CALLABLE(value[LOGGER])


def _TRANSFORM_WHEN_LOGGER_NOT_CALLABLE(value: Dict[str, Any]) -> Dict[str, Any]:
    value[LOGGER] = IDENTITY_FACTORY(value[LOGGER])
    return value


_TRANSFORM_WHEN_IS_CALLABLE = _TRANSFORM_WHEN_IS_STR


class Log(Middleware):
    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        # `{'log': <str>}` -> `{'log': {MESSAGE: <str>}}`
        self.simplifications.append((IS_STR, _TRANSFORM_WHEN_IS_STR))

        # `{'log': <callable>}` -> `{'log': {MESSAGE: <callable>}}`
        self.simplifications.append((IS_CALLABLE, _TRANSFORM_WHEN_IS_CALLABLE))

        # `{'log': {MESSAGE: ..., LOGGER: ...}}` -> `{'log': {MESSAGE: ..., LOGGER: ..., LEVEL: DEBUG}}`
        self.simplifications.append((AND(IS_DICT, _MISSING_LEVEL), _TRANSFORM_WHEN_MISSING_LEVEL))

        # `{'log': {MESSAGE: ..., LEVEL: ...}}` -> `{'log': {MESSAGE: ..., LOGGER: logging.getLogger, LEVEL: ...}}`
        self.simplifications.append(
            (AND(IS_DICT, _MISSING_LOGGER), _TRANSFORM_WHEN_MISSING_LOGGER)
        )

        # `{'log': {MESSAGE: <str>, LOGGER: ..., LEVEL: ...}}` -> `{'log': {MESSAGE: IDENTITY_FACTORY(<str>), LOGGER: ..., LEVEL: ...}}`
        self.simplifications.append(
            (AND(IS_DICT, _MESSAGE_IS_STR), _TRANSFORM_WHEN_MESSAGE_IS_STR)
        )

        # `{'log': {MESSAGE: ..., LOGGER: ..., LEVEL: <int>}}` -> `{'log': {MESSAGE: ..., LOGGER: ..., LEVEL: IDENTITY_FACTORY(<int>)}}`
        self.simplifications.append(
            (AND(IS_DICT, _LEVEL_NOT_CALLABLE), _TRANSFORM_WHEN_LEVEL_NOT_CALLABLE)
        )

        # `{'log': {MESSAGE: ..., LOGGER: <logger> LEVEL: ...}}` -> `{'log': {MESSAGE: ..., LOGGER: IDENTITY_FACTORY(<logger>), LEVEL: ...)}}`
        self.simplifications.append(
            (AND(IS_DICT, _LOGGER_NOT_CALLABLE), _TRANSFORM_WHEN_LOGGER_NOT_CALLABLE)
        )

    @classmethod
    def verify(cls, value: Any) -> None:
        super().verify(value)

        if not IS_DICT(value):
            raise TypeError(f"{value} should be dict")

        if _MISSING_LEVEL(value):
            raise DEFAULT_KEYERROR(value, LEVEL)

        if _MISSING_LOGGER(value):
            raise DEFAULT_KEYERROR(value, LOGGER)

        if _MISSING_MESSAGE(value):
            raise DEFAULT_KEYERROR(value, MESSAGE)

    def _do_parse(self, value: Dict[str, Any]) -> Dict[str, Middleware]:
        self.verify(value)

        parsed = dict()
        middleware_name = ACTION
        for middleware_type, keyname in zip(itertools.repeat(Action), [LOGGER, LEVEL, MESSAGE]):
            new_value = {middleware_name: value[keyname]}
            parsed[keyname] = middleware_type(new_value)

        return parsed

    async def get_log_level(self, context: Context) -> int:
        scoped = await Middleware.apply_onto(
            getattr(self, LEVEL), context.replace_with_void_next()
        )
        level = scoped.getmagic(VALUE)
        context.scoped.setmagic(LEVEL, level)
        return level

    async def get_logger(self, context: Context) -> logging.Logger:
        scoped = await Middleware.apply_onto(
            getattr(self, LOGGER), context.replace_with_void_next()
        )
        logger = scoped.getmagic(VALUE)
        context.scoped.setmagic(LOGGER, logger)
        return logger

    async def get_message(self, context: Context) -> str:
        scoped = await Middleware.apply_onto(
            getattr(self, MESSAGE), context.replace_with_void_next()
        )
        message = scoped.getmagic(VALUE)
        context.scoped.setmagic(MESSAGE, message)
        return message

    async def _do_apply(self, context: Context) -> Scoped:
        message = await self.get_message(context)

        level = await self.get_log_level(context)

        logger = await self.get_logger(context)
        logger.log(level, message)

        await context.next()
        return context.scoped


LOG = Log.get_name()
