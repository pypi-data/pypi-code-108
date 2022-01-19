import sys
from argparse import ArgumentParser
from typing import Any, Callable, Dict, List, Optional, Union

from rich import print

from ..common import AND, DEFAULT_KEYERROR, IS_DICT, IS_NOT_DICT, findvalue, format_help
from ..services import Scoped
from .action import Argparse
from .argument import Arguments
from .cleanup import Cleanup
from .log import Log
from .middleware import APPLY_INTO, APPLY_ONTO, Context, Middleware, WithMiddlewares
from .name import NAME, Name
from .parser import AbstractParser
from .runstage import Runstages
from .runstep import _MISSING_RUNSTEP_NAME, _TRANSFORM_WHEN_MISSING_NAME
from .setup import Setup
from .skip import Skip
from .validator import Validator

_MISSING_PIPELINE_NAME = _MISSING_RUNSTEP_NAME


def _HELP_ARG_SPECIFIED() -> bool:
    args = sys.argv
    return "-h" in args or "--help" in args


class Pipeline(Middleware, WithMiddlewares):
    @classmethod
    def verify(cls, value: Any) -> None:
        super().verify(value)

        if IS_NOT_DICT(value):
            raise TypeError(f"{value} should be dict")

        if _MISSING_PIPELINE_NAME(value):
            raise DEFAULT_KEYERROR(value, NAME)

    def parse(self, value: Any) -> Dict[str, Any]:
        """
        Accept both `{...}` and `{PIPELINE: {...}}`
        """
        if PIPELINE in value:
            return super().parse(value)

        return AbstractParser.parse(self, value)

    def _init_middleware_types(self) -> None:
        super()._init_middleware_types()
        self.middleware_types.extend(
            [Name, Skip, Arguments, Setup, Validator, Runstages, Log, Cleanup]
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
                APPLY_ONTO,
                APPLY_ONTO,
                APPLY_ONTO,
            ]
        )

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        # `{RUNSTAGE: {...}}` -> `{RUNSTAGE: {.., NAME: <uuid>}}`
        self.simplifications.append(
            (AND(IS_DICT, _MISSING_PIPELINE_NAME), _TRANSFORM_WHEN_MISSING_NAME)
        )

    def _do_parse(self, value: Any) -> Dict[str, List[Middleware]]:
        self.verify(value)
        return {"middlewares": list(self.create_middlewares_from(value))}

    async def _do_apply(self, context: Context) -> Scoped:
        coroutine = WithMiddlewares.apply(self, context)
        return await coroutine()

    def format_help(
        self, argument_parser: Optional[Union[ArgumentParser, Dict[str, Any]]] = None
    ) -> str:
        if argument_parser is None:
            argument_parser = dict()

        arguments = map(
            Argparse.to_argument_definition,
            findvalue(self.declaration, Argparse.is_variant),
        )

        return format_help(argument_parser, arguments)

    def print_help(
        self,
        argument_parser: Optional[Union[ArgumentParser, Dict[str, Any]]] = None,
        condition: Callable[[], bool] = _HELP_ARG_SPECIFIED,
    ) -> None:
        if condition():
            print(self.format_help(argument_parser))
            sys.exit(0)


PIPELINE = Pipeline.get_name()
