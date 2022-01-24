from __future__ import annotations

__all__ = [
    "warning_on_one_line",
    "check_function_arity",
    "get_function_source_code",
    "patch_lambda_function_name",
    "functionify_lambda",
    "get_formatted_function_source_code",
    "escape_non_alphanumeric",
    "ascii_to_character",
    "convert_id_to_sbml",
    "convert_sbml_id",
]


import inspect
import re
import subprocess
import warnings
from typing import Any, Callable, Optional, Type, Union

RE_LAMBDA_FUNC = re.compile(r".*(lambda)(.+?):(.*?)")
RE_LAMBDA_RATE_FUNC = re.compile(r".*(lambda)(.+?):(.*?),")
RE_LAMBDA_ALGEBRAIC_MODULE_FUNC = re.compile(r".*(lambda)(.+?):(.*[\(\[].+[\)\]]),")
RE_TO_SBML = re.compile(r"([^0-9_a-zA-Z])")
RE_FROM_SBML = re.compile(r"__(\d+)__")
SBML_DOT = "__SBML_DOT__"


def warning_on_one_line(
    message: Union[Warning, str],
    category: Type[Warning],
    _filename: str,
    _lineno: int,
    _line: Optional[int] = None,
) -> str:  # type: ignore
    """Format warnings to only show the message."""
    return f"{category.__name__}: {message}\n"


warnings.formatwarning = warning_on_one_line  # type: ignore


##########################################################################
# Source code functions
##########################################################################


def check_function_arity(function: Callable, arity: int) -> bool:
    """Check if the amount of arguments given fits the argument count of the function"""
    argspec = inspect.getfullargspec(function)
    # Give up on *args functions
    if argspec.varargs is not None:
        return True

    # The sane case
    if len(argspec.args) == arity:
        return True

    # It might be that the user has set some args to default values,
    # in which case they are also ok (might be kwonly as well)
    defaults = argspec.defaults
    if defaults is not None:
        if len(argspec.args) + len(defaults) == arity:
            return True
    kwonly = argspec.kwonlyargs
    if defaults is not None:
        if len(argspec.args) + len(kwonly) == arity:
            return True
    return False


def get_function_source_code(function: Callable) -> Optional[str]:
    """Get source code of a function."""
    try:
        return inspect.getsource(function)[:-1]  # Remove line break
    except OSError:
        pass
    try:
        # for functions parsed and dynamically executed with modelbase/sbml/parser
        source: str = function.__source__  # type: ignore
        return source
    except AttributeError:
        return None


def patch_lambda_function_name(function: Callable, name: str) -> None:
    """Add a name to a lambda function."""
    if function.__name__ == "<lambda>":
        function.__name__ = name


def functionify_lambda(lambda_function_code: str, function_name: str, pattern: re.Pattern[str]) -> str:
    """Convert lambda function to a proper function."""
    match = re.match(pattern=pattern, string=lambda_function_code)
    if match is None:
        raise ValueError("Could not find pattern")
    _, args, code = match.groups()
    return f"def {function_name}({args.strip()}):\n    return {code.strip()}"


def get_formatted_function_source_code(function_name: str, function: Callable, function_type: str) -> str:
    """Get source code of a function and format it using black."""
    source = get_function_source_code(function=function)

    if source is None:
        raise ValueError("Cannot find function source")

    if "lambda" in source:
        if function_type == "rate":
            source = functionify_lambda(
                lambda_function_code=source,
                function_name=function_name,
                pattern=RE_LAMBDA_RATE_FUNC,
            )
        elif function_type == "module":
            source = functionify_lambda(
                lambda_function_code=source,
                function_name=function_name,
                pattern=RE_LAMBDA_ALGEBRAIC_MODULE_FUNC,
            )
        elif function_type == "function":
            source = functionify_lambda(
                lambda_function_code=source,
                function_name=function_name,
                pattern=RE_LAMBDA_FUNC,
            )
        else:
            raise ValueError("Can only handle rate or module functions")
    blacked_string = subprocess.run(["black", "--fast", "--code", source], stdout=subprocess.PIPE, check=True)
    return blacked_string.stdout.decode("utf-8").strip()  # Removing new lines


##########################################################################
# SBML functions
##########################################################################


def escape_non_alphanumeric(re_sub: Any) -> str:
    """Convert a non-alphanumeric charactor to a string representation of its ascii number."""
    return f"__{ord(re_sub.group(0))}__"


def ascii_to_character(re_sub: Any) -> str:
    """Convert an escaped non-alphanumeric character."""
    return chr(int(re_sub.group(1)))


def convert_id_to_sbml(id_: str, prefix: str) -> str:
    """Add prefix if id startswith number."""
    new_id = RE_TO_SBML.sub(escape_non_alphanumeric, id_).replace(".", SBML_DOT)
    if not new_id[0].isalpha():
        return f"{prefix}_{new_id}"
    return new_id


def convert_sbml_id(sbml_id: str, prefix: str) -> str:
    """Convert an model object id to sbml-compatible string.

    Adds a prefix if the id starts with a number."""
    new_id = sbml_id.replace(SBML_DOT, ".")
    new_id = RE_FROM_SBML.sub(ascii_to_character, new_id)
    return new_id.lstrip(f"{prefix}_")
