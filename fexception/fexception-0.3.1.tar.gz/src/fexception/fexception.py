"""
This is the starting point for the exceptions. Install fexception, set the module (fexception) and load the exception.
This module creates additional information formatted exception output based on the built-in Python exceptions.
All formatted exceptions are based on one level of the built-in Python exception hierarchy.
"""
import dataclasses
import inspect
import sys
import os
import traceback
from typing import Optional
from pathlib import Path


from .formatter import exception_formatter
from .util import InvalidKeyError, KeyCheck
from .common import (
    ProcessedMessageArgs, ProcessedOverrideArgs,
    ExceptionArgs, HookArgs,
    ErrorFormatFailure, InputFailure
)


# ########################################################
# #############Processes The Exception Message############
# ########################################################


class ExceptionProcessor:
    """Processes the exception message arguments and makes the middleman calls."""
    def __init__(self, message_args: dict, exception_args: ExceptionArgs) -> None:
        """
        Processes the exception message arguments and makes the middleman calls.

        Args:
            message_args (ProcessedMessageArgs):\\
            \t\\- Exception message args.
            exception_args (ExceptionArgs):\\
            \t\\- Exception args to construct the formatted exception message.
        """
        try:
            self._processed_message_args = ConvertArgs(message_args, exception_args).set_message_args()
            self._processed_override_args = ConvertArgs(message_args, exception_args).set_override_args()
            # Checks if override args are set.
            if 'module=None, name=None, line=None' not in str(self._processed_override_args):
                # Updates the ExceptionArgs dataclass args with the override values.
                exception_args = dataclasses.replace(exception_args,
                                                     caller_module=self._processed_override_args.module)
                exception_args = dataclasses.replace(exception_args,
                                                     caller_name=self._processed_override_args.name)
                exception_args = dataclasses.replace(exception_args,
                                                     caller_line=self._processed_override_args.line)
            # Formats the exception message based on the args.
            self._formatted_exception = exception_formatter(self._processed_message_args, exception_args)
            self._exception_args = exception_args
        except InputFailure as exec:
            # Updates the selected exception_type to the internal exception error.
            exception_args = dataclasses.replace(exception_args, exception_type=InputFailure)
            exception_args = dataclasses.replace(exception_args, tb_limit=None)
            exception_args = dataclasses.replace(exception_args, caller_override=None)
            # Sets formatted exception to the internal exception error.
            self._formatted_exception = exec
            self._exception_args = exception_args
            SetLocalExceptionHook(HookArgs(formatted_exception=exec, exception_args=self._exception_args))
        except ErrorFormatFailure as exec:
            # Updates the selected exception_type to the internal exception error.
            exception_args = dataclasses.replace(exception_args, exception_type=ErrorFormatFailure)
            exception_args = dataclasses.replace(exception_args, tb_limit=None)
            exception_args = dataclasses.replace(exception_args, caller_override=None)
            # Sets formatted exception to the internal exception error.
            self._formatted_exception = exec
            self._exception_args = exception_args
            SetLocalExceptionHook(HookArgs(formatted_exception=exec, exception_args=self._exception_args))
        else:
            SetExceptionHook(HookArgs(formatted_exception=self._formatted_exception,
                                      exception_args=self._exception_args))

    def __str__(self) -> str:
        """
        Returns the formatted exception for use in nested formatted\\
        exceptions or other areas when the exception is not raised.
        """
        return str(self._formatted_exception)


class ConvertArgs(ExceptionProcessor):
    """Validates the correct message_args keys are sent\\
        and converts the dictionary entries to a dataclass."""

    def __init__(self, message_args: dict, exception_args: ExceptionArgs) -> None:
        """
        Validates the correct message_args keys are sent\\
        and converts the dictionary entries to a dataclass.

        Args:
            message_args (dict):\\
            \t\\- Exception message args.
            exception_args (ExceptionArgs):\\
            \t\\- Exception args to construct the formatted exception message.
        """
        self._message_args = message_args
        self._caller_module = exception_args.caller_module
        self._caller_name = exception_args.caller_name
        self._caller_line = exception_args.caller_line
        self._tb_limit = exception_args.tb_limit
        self._caller_override = exception_args.caller_override

    def set_message_args(self) -> ProcessedMessageArgs:
        """
        Validates the correct message_args keys are sent\\
        and converts the dictionary entries to a dataclass.

        Raises:
            InputFailure:\\
            \t\\- Dictionary format is the required input to format an exception message.\\
            \t   Single line messages should use the built-in Python exceptions.
            InputFailure:\\
            \t\\- int format is the required input to set the traceback limit option.
            InputFailure:\\
            \t\\- KeyCheck raised exceptions.

        Returns:
            ProcessedMessageArgs: Message arguments in the dataclass.
        """
        if not isinstance(self._message_args, dict):
            raise InputFailure('Dictionary format is the required input to format an exception message. '
                               'Single line messages should use the built-in Python exceptions.')
        if self._tb_limit:
            if not isinstance(self._tb_limit, int):
                raise InputFailure('int format is the required input to set the traceback limit option.')

        try:
            # Creates a sample dictionary key to use as a contains match for the incoming exception formatter keys.
            match_dict_key = {'main_message': None, 'expected_result': None, 'returned_result': None,
                              'suggested_resolution': None, 'original_exception': None, 'original_exception': None}
            # Pulls the keys from the importing exception dictionary.
            importing_exception_keys = list(self._message_args.keys())
            key_check = KeyCheck(match_dict_key,
                                 self._caller_module,
                                 self._caller_name,
                                 self._caller_line)
            key_check.contains_keys(importing_exception_keys, reverse=True)

            main_message = self._message_args.get('main_message')
            expected_result = self._message_args.get('expected_result')
            returned_result = self._message_args.get('returned_result')
            suggested_resolution = self._message_args.get('suggested_resolution')
            original_exception = self._message_args.get('original_exception')
        except (AttributeError, InvalidKeyError) as exec:
            raise InputFailure(exec)
        else:
            return ProcessedMessageArgs(
                main_message=main_message,
                expected_result=expected_result,
                returned_result=returned_result,
                suggested_resolution=suggested_resolution,
                original_exception=original_exception,
            )

    def set_override_args(self) -> ProcessedOverrideArgs:
        """
        Validates the correct caller_override keys are sent and converts the dictionary entries to a dataclass.

        Raises:
            InputFailure:\\
            \t\\- dict format is the required input to set the caller override option.
            InputFailure:\\
            \t\\- KeyCheck raised exceptions.

        Returns:
            ProcessedOverrideArgs: Overide arguments in the dataclass.
        """
        if self._caller_override:
            if not isinstance(self._caller_override, dict):
                raise InputFailure('dict format is the required input to set the caller override option.')

            try:
                # Creates a sample dictionary key to use as a contains match for the incoming exception formatter keys.
                match_dict_key = {'module': None, 'name': None, 'line': None, 'tb_remove': None}
                # Pulls the keys from the importing exception dictionary.
                importing_exception_keys = list(self._caller_override.keys())
                key_check = KeyCheck(match_dict_key,
                                     self._caller_module,
                                     self._caller_name,
                                     self._caller_line)
                key_check.all_keys(importing_exception_keys, reverse=True)

                # Gets the dictionary values to set the overide arg
                module = self._caller_override.get('module')
                name = self._caller_override.get('name')
                line = self._caller_override.get('line')
            except (AttributeError, InvalidKeyError) as exec:
                raise InputFailure(exec)
            else:
                return ProcessedOverrideArgs(
                    module=module,
                    name=name,
                    line=line,
                )
        else:
            return ProcessedOverrideArgs(
                module=None,
                name=None,
                line=None,
            )


class SetLocalExceptionHook(ExceptionProcessor):
    """Local exception hook to sets the most recent failure"""

    def __init__(self, hook_args: HookArgs) -> None:
        """
        Local exception hook to sets the most recent failure\\
        last call in the traceback output or no traceback output.

        Args:
            message (str): The local module exception message.
        """
        self._formatted_exception = hook_args.formatted_exception
        self.exception_type = hook_args.exception_args.exception_type

        # Except hook will use custom exceptions and a formatted message,
        # so the kind and message variables will not be used but must exist.
        def except_hook(kind, message, tb) -> sys.excepthook:
            # Returns the selected custom exception class and the formatted exception message.
            # Includes traceback.
            sys.__excepthook__(self.exception_type, self.exception_type(self._formatted_exception), tb)

        sys.excepthook = except_hook


class SetExceptionHook(ExceptionProcessor):
    """Sets the message exception hook to most recent failure"""

    def __init__(self, hook_args: HookArgs) -> None:
        """
        Sets the message exception hook to most recent failure\\
        last call in the traceback output or no traceback.\\

        Supports limited traceback output.

        Supports traceback module removal.
    
        Args:
            hook_args (HookArgs):\\
            \t\\- The formatted excpetion message and exception args.
        """
        self._formatted_exception = hook_args.formatted_exception
        self._exception_type = hook_args.exception_args.exception_type
        self._tb_limit = hook_args.exception_args.tb_limit
        if hook_args.exception_args.caller_override:
            self._tb_remove = hook_args.exception_args.caller_override.get('tb_remove')
        else:
            self._tb_remove = None

        # Except hook will use custom exceptions and a formatted message,
        # so the kind and message variables will not be used but must exist.
        def except_hook(kind, message, tb) -> sys.excepthook:
            # Checks of the user is setting the traceback limit with an index or override.
            if hook_args.exception_args.caller_override is not None:
                # Loops through each traceback to find the limit number.
                for tb_level_index, (frame, _) in enumerate(traceback.walk_tb(tb)):
                    if 'py' in self._tb_remove:
                        tb_remove = self._tb_remove
                    else:
                        tb_remove = f'{self._tb_remove}.py'
                    # Checks if the overwritten caller_module matches the trace to the
                    # traceback to the position before the overwritten caller_module name.
                    if os.path.basename(frame.f_code.co_filename) == tb_remove:
                        # Checks if a limit is set.
                        if self._tb_limit:
                            # Check if the set tb_limit is greater than the index.
                            if int(tb_level_index) > int(self._tb_limit):
                                # Set tb_limit less than the index, so the set tb_limit will be used.
                                limit = self._tb_limit
                            else:
                                # Set tb_limit was greater than the index. The index will be used
                                # for the displayed traceback.
                                limit = tb_level_index
                        else:
                            limit = tb_level_index
                        break
                    else:
                        limit = None
                else:
                    limit = None
                traceback.print_exception(self._exception_type,
                                          self._exception_type(self._formatted_exception),
                                          tb, limit=limit, chain=True)
            elif isinstance(self._tb_limit, int):
                traceback.print_exception(self._exception_type,
                                          self._exception_type(self._formatted_exception),
                                          tb,
                                          limit=self._tb_limit, chain=True)

        # Checks if a tb_limit is set or caller_override is enabled.
        if (
            self._tb_limit is not None
            or hook_args.exception_args.caller_override is not None
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

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Base Exception' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FException(Exception):
    """
    Formatted 'Exception' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Exception' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FArithmeticError(Exception):
    """
    Formatted 'Arithmetic Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Arithmetic Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FBufferError(Exception):
    """
    Formatted 'Buffer Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Buffer Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FLookupError(Exception):
    """
    Formatted 'Lookup Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Lookup Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

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

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Assertion Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FAttributeError(Exception):
    """
    Formatted 'Attribute Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Attribute Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FEOFError(Exception):
    """
    Formatted 'EOF Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'EOF Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFloatingPointError(Exception):
    """
    Formatted 'FloatingPoint Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'FloatingPoint Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FGeneratorExit(Exception):
    """
    Formatted 'Generator Exit' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Generator Exit' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FImportError(Exception):
    """
    Formatted 'Import Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Import Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FModuleNotFoundError(Exception):
    """
    Formatted 'ModuleNotFound Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'ModuleNotFound Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIndexError(Exception):
    """
    Formatted 'Index Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Index Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FKeyError(Exception):
    """
    Formatted 'Key Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Key Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FKeyboardInterrupt(Exception):
    """
    Formatted 'Keyboard Interrupt' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Keyboard Interrupt' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FMemoryError(Exception):
    """
    Formatted 'Memory Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Memory Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FNameError(Exception):
    """
    Formatted 'Name Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Name Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FNotImplementedError(Exception):
    """
    Formatted 'NotImplemented Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted ''NotImplemented Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FOSError(Exception):
    """
    Formatted 'OS Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'OS Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FOverflowError(Exception):
    """
    Formatted 'Overflow Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Overflow Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FRecursionError(Exception):
    """
    Formatted 'Recursion Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Recursion Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FReferenceError(Exception):
    """
    Formatted 'Reference Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Reference Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FRuntimeError(Exception):
    """
    Formatted 'Runtime Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Runtime Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FStopIteration(Exception):
    """
    Formatted 'Stop Iteration' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Stop Iteration' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FStopAsyncIteration(Exception):
    """
    Formatted 'StopAsync Iteration' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'StopAsync Iteration' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSyntaxError(Exception):
    """
    Formatted 'Syntax Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Syntax Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIndentationError(Exception):
    """
    Formatted 'Indentation Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Indentation Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FTabError(Exception):
    """
    Formatted 'Tab Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Tab Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSystemError(Exception):
    """
    Formatted 'System Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'System Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSystemExit(Exception):
    """
    Formatted 'System Exit' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'System Exit' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FTypeError(Exception):
    """
    Formatted 'Type Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Type Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnboundLocalError(Exception):
    """
    Formatted 'Unbound Local Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Unbound Local Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeError(Exception):
    """
    Formatted 'Unicode Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Unicode Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeEncodeError(Exception):
    """
    Formatted 'Unicode Encode Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Unicode Encode Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeDecodeError(Exception):
    """
    Formatted 'Unicode Decode Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Unicode Decode Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeTranslateError(Exception):
    """
    Formatted 'Unicode Translate Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Unicode Translate Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FValueError(Exception):
    """
    Formatted 'Value Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Value Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FZeroDivisionError(Exception):
    """
    Formatted 'Zero Division Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Zero Division Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FEnvironmentError(Exception):
    """
    Formatted 'Environment Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Environment Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIOError(Exception):
    """
    Formatted 'IO Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'IO Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FWindowsError(Exception):
    """
    Formatted 'Windows Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Windows Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

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

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'BlockingIO Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FChildProcessError(Exception):
    """
    Formatted 'Child Process Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Child Process Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionError(Exception):
    """
    Formatted 'Connection Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Connection Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FBrokenPipeError(Exception):
    """
    Formatted 'Broken Pipe Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Broken Pipe Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionAbortedError(Exception):
    """
    Formatted 'Connection Aborted Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Connection Aborted Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionRefusedError(Exception):
    """
    Formatted 'Connection Refused Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Connection Refused Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FConnectionResetError(Exception):
    """
    Formatted 'Connection Reset Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Connection Reset Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFileExistsError(Exception):
    """
    Formatted 'File Exists Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'File Exists Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFileNotFoundError(Exception):
    """
    Formatted 'FileNotFound Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'FileNotFound Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FInterruptedError(Exception):
    """
    Formatted 'Interrupted Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Interrupted Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FIsADirectoryError(Exception):
    """
    Formatted 'IsADirectory Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'IsADirectory Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FNotADirectoryError(Exception):
    """
    Formatted 'NotADirectory Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'NotADirectory Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FPermissionError(Exception):
    """
    Formatted 'Permission Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Permission Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FProcessLookupError(Exception):
    """
    Formatted 'Process Lookup Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Process Lookup Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FTimeoutError(Exception):
    """
    Formatted 'Timeout Error' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Timeout Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

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

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUserWarning(Exception):
    """
    Formatted 'User Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'User Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FDeprecationWarning(Exception):
    """
    Formatted 'Deprecation Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Deprecation Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FPendingDeprecationWarning(Exception):
    """
    Formatted 'Pending Deprecation Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Pending Deprecation Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FSyntaxWarning(Exception):
    """
    Formatted 'Syntax Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Syntax Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FRuntimeWarning(Exception):
    """
    Formatted 'Runtime Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Runtime Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FFutureWarning(Exception):
    """
    Formatted 'Future Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Future Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FImportWarning(Exception):
    """
    Formatted 'Import Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Import Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FUnicodeWarning(Exception):
    """
    Formatted 'Unicode Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Unicode Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FEncodingWarning(Exception):
    """
    Formatted 'Encoding Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Encoding Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FBytesWarning(Exception):
    """
    Formatted 'Bytes Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Bytes Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)


class FResourceWarning(Exception):
    """
    Formatted 'Resource Warning' with additional exception message options.
    """
    __slots__ = 'message_args'
    __module__ = 'builtins'

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Resource Warning' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

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

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'Custom Exception' with additional exception message options.

        FCustomException is used to add custom exception classes to the message.

        An exception class is required to use this option.

        Args:
            message_args (dict):
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- custom_type (custom_type):\\
            \t\t\\- The custom exception type.
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

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

    def __init__(self, message_args: dict, tb_limit: Optional[int] = None, caller_override: Optional[dict] = None) -> None:
        """
        Formatted 'General Error' with additional exception message options.

        Args:
            message_args (dict):\\
            \t\\- Dictionary will create a formatted exception message.\\
            tb_limit (int, Optional):\\
            \t\\- Set the traceback limit index at the most recent call.\\
            \t\\-  Defaults to None.\\
            caller_override (dict, Optional):\\
            \t\\- Change the traceback output.\\
            \t\\- Defaults to None.

        Arg Keys:
            message_args Keys:\\
            \t\\- main_message (str):\\
            \t\t\\- The main exception message.\\
            \t\\- expected_result (Union[str, list], Optional):\\
            \t\t\\- The expected result.\\
            \t\\- returned_result (Union[str, list], Optional):\\
            \t\t\\- The returned result.\\
            \t\\- suggested_resolution (Union[str, list], Optional):\\
            \t\t\\- A suggested resolution.\\
            \t\\- original_exception (any, Optional):\\
            \t\t\\- The original exception.

            caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.
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
                                                                         tb_limit=tb_limit,
                                                                         caller_override=caller_override))

            # Sets the Exception output used for printing the exception message.
            Exception.__init__(self, self._formatted_exception)
