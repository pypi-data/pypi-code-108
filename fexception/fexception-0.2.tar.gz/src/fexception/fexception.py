"""
This is the starting point for the exceptions. Install fexception, set the module (fexception) and load the exception.
This module creates additional information formatted exception output based on the built-in Python exceptions.
All formatted exceptions are based on one level of the built-in Python exception hierarchy.
"""
from typing import Optional
import dataclasses
import inspect
import sys
from pathlib import Path

from .formatter import exception_formatter
from .util import KeyCheck, get_line_number
from .common import (
    ProcessedMessageArgs, ExceptionArgs, HookArgs,
    ErrorFormatFailure, InputFailure
)


# ########################################################
# #############Processes The Exception Message############
# ########################################################


class ExceptionProcessor:
    """
    Processes the exception message arguments and makes the middleman calls.

    Args:
        message_args (ProcessedMessageArgs): Exception message args.
        exception_args (ExceptionArgs): Exception args to construct the formatted exception message.
    """
    def __init__(self, message_args: ProcessedMessageArgs, exception_args: ExceptionArgs) -> None:
        try:
            self._processed_message_args = ConvertMessageArgs(message_args, exception_args).set_message_args()
            # Formats the exception message based on the args.
            self._formatted_exception = exception_formatter(self._processed_message_args, exception_args)
            self._exception_args = exception_args
        except InputFailure as exec:
            # Updates the selected exception_type to the internal exception error.
            exception_args = dataclasses.replace(exception_args, exception_type=InputFailure)
            exception_args = dataclasses.replace(exception_args, traceback=True)
            exception_args = dataclasses.replace(exception_args, all_tracing=True)
            # Sets formatted exception to the internal exception error.
            self._formatted_exception = exec
            self._exception_args = exception_args
            SetLocalExceptionHook(HookArgs(formatted_exception=exec, exception_args=self._exception_args))
        except ErrorFormatFailure as exec:
            # Updates the selected exception_type to the internal exception error.
            exception_args = dataclasses.replace(exception_args, exception_type=ErrorFormatFailure)
            exception_args = dataclasses.replace(exception_args, traceback=True)
            exception_args = dataclasses.replace(exception_args, all_tracing=True)
            # Sets formatted exception to the internal exception error.
            self._formatted_exception = exec
            self._exception_args = exception_args
            SetLocalExceptionHook(HookArgs(formatted_exception=exec, exception_args=self._exception_args))
        else:
            SetExceptionHook(HookArgs(formatted_exception=self._formatted_exception,
                                      exception_args=self._exception_args))

    def __str__(self) -> str:
        """
        Returns the formatted exception for use in nested formatted exceptions
        or other areas when the exception is not raised.
        """
        return str(self._formatted_exception)


class ConvertMessageArgs(ExceptionProcessor):
    """
    Validates the correct message_args keys are sent and converts the dictionary entries to a dataclass.

    Args:
        message_args (dict): Exception message args.
        exception_args (ExceptionArgs): Exception args to construct the formatted exception message.
    """
    def __init__(self, message_args: dict, exception_args: ExceptionArgs) -> None:
        self._message_args = message_args
        self._caller_module = exception_args.caller_module
        self._caller_name = exception_args.caller_name
        self._caller_line = exception_args.caller_line
        self._traceback = exception_args.traceback
        self._all_tracing = exception_args.all_tracing

    def set_message_args(self) -> ProcessedMessageArgs:
        if not isinstance(self._message_args, dict):
            raise InputFailure('Dictionary format is the required input to format an exception message. '
                               'Single line messages should use the built-in Python exceptions.')
        if not isinstance(self._traceback, bool) or not isinstance(self._all_tracing, bool):
            raise InputFailure('Bool format is the required input to set the traceback options.')
        try:
            # Creates a sample dictionary key to use as a contains match for the incoming exception formatter keys.
            match_dict_key = {'main_message': None, 'expected_result': None, 'returned_result': None,
                              'suggested_resolution': None, 'original_exception': None}
            # Pulls the keys from the importing exception dictionary.
            importing_exception_keys = list(self._message_args.keys())
            key_check = KeyCheck(match_dict_key,
                                 self._caller_module,
                                 self._caller_name,
                                 self._caller_line)
            key_check.contains_keys(importing_exception_keys)

            main_message = self._message_args.get('main_message')
            expected_result = self._message_args.get('expected_result')
            returned_result = self._message_args.get('returned_result')
            suggested_resolution = self._message_args.get('suggested_resolution')
            original_exception = self._message_args.get('original_exception')
        except Exception as exec:
            raise InputFailure(exec)
        else:
            return ProcessedMessageArgs(
                main_message=main_message,
                expected_result=expected_result,
                returned_result=returned_result,
                suggested_resolution=suggested_resolution,
                original_exception=original_exception,
            )


class SetLocalExceptionHook(ExceptionProcessor):
    """
    Local exception hook to sets the most recent failure last call in
    the traceback output or no traceback output.

    Args:
        message (str): The local module exception message.
    """
    def __init__(self, hook_args: HookArgs) -> None:
        self._formatted_exception = hook_args.formatted_exception
        self.exception_type = hook_args.exception_args.exception_type
        self._traceback = hook_args.exception_args.traceback
        self._all_tracing = hook_args.exception_args.all_tracing

        # Except hook will use custom exceptions and a formatted message,
        # so the kind and message variables will not be used but must exist.
        def except_hook(kind, message, traceback) -> sys.excepthook:
            # Returns the selected custom exception class and the formatted exception message.
            # Includes traceback.
            sys.__excepthook__(self.exception_type, self.exception_type(self._formatted_exception), traceback)

        sys.excepthook = except_hook


class SetExceptionHook(ExceptionProcessor):
    """
    Sets the message exception hook to set the most recent failure\\
    last call in the traceback output, or, full exception with traceback,\\
    or no traceback.

    No other raised exception tracebacks display when traceback is enabled.

    Note: traceback and all_tracing must be default True for each Exception class.

    Args:
        hook_args (HookArgs): The formatted excpetion message and exception args.
    """
    def __init__(self, hook_args: HookArgs) -> None:
        self._formatted_exception = hook_args.formatted_exception
        self.exception_type = hook_args.exception_args.exception_type
        self._traceback = hook_args.exception_args.traceback
        self._all_tracing = hook_args.exception_args.all_tracing

        # Except hook will use custom exceptions and a formatted message,
        # so the kind and message variables will not be used but must exist.
        def except_hook(kind, message, traceback) -> sys.excepthook:
            if self._traceback:
                # Returns the selected custom exception class and the formatted exception message.
                # Includes traceback.
                sys.__excepthook__(self.exception_type, self.exception_type(self._formatted_exception), traceback)
            else:
                # Returns the selected custom exception class and the formatted exception message.
                # No traceback.
                print(f'{self.exception_type.__name__}:', self._formatted_exception)

        # Checks if all tracing output is disabled or if traceback is disabled with the
        # default all_tracing flag set to True. Calling sys.excepthook adjusts the way the
        # exception is displayed.
        if (
            (self._all_tracing is False)
            or (self._traceback is False and self._all_tracing is True)
        ):
            sys.excepthook = except_hook


# ########################################################
# #################Base Exception Classes#################
# ########################################################


class FKBaseException(Exception):
    """
    Formatted 'Base Exception' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Base Exception' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FKBaseException,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FException(Exception):
    """
    Formatted 'Exception' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Exception' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FException,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FArithmeticError(Exception):
    """
    Formatted 'Arithmetic Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Arithmetic Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FArithmeticError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FBufferError(Exception):
    """
    Formatted 'Buffer Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Buffer Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FBufferError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FLookupError(Exception):
    """
    Formatted 'Lookup Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Lookup Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FLookupError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


# ########################################################
# ###############Concrete Exception Classes###############
# ########################################################


class FAssertionError(Exception):
    """
    Formatted 'Assertion Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Assertion Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FAssertionError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FAttributeError(Exception):
    """
    Formatted 'Attribute Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Attribute Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FAttributeError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FEOFError(Exception):
    """
    Formatted 'EOF Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'EOF Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FEOFError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFloatingPointError(Exception):
    """
    Formatted 'FloatingPoint Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'FloatingPoint Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FFloatingPointError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FGeneratorExit(Exception):
    """
    Formatted 'Generator Exit' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Generator Exit' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FGeneratorExit,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FImportError(Exception):
    """
    Formatted 'Import Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Import Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FImportError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FModuleNotFoundError(Exception):
    """
    Formatted 'ModuleNotFound Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'ModuleNotFound Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FModuleNotFoundError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIndexError(Exception):
    """
    Formatted 'Index Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Index Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FIndexError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FKeyError(Exception):
    """
    Formatted 'Key Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Key Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FKeyError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FKeyboardInterrupt(Exception):
    """
    Formatted 'Keyboard Interrupt' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Keyboard Interrupt' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FKeyboardInterrupt,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FMemoryError(Exception):
    """
    Formatted 'Memory Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Memory Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FMemoryError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FNameError(Exception):
    """
    Formatted 'Name Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Name Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FNameError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FNotImplementedError(Exception):
    """
    Formatted 'NotImplemented Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted ''NotImplemented Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FNotImplementedError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FOSError(Exception):
    """
    Formatted 'OS Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'OS Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FOSError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FOverflowError(Exception):
    """
    Formatted 'Overflow Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Overflow Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FOverflowError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FRecursionError(Exception):
    """
    Formatted 'Recursion Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Recursion Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FRecursionError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FReferenceError(Exception):
    """
    Formatted 'Reference Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Reference Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FReferenceError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FRuntimeError(Exception):
    """
    Formatted 'Runtime Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Runtime Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FRuntimeError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FStopIteration(Exception):
    """
    Formatted 'Stop Iteration' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Stop Iteration' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FStopIteration,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FStopAsyncIteration(Exception):
    """
    Formatted 'StopAsync Iteration' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'StopAsync Iteration' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FStopAsyncIteration,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSyntaxError(Exception):
    """
    Formatted 'Syntax Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Syntax Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FSyntaxError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIndentationError(Exception):
    """
    Formatted 'Indentation Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Indentation Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FIndentationError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FTabError(Exception):
    """
    Formatted 'Tab Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Tab Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FTabError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSystemError(Exception):
    """
    Formatted 'System Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'System Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FSystemError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSystemExit(Exception):
    """
    Formatted 'System Exit' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'System Exit' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FSystemExit,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FTypeError(Exception):
    """
    Formatted 'Type Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Type Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FTypeError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnboundLocalError(Exception):
    """
    Formatted 'Unbound Local Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Unbound Local Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FUnboundLocalError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeError(Exception):
    """
    Formatted 'Unicode Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Unicode Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FUnicodeError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeEncodeError(Exception):
    """
    Formatted 'Unicode Encode Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Unicode Encode Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FUnicodeEncodeError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeDecodeError(Exception):
    """
    Formatted 'Unicode Decode Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Unicode Decode Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FUnicodeDecodeError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeTranslateError(Exception):
    """
    Formatted 'Unicode Translate Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Unicode Translate Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FUnicodeTranslateError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FValueError(Exception):
    """
    Formatted 'Value Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Value Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FValueError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FZeroDivisionError(Exception):
    """
    Formatted 'Zero Division Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Zero Division Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FZeroDivisionError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FEnvironmentError(Exception):
    """
    Formatted 'Environment Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Environment Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FEnvironmentError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIOError(Exception):
    """
    Formatted 'IO Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'IO Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FIOError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FWindowsError(Exception):
    """
    Formatted 'Windows Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Windows Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FWindowsError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


# ########################################################
# ##################OS Exception Classes##################
# ########################################################


class FBlockingIOError(Exception):
    """
    Formatted 'BlockingIO Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'BlockingIO Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FBlockingIOError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FChildProcessError(Exception):
    """
    Formatted 'Child Process Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Child Process Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FChildProcessError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionError(Exception):
    """
    Formatted 'Connection Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Connection Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FConnectionError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FBrokenPipeError(Exception):
    """
    Formatted 'Broken Pipe Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Broken Pipe Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FBrokenPipeError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionAbortedError(Exception):
    """
    Formatted 'Connection Aborted Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Connection Aborted Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FConnectionAbortedError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionRefusedError(Exception):
    """
    Formatted 'Connection Refused Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Connection Refused Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FConnectionRefusedError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionResetError(Exception):
    """
    Formatted 'Connection Reset Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Connection Reset Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FConnectionResetError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFileExistsError(Exception):
    """
    Formatted 'File Exists Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'File Exists Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FFileExistsError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFileNotFoundError(Exception):
    """
    Formatted 'FileNotFound Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'FileNotFound Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FFileNotFoundError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FInterruptedError(Exception):
    """
    Formatted 'Interrupted Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Interrupted Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FInterruptedError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIsADirectoryError(Exception):
    """
    Formatted 'IsADirectory Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'IsADirectory Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FIsADirectoryError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FNotADirectoryError(Exception):
    """
    Formatted 'NotADirectory Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'NotADirectory Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FNotADirectoryError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FPermissionError(Exception):
    """
    Formatted 'Permission Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Permission Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FPermissionError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FProcessLookupError(Exception):
    """
    Formatted 'Process Lookup Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Process Lookup Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FProcessLookupError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FTimeoutError(Exception):
    """
    Formatted 'Timeout Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Timeout Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FTimeoutError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


# ########################################################
# ####################Warnings Classes####################
# ########################################################


class FWarning(Exception):
    """
    Formatted 'Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUserWarning(Exception):
    """
    Formatted 'User Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'User Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FUserWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FDeprecationWarning(Exception):
    """
    Formatted 'Deprecation Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Deprecation Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FDeprecationWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FPendingDeprecationWarning(Exception):
    """
    Formatted 'Pending Deprecation Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Pending Deprecation Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FPendingDeprecationWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSyntaxWarning(Exception):
    """
    Formatted 'Syntax Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Syntax Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FSyntaxWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FRuntimeWarning(Exception):
    """
    Formatted 'Runtime Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Runtime Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FRuntimeWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFutureWarning(Exception):
    """
    Formatted 'Future Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Future Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FFutureWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FImportWarning(Exception):
    """
    Formatted 'Import Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Import Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FImportWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeWarning(Exception):
    """
    Formatted 'Unicode Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Unicode Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FUnicodeWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FEncodingWarning(Exception):
    """
    Formatted 'Encoding Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Encoding Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FEncodingWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FBytesWarning(Exception):
    """
    Formatted 'Bytes Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Bytes Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FBytesWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FResourceWarning(Exception):
    """
    Formatted 'Resource Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Resource Warning' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FResourceWarning,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


# ########################################################
# ###############Additional General Classes###############
# ########################################################


class FCustomException(Exception):
    """
    Formatted 'Custom Exception' with additional exception message options.

    This class is ideal for defining custom exceptions within a module and having the exception formatted, but using your custom exception name.

    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'Custom Exception' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
                custom_type (custom_type, Optional): The custom exception type.
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:

            # The custom exception option accepts custom exception types.
            # A few additional steps are required for this method.
            if not isinstance(message_args, dict):
                raise InputFailure('Dictionary format is the required input to format an exception message. '
                                   'Single line messages should use the built-in Python exceptions.')

            custom_type = message_args.get('custom_type')
            if not isinstance(custom_type, type):
                raise InputFailure('A pre-configured exception class is required to use the FCustomException formatter class.')

            try:
                # Creates a sample dictionary key to use as a contains match for the incoming exception formatter keys.
                match_dict_key = {'main_message': None, 'expected_result': None, 'returned_result': None,
                                  'suggested_resolution': None, 'original_exception': None, 'custom_type': None}
                # Pulls the keys from the importing exception dictionary.
                importing_exception_keys = list(message_args.keys())
                key_check = KeyCheck(match_dict_key,
                                     Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                     inspect.currentframe().f_back.f_code.co_name,
                                     inspect.currentframe().f_back.f_lineno)
                key_check.contains_keys(importing_exception_keys)
            except Exception as exec:
                raise InputFailure(exec)

            custom_type = message_args.get('custom_type')
            # Deletes the custom key and value from the message_args because this key is not allowed through other validations.
            del message_args['custom_type']
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=custom_type,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            Exception.__init__(self, self._formatted_exception)


# ########################################################
# ###############IC Tools Companion Classes###############
# ########################################################


class FGeneralError(Exception):
    """
    Formatted 'General Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, traceback: Optional[bool] = True, all_tracing: Optional[bool] = True) -> None:
        """
        Formatted 'General Error' with additional exception message options.

        Args:
            message_args (Union[dict, str]): Dictionary will create a formatted exception message.
            traceback (bool, Optional): Displays most recent traceback output. Defaults to True.
            all_tracing (bool, Optional): True displays all traceback. False will show most recent. Defaults to True.

            Keys:\\
                main_message (str): The main exception message.\\
                expected_result (Union[str, list], Optional): The expected result.\\
                returned_result (Union[str, list], Optional): The returned result.\\
                suggested_resolution (Union[str, list], Optional): A suggested resolution.\\
                original_exception (any, Optional): The original exception.\\
        """
        # except_hook is the function that returns the formatted exception.
        # When the formatted message is returned, the calling function is used to set the class.
        if 'except_hook' == inspect.currentframe().f_back.f_code.co_name:
            pass
        else:
            self._formatted_exception = ExceptionProcessor(message_args,
                                                           ExceptionArgs(exception_type=FGeneralError,
                                                                         caller_module=Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                                                                         caller_line=inspect.currentframe().f_back.f_lineno,
                                                                         caller_name=inspect.currentframe().f_back.f_code.co_name,
                                                                         traceback=traceback,
                                                                         all_tracing=all_tracing))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)
