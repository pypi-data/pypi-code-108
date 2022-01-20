import sys
from functools import partial
from subprocess import DEVNULL, PIPE
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Type, Union

from ..common import (
    AND,
    IDENTITY_FACTORY,
    IS_DICT_MISSING_KEY,
    IS_DICTVALUE_NOT_CALLABLE,
    IS_LIST,
    IS_NOT_CALLABLE,
    IS_NOT_LIST,
    IS_NOT_LIST_OF_CALLABLE,
    IS_STR,
    IS_TYPE,
    TYPE,
    VALUE,
    ArgumentDefinition,
    ParsedArgument,
    StdinStream,
    Stream,
    SubprocessResult,
    get_or_raise,
    parse_argument,
    rewrite_function_parameters,
)
from ..common import run as run_
from ..parsing import Variant, WithVariants
from ..services import Scoped
from .middleware import Context, Middleware
from .name import NAME


def _TRANSFORM_DICTVALUE_TO_CALLABLE(value: Dict[str, Any], key: str) -> Dict[str, Any]:
    value[key] = IDENTITY_FACTORY(value[key])
    return value


def _TRANSFORM_DICTVALUE_TO_NONE(value: Dict[str, Any], key: str) -> Dict[str, Any]:
    value[key] = None
    return value


def _EXPECT_CALLABLE_AT_KEY(dictionary: Dict[str, Any], key: str) -> None:
    value = get_or_raise(dictionary, key)
    if IS_NOT_CALLABLE(value):
        raise TypeError(f"Expect value for {key} to be a Callable, received {value}")


ARGS = "args"
STDIN = "stdin"
STDOUT = "stdout"
STDERR = "stderr"
KWARGS = "kwargs"


_IS_ARGS_NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=ARGS)


_TRANSFORM_WHEN_ARGS_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=ARGS)


_MISSING_STDIN = partial(IS_DICT_MISSING_KEY, key=STDIN)


def _TRANSFORM_WHEN_MISSING_STDIN(value: Dict[str, Any]) -> Dict[str, Any]:
    value[STDIN] = DEVNULL
    return value


def _IS_STDIN_STR(value: Dict[str, Any]) -> bool:
    return IS_STR(value[STDIN])


def _TRANSFORM_WHEN_STDIN_IS_STR(value: Dict[str, Any]) -> Dict[str, Any]:
    string: str = value[STDIN]
    value[STDIN] = string.encode("utf-8")
    return value


_MISSING_ARGS = partial(IS_DICT_MISSING_KEY, key=ARGS)


_IS_STDIN_NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=STDIN)


_TRANSFORM_WHEN_STDIN_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=STDIN)


_MISSING_STDOUT = partial(IS_DICT_MISSING_KEY, key=STDOUT)


def _TRANSFORM_WHEN_MISSING_STDOUT(value: Dict[str, Any]) -> Dict[str, Any]:
    value[STDOUT] = PIPE
    return value


_IS_STDOUT_NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=STDOUT)


_TRANSFORM_WHEN_STDOUT_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=STDOUT)

_MISSING_STDERR = partial(IS_DICT_MISSING_KEY, key=STDERR)


def _TRANSFORM_WHEN_MISSING_STDERR(value: Dict[str, Any]) -> Dict[str, Any]:
    value[STDERR] = PIPE
    return value


_IS_STDERR_NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=STDERR)

_TRANSFORM_WHEN_STDERR_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=STDERR)

_MISSING_KWARGS = partial(IS_DICT_MISSING_KEY, key=KWARGS)


def _TRANSFORM_WHEN_MISSING_KWARGS(value: Dict[str, Any]) -> Dict[str, Any]:
    value[KWARGS] = dict()
    return value


_IS_KWARGS_NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=KWARGS)


_TRANSFORM_WHEN_KWARGS_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=KWARGS)


class Shell(Variant):
    run: ClassVar[
        Callable[[str, StdinStream, Stream, Stream, Dict[str, Any]], SubprocessResult]
    ] = rewrite_function_parameters(
        run_, "run", f"_{VALUE}0_", f"_{VALUE}1_", f"_{VALUE}2_", f"_{VALUE}3_", f"_{VALUE}4_"
    )

    @classmethod
    def reduce(cls, value: Any) -> Any:
        cls.verify(value)

        return [value[ARGS], value[STDIN], value[STDOUT], value[STDERR], value[KWARGS], cls.run]

    @classmethod
    def verify(cls, value: Any) -> None:
        for key in [ARGS, STDIN, STDOUT, STDERR, KWARGS]:
            _EXPECT_CALLABLE_AT_KEY(value, key)
        return value

    def _init_simplifications_for_variant(self) -> None:
        super()._init_simplifications_for_variant()

        self._variant_simplifications.append(
            (_IS_ARGS_NOT_CALLABLE, _TRANSFORM_WHEN_ARGS_NOT_CALLABLE)
        )

        self._variant_simplifications.append((_MISSING_STDIN, _TRANSFORM_WHEN_MISSING_STDIN))

        self._variant_simplifications.append((_IS_STDIN_STR, _TRANSFORM_WHEN_STDIN_IS_STR))

        self._variant_simplifications.append(
            (_IS_STDIN_NOT_CALLABLE, _TRANSFORM_WHEN_STDIN_NOT_CALLABLE)
        )

        self._variant_simplifications.append((_MISSING_STDOUT, _TRANSFORM_WHEN_MISSING_STDOUT))

        self._variant_simplifications.append(
            (_IS_STDOUT_NOT_CALLABLE, _TRANSFORM_WHEN_STDOUT_NOT_CALLABLE)
        )

        self._variant_simplifications.append((_MISSING_STDERR, _TRANSFORM_WHEN_MISSING_STDERR))

        self._variant_simplifications.append(
            (_IS_STDERR_NOT_CALLABLE, _TRANSFORM_WHEN_STDERR_NOT_CALLABLE)
        )

        self._variant_simplifications.append((_MISSING_KWARGS, _TRANSFORM_WHEN_MISSING_KWARGS))

        self._variant_simplifications.append(
            (_IS_KWARGS_NOT_CALLABLE, _TRANSFORM_WHEN_KWARGS_NOT_CALLABLE)
        )


SHELL = Shell.get_name()


NARGS = "nargs"
CONST = "const"
DEFAULT = "default"
ARGTYPE = "type_"
CHOICES = "choices"
REQUIRED = "required"
HELP = "help"
METAVAR = "metavar"
DEST = "dest"


_NAME_NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=NAME)
_TRANSFORM_WHEN_NAME_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=NAME)

_MISSING_ARGS = partial(IS_DICT_MISSING_KEY, key=ARGS)


def _TRANSFORM_WHEN_MISSING_ARGS(value: Dict[str, Any]) -> Dict[str, Any]:
    value[ARGS] = sys.argv
    return value


_ARGS_NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=ARGS)
_TRANSFORM_WHEN_ARGS_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=ARGS)


def _ARGTYPE_NOT_CALLABLE(value: Dict[str, Any]) -> bool:
    argtype = value[ARGTYPE]
    return IS_NOT_CALLABLE(argtype) or IS_TYPE(argtype)


def _get_argparse_value(_value_: ParsedArgument) -> Any:
    return _value_.value


class Argparse(Variant):
    parse: ClassVar[
        Callable[
            [
                Union[str, List[str]],
                Optional[str],
                Optional[Union[str, int]],
                Optional[Any],
                Optional[Any],
                Optional[Type[Any]],
                Optional[Iterable[Any]],
                Optional[bool],
                Optional[str],
                Optional[str],
                Optional[str],
                List[str],
            ],
            ParsedArgument,
        ]
    ] = rewrite_function_parameters(
        parse_argument,
        "parse",
        f"_{VALUE}0_",
        f"_{VALUE}1_",
        f"_{VALUE}2_",
        f"_{VALUE}3_",
        f"_{VALUE}4_",
        f"_{VALUE}5_",
        f"_{VALUE}6_",
        f"_{VALUE}7_",
        f"_{VALUE}8_",
        f"_{VALUE}9_",
        f"_{VALUE}10_",
        f"_{VALUE}11_",
    )

    @staticmethod
    def to_argument_definition(value: Dict[str, Any]) -> ArgumentDefinition:
        return ArgumentDefinition.of(
            **{TYPE if k == ARGTYPE else k: v for k, v in value.items() if k != TYPE and k != ARGS}
        )

    @staticmethod
    def get_keys() -> List[str]:
        return [
            NAME,
            ACTION,
            NARGS,
            CONST,
            DEFAULT,
            ARGTYPE,
            CHOICES,
            REQUIRED,
            HELP,
            METAVAR,
            DEST,
            ARGS,
        ]

    @classmethod
    def reduce(cls, value: Any) -> Any:
        actions = [value[key] for key in cls.get_keys()]
        actions.append(cls.parse)
        actions.append(_get_argparse_value)
        return actions

    @classmethod
    def verify(cls, value: Any) -> None:
        for key in cls.get_keys():
            _EXPECT_CALLABLE_AT_KEY(value, key)
        return value

    def _init_simplifications_for_variant(self) -> None:
        super()._init_simplifications_for_variant()

        self._variant_simplifications.append(
            (_NAME_NOT_CALLABLE, _TRANSFORM_WHEN_NAME_NOT_CALLABLE)
        )

        for key in self.get_keys()[1:-1]:
            MISSING = partial(IS_DICT_MISSING_KEY, key=key)
            TRANSFORM_WHEN_MISSING = partial(_TRANSFORM_DICTVALUE_TO_NONE, key=key)

            if key == ARGTYPE:
                NOT_CALLABLE = _ARGTYPE_NOT_CALLABLE
            else:
                NOT_CALLABLE = partial(IS_DICTVALUE_NOT_CALLABLE, key=key)

            TRANSFORM_WHEN_NOT_CALLABLE = partial(_TRANSFORM_DICTVALUE_TO_CALLABLE, key=key)

            self._variant_simplifications.append((MISSING, TRANSFORM_WHEN_MISSING))
            self._variant_simplifications.append((NOT_CALLABLE, TRANSFORM_WHEN_NOT_CALLABLE))

        self._variant_simplifications.append((_MISSING_ARGS, _TRANSFORM_WHEN_MISSING_ARGS))
        self._variant_simplifications.append(
            (_ARGS_NOT_CALLABLE, _TRANSFORM_WHEN_ARGS_NOT_CALLABLE)
        )


ARGPARSE = Argparse.get_name()


def _TRANSFORM_WHEN_NOT_LIST(value: Callable[..., Any]) -> List[Callable[..., Any]]:
    return [value]


class AbstractAction(Middleware):
    actions: List[Callable[..., Any]]

    @classmethod
    def verify(cls, value: Any) -> None:
        super().verify(value)

        if IS_NOT_LIST_OF_CALLABLE(value):
            raise TypeError(f"{value} should be a callable or a list of callable")

    def _init_simplifications(self) -> None:
        super()._init_simplifications()

        self.simplifications.append((AND(IS_NOT_LIST, IS_NOT_CALLABLE), IDENTITY_FACTORY))

        self.simplifications.append((AND(IS_LIST, IS_NOT_LIST_OF_CALLABLE), IDENTITY_FACTORY))

        self.simplifications.append((IS_NOT_LIST, _TRANSFORM_WHEN_NOT_LIST))

    def _do_parse(self, value: List[Callable[..., Any]]) -> Dict[str, Any]:
        self.verify(value)

        return {"actions": value}

    async def _do_apply(self, context: Context) -> Scoped:
        for index, action in enumerate(self.actions):
            result = await context.submit(action)
            context.scoped.setmagic(f"{VALUE}{index}", result)
            context.scoped.setmagic(VALUE, result)

        await context.next()
        return context.scoped


class Action(AbstractAction, WithVariants):
    def _init_variants(self) -> None:
        super()._init_variants()

        self.variants.extend([Shell(), Argparse()])


ACTION = Action.get_name()
