from typing import Union
from dataclasses import dataclass


class ErrorFormatFailure(Exception):
    """
    Exception raised for an issue formatting the exception message.

    Args:
        exception_message: The invalid key reason.
    """
    __module__ = 'builtins'

    exception_message: str

    def __init__(self, exception_message: str) -> None:
        self.exception_message = exception_message


class InputFailure(Exception):
    """
    Exception raised for an input exception message.

    Args:
        exception_message: The incorrect input reason.
    """
    __module__ = 'builtins'

    exception_message: str

    def __init__(self, exception_message: str) -> None:
        self.exception_message = exception_message


@dataclass
class ProcessedMessageArgs:
    """
    Processed exception info to format the exception message.

    Args:
        main_message (str): The main exception message.\\
        expected_result (Union[str, list], Optional): The expected result.\\
        \tstr vs list:
        \t\tA string will be a single formatted line.\\
        \t\tA list will be split into individual formatted lines.\\
        returned_result (Union[str, list], Optional): The returned result.\\
        \tstr vs list:
        \t\tA string will be a single formatted line.\\
        \t\tA list will be split into individual formatted lines.\\
        suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
        \tstr vs list:
        \t\tA string will be a single formatted line.\\
        \t\tA list will be split into individual formatted lines.\\
        original_exception (any, Optional): The original exception.\\
    """
    __slots__ = ("main_message", "expected_result", "returned_result",
                 "suggested_resolution", "original_exception")

    main_message: str
    expected_result: Union[str, list]
    returned_result: Union[str, list]
    suggested_resolution: Union[str, list]
    original_exception: Exception


@dataclass
class ExceptionArgs:
    """
    Exception args to construct the formatted exception message.

    Args:
        exception_type (Exception): The exception type.
        caller_module (str): Exception caller module.
        caller_line (int): Exception caller line.
        caller_name (str): Exception function or class name.
        traceback (bool): Display traceback details. Defaults to True.
        all_tracing (bool): True will display all traceback calls. False will show most recent. Defaults to True.
    """
    __slots__ = "exception_type", "caller_module", "caller_line", "caller_name", "traceback", "all_tracing"

    exception_type: Exception
    caller_module: str
    caller_line: int
    caller_name: str
    traceback: bool
    all_tracing: bool


@dataclass
class HookArgs:
    """
    Exception hook args used to return the formatted raised exception message.

    Args:
        formatted_exception (str): The formatted exception message.
        exception_args (ExceptionArgs): The exception constructor args.
    """
    __slots__ = "formatted_exception", "exception_args"

    formatted_exception: str
    exception_args: ExceptionArgs
