from __future__ import annotations

import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Type, Union

from .dictionary import set_if_not_none
from .predicates import IS_STR


@dataclass
class ParsedArgument:
    name: str
    value: Any
    remaining_args: List[str]
    definition: ArgumentDefinition


@dataclass
class ArgumentDefinition:
    args: List[str]
    kwargs: Dict[str, Any]

    @classmethod
    def of(
        cls,
        name: Union[str, List[str]],
        action: Optional[str] = None,
        nargs: Optional[Union[str, int]] = None,
        const: Optional[Any] = None,
        default: Optional[Any] = None,
        type: Optional[Type[Any]] = None,
        choices: Optional[Iterable[Any]] = None,
        required: Optional[bool] = None,
        help: Optional[str] = None,
        metavar: Optional[str] = None,
        dest: Optional[str] = None,
    ) -> ArgumentDefinition:
        kwargs: Dict[str, Any] = {}
        args: List[str] = [name] if IS_STR(name) else name

        set_if_not_none(kwargs, "action", action)
        set_if_not_none(kwargs, "nargs", nargs)
        set_if_not_none(kwargs, "const", const)
        set_if_not_none(kwargs, "default", default)
        set_if_not_none(kwargs, "type", type)
        set_if_not_none(kwargs, "choices", choices)
        set_if_not_none(kwargs, "required", required)
        set_if_not_none(kwargs, "help", help)
        set_if_not_none(kwargs, "metavar", metavar)
        set_if_not_none(kwargs, "dest", dest)

        return cls(args, kwargs)

    def add_to(self, argument_parser: ArgumentParser) -> None:
        argument_parser.add_argument(*self.args, **self.kwargs)


def parse_argument(
    name: Union[str, List[str]],
    action: Optional[str] = None,
    nargs: Optional[Union[str, int]] = None,
    const: Optional[Any] = None,
    default: Optional[Any] = None,
    type: Optional[Type[Any]] = str,
    choices: Optional[Iterable[Any]] = None,
    required: Optional[bool] = None,
    help: Optional[str] = None,
    metavar: Optional[str] = None,
    dest: Optional[str] = None,
    args: List[str] = sys.argv,
    add_help: bool = False,
    allow_abbrev: bool = False,
) -> ParsedArgument:
    """
    Combine `add_argument` and `parse_known_args` from argparse.

    Parameters
    ------
    add_help: bool
        Whether help argument will be parsed. Default to False to
        avoid influencing causing system exit and interrupting
        partial parsing. This should be the expected argument.
    allow_abbrev: bool
        Normally, when you pass an argument list to the parse_args() method of an ArgumentParser, it recognizes abbreviations of long options.

        This feature can be disabled by setting allow_abbrev to False.
    """

    parser = ArgumentParser(add_help=add_help, allow_abbrev=allow_abbrev)
    argument_definition = ArgumentDefinition.of(
        name, action, nargs, const, default, type, choices, required, help, metavar, dest
    )
    argument_definition.add_to(parser)

    namespace, remaining_args = parser.parse_known_args(args)
    parsed = vars(namespace)
    argname, argvalue = parsed.popitem()
    return ParsedArgument(argname, argvalue, remaining_args, argument_definition)


def format_help(
    argument_parser: Union[ArgumentParser, Dict[str, Any]],
    arguments: Iterable[Union[Dict[str, Any], ArgumentDefinition]],
) -> str:
    if not isinstance(argument_parser, ArgumentParser):
        argument_parser = ArgumentParser(**argument_parser)

    for argument in arguments:
        if not isinstance(argument, ArgumentDefinition):
            argument = ArgumentDefinition.of(**argument)

        argument.add_to(argument_parser)

    return argument_parser.format_help()
