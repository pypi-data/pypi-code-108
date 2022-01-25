from typing import Union
import inspect
from pathlib import Path

# Own modules
from fexception import FCustomException, FAttributeError, FTypeError
from .common import InputFailure


def type_check(value: any, required_type: Union[type, list],
               caller_override: dict = None, msg_override: str = None) -> None:
    """
    A simple type validation check. This function is designed to be widely used to check any values.

    Raises a cleanly formatted reason if the type validation is unsuccessful.

    No return output.

    Args:
        value (any):
        \t\\- Any value needing its type validated.\\
        required_type (Union[type, list]):
        \t\\- The required type the value should match.\\
        \t\\- Can be a single type or list of types.
        caller_override (dict, optional):
        \t\\- Change the traceback output.\\
        \t\\- Defaults to None.
        msg_override (str, optional):
        \t\\- Main top-level message override.\\
        \t\\= The expected and returned results will be the same.\\
        \t\\- Ideal for type checks for other importing files such as YAML.\\
        \t\\- Defaults to None.

    Arg Keys:
        caller_override Keys:\\
            \t\\- module (str):\\
            \t\t\\- The override module.\\
            \t\\- name (str):\\
            \t\t\\- The override name.\\
            \t\\- line (int):\\
            \t\t\\- The override line.\\
            \t\\- tb_remove (str):\\
            \t\t\\- The traceback module name that needing removed.

    Raises:
        FAttributeError (fexception):
        \t\\- The value \'{value}\' sent is not an accepted input.
        FAttributeError (fexception):
        \t\\- No type or list of types has been entered for type validation.
        FTypeError (fexception):
        \t\\- The value \'{value}\' is not in {required_type} format.
    """

    # If set, checks and sets the caller_override args or uses caller info.
    if caller_override:
        if not isinstance(caller_override, dict):
            raise InputFailure('dict format is the required input to set the caller override option.')
        if (
            'module' not in str(caller_override.keys())
            or 'name' not in str(caller_override.keys())
            or 'line' not in str(caller_override.keys())
            or 'tb_remove' not in str(caller_override.keys())
        ):
            exc_args = {
                'main_message': 'Incorrect caller_overide keys.',
                'custom_type': InputFailure,
                'expected_result': """Expected Key(s) = ['module', 'name', 'line', 'tb_remove']""",
                'returned_result': f'Failed Key(s) = {caller_override.keys()}'
            }
            caller_override = {
                'module': Path(inspect.currentframe().f_back.f_code.co_filename).stem,
                'name': inspect.currentframe().f_back.f_code.co_name,
                'line': inspect.currentframe().f_back.f_lineno,
                'tb_remove': 'type_checks'
            }
            raise FCustomException(exc_args, tb_limit=None, caller_override=caller_override)
        else:
            override_module = caller_override.get('module')
            override_name = caller_override.get('name')
            override_line = caller_override.get('line')
            override_tb_remove = caller_override.get('tb_remove')
    else:
        override_module = Path(inspect.currentframe().f_back.f_code.co_filename).stem
        override_name = inspect.currentframe().f_back.f_code.co_name
        override_line = inspect.currentframe().f_back.f_lineno
        override_tb_remove = 'type_checks'

    # Verifies a value is sent.
    if (
        value is None
        or value == ''
    ):
        exc_args = {
            'main_message': f'The value \'{value}\' sent is not an accepted input.',
            'expected_result': 'Any value other than None or an empty string',
            'returned_result': type(value)
        }
        # Caller override two calls before.
        caller_override = {
            'module': override_module,
            'name': override_name,
            'line': override_line,
            'tb_remove': override_tb_remove
        }
        raise FAttributeError(exc_args, None, caller_override)

    # Verifies a type or list is sent.
    if (
        not (isinstance(required_type, list) or isinstance(required_type, type))
    ):
        exc_args = {
            'main_message': 'No type or list of types has been entered for type validation.',
            'expected_result': 'type or list of types',
            'returned_result': type(required_type)
        }
        # Caller override two calls before.
        caller_override = {
            'module': override_module,
            'name': override_name,
            'line': override_line,
            'tb_remove': override_tb_remove
        }
        raise FAttributeError(exc_args, None, caller_override)

    # Checks if the required type option one type or multiple.
    if isinstance(required_type, list):
        for value_type in required_type:
            if isinstance(value, value_type):
                matching_type_flag = True
                break
            else:
                matching_type_flag = False
    else:
        if not isinstance(value, required_type):
            matching_type_flag = False
        else:
            matching_type_flag = True

    # Checks for no match.
    if matching_type_flag is False:
        # Sets message override if one is provided.
        if msg_override:
            main_message = msg_override
        else:
            main_message = f'The value \'{value}\' is not in {required_type} format.'

        exc_args = {
            'main_message': main_message,
            'expected_result': required_type,
            'returned_result': type(value)
        }
        # Caller override two calls before.
        caller_override = {
            'module': override_module,
            'name': override_name,
            'line': override_line,
            'tb_remove': override_tb_remove
        }
        raise FTypeError(exc_args, tb_limit=None, caller_override=caller_override)
