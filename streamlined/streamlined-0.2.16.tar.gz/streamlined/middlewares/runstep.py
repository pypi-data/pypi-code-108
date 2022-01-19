import uuid
from typing import Any, Dict, List

from ..common import AND, DEFAULT_KEYERROR, IS_CALLABLE, IS_DICT, IS_NOT_DICT, VOID
from ..services import Scoped
from .action import ACTION, Action
from .argument import Arguments
from .cleanup import Cleanup
from .log import Log
from .middleware import APPLY_INTO, APPLY_ONTO, Context, Middleware, WithMiddlewares
from .middlewares import StackedMiddlewares
from .name import NAME, Name
from .setup import Setup
from .skip import Skip
from .validator import Validator


def _MISSING_RUNSTEP_NAME(value: Dict[str, Any]) -> bool:
    return NAME not in value


def _MISSING_RUNSTEP_ACTION(value: Dict[str, Any]) -> bool:
    return ACTION not in value


def _TRANSFORM_WHEN_MISSING_ACTION(value: Dict[str, Any]) -> Dict[str, Any]:
    value[ACTION] = VOID
    return value


def _TRANSFORM_WHEN_RUNSTEP_IS_CALLABLE(value: Dict[str, Any]) -> Dict[str, Any]:
    return {ACTION: value}


def _TRANSFORM_WHEN_MISSING_NAME(value: Dict[str, Any]) -> Dict[str, Any]:
    value[NAME] = str(uuid.uuid4())
    return value


class Runstep(Middleware, WithMiddlewares):
    @classmethod
    def verify(cls, value: Any) -> None:
        super().verify(value)

        if IS_NOT_DICT(value):
            raise TypeError(f"{value} should be dict")

        if _MISSING_RUNSTEP_NAME(value):
            raise DEFAULT_KEYERROR(value, NAME)

        if _MISSING_RUNSTEP_ACTION(value):
            raise DEFAULT_KEYERROR(value, ACTION)

    def _init_middleware_types(self) -> None:
        super()._init_middleware_types()
        self.middleware_types.extend(
            [Name, Skip, Arguments, Setup, Validator, Action, Log, Cleanup]
        )

    def _init_middleware_apply_methods(self) -> None:
        super()._init_middleware_apply_methods()
        self.middleware_apply_methods.extend(
            [
                APPLY_ONTO,
                APPLY_ONTO,
                APPLY_INTO,
                APPLY_ONTO,
                APPLY_ONTO,
                APPLY_INTO,
                APPLY_ONTO,
                APPLY_ONTO,
            ]
        )

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        # `{RUNSTEP: <callable>}` -> `{RUNSTEP: {.., ACTION: <callable>}}`
        self.simplifications.append((IS_CALLABLE, _TRANSFORM_WHEN_RUNSTEP_IS_CALLABLE))

        # `{RUNSTEP: {...}}` -> `{RUNSTEP: {.., ACTION: VOID}}`
        self.simplifications.append(
            (AND(IS_DICT, _MISSING_RUNSTEP_ACTION), _TRANSFORM_WHEN_MISSING_ACTION)
        )

        # `{RUNSTEP: {...}}` -> `{RUNSTEP: {.., NAME: <uuid>}}`
        self.simplifications.append(
            (AND(IS_DICT, _MISSING_RUNSTEP_NAME), _TRANSFORM_WHEN_MISSING_NAME)
        )

    def _do_parse(self, value: Any) -> Dict[str, List[Middleware]]:
        self.verify(value)
        return {"middlewares": list(self.create_middlewares_from(value))}

    async def _do_apply(self, context: Context) -> Scoped:
        coroutine = WithMiddlewares.apply(self, context)
        return await coroutine()


RUNSTEP = Runstep.get_name()


class Runsteps(StackedMiddlewares):
    pass


RUNSTEPS = Runsteps.get_name()
