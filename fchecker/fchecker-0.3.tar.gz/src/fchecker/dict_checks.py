from typing import Optional, Union
import inspect
from pathlib import Path

# Own modules
from fexception import FCustomException, FAttributeError
from .type_checks import type_check
from .common import InvalidKeyError


class KeyCheck():
    """
    An advanced dictionary key checker that offers two different check options.

    Raises a cleanly formatted reason if the key validation is unsuccessful.

    No return output.

    Options:\\
    \t\\- contains_keys():\\
    \t\t\\- Checks if some required keys exist in the dictionary.\\
    \t\\- all_keys():\\
    \t\t\\- Checks if all required keys exist in the dictionary.

    Args:
        values (dict):\\
        \t\\- A dictionary that needs the keys validated.
        \t\t\\- A template can be used with the reverse option enabled.
    """
    def __init__(self, values: dict) -> None:
        type_check(
            values,
            dict,
            # Caller override two calls before.
            caller_override={
                'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                'line': inspect.currentframe().f_back.f_back.f_lineno,
                'tb_remove': 'dict_checks'}
        )

        self._values = values

    def contains_keys(self, required_keys: Union[str, list], reverse_output: Optional[bool] = False) -> None:
        """
        Checks if some required keys exist in the dictionary.

        Args:
            required_keys (Union[str, list])):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or list of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            FAttributeError (fexception):\\
            \t\\- No key(s) were sent.
            FAttributeError (fexception):\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            FAttributeError (fexception):\\
            \t\\- The required key list contains duplicate keys. All keys must be unique.\\
            InvalidKeyError (fexception):\\
            \t\\- The dictionary key (\'{no_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        """
        self._required_keys = required_keys
        self._all_key_check = False
        self.reverse_output = reverse_output
        try:
            self._key_validation()
        except (InvalidKeyError, FAttributeError):
            raise

    def all_keys(self, required_keys: Union[str, list], reverse_output: Optional[bool] = False) -> None:
        """
        Checks if all required keys exist in the dictionary

        Args:
            required_keys (Union[str, list])):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or list of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            FAttributeError (fexception):\\
            \t\\- No key(s) were sent.
            FAttributeError (fexception):\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            FAttributeError (fexception):\\
            \t\\- The required key list contains duplicate keys. All keys must be unique.\\
            InvalidKeyError (fexception):\\
            \t\\- The dictionary key (\'{no_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        """
        self._required_keys = required_keys
        self._all_key_check = True
        self.reverse_output = reverse_output
        try:
            self._key_validation()
        except (InvalidKeyError, FAttributeError):
            raise

    def _key_validation(self) -> None:
        """
        Performs the key validation.

        Raises:
            FAttributeError (fexception):\\
            \t\\- No key(s) were sent.
            FAttributeError (fexception):\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            FAttributeError (fexception):\\
            \t\\- The required key list contains duplicate keys. All keys must be unique.\\
            InvalidKeyError (fexception):\\
            \t\\- The dictionary key (\'{no_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        """

        type_check(
            self._required_keys,
            [str, list],
            # Caller override two calls before.
            caller_override={
                'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                'line': inspect.currentframe().f_back.f_back.f_lineno,
                'tb_remove': 'dict_checks'}
        )

        # Loops through to find any keys that do not match.
        dict_keys = list(self._values.keys())

        # Reverses key results for flipped reverse checks.
        if self.reverse_output:
            expected_key_result = dict_keys
            required_key_result = self._required_keys
        else:
            expected_key_result = self._required_keys
            required_key_result = dict_keys

        # Checks for that required keys are sent.
        if not self._required_keys:
            # Formats the output based on the check option.
            if self._all_key_check:
                expected_result = f'  - Expected Key(s) = {expected_key_result}'
            else:
                expected_result = f'  - Expected Match Option Key(s) = {dict_keys}'

            exc_args = {
                'main_message': 'No key(s) were sent.',
                'expected_result': expected_result,
                'returned_result': None
            }
            # Caller override two calls before.
            caller_override = {
                'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                'line': inspect.currentframe().f_back.f_back.f_lineno,
                'tb_remove': 'validation_director'
            }
            raise FAttributeError(exc_args, tb_limit=None, caller_override=caller_override)

        # Checks for 1:1 input when using the all_keys option.
        if self._all_key_check:
            mismatched_input: bool
            if isinstance(self._required_keys, list):
                if len(dict_keys) != len(self._required_keys):
                    mismatched_input = True
                else:
                    mismatched_input = False
            else:
                if len(self._values) > 1:
                    mismatched_input = True
                else:
                    mismatched_input = False

            if mismatched_input is True:
                exc_args = {
                    'main_message': 'The input keys have inconsistent value and requirement keys.',
                    'expected_result': f'Required Key(s) = {expected_key_result}',
                    'returned_result': f'Failed Key(s) = {required_key_result}'
                }
                # Caller override two calls before.
                caller_override = {
                    'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                    'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                    'line': inspect.currentframe().f_back.f_back.f_lineno,
                    'tb_remove': 'validation_director'
                }
                raise FAttributeError(exc_args, tb_limit=None, caller_override=caller_override)
        else:
            mismatched_input = False

        # Checks for duplicate values.
        if isinstance(self._required_keys, list):
            if len(self._required_keys) != len(set(self._required_keys)):
                exc_args = {
                    'main_message': 'The required key list contains duplicate keys. All keys must be unique.',
                    'returned_result': f'Required Key(s) = {self._required_keys}'
                }
                # Caller override two calls before.
                caller_override = {
                    'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                    'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                    'line': inspect.currentframe().f_back.f_back.f_lineno,
                    'tb_remove': 'validation_director'
                }
                raise FAttributeError(exc_args, tb_limit=None, caller_override=caller_override)

        if isinstance(dict_keys, list):
            if len(dict_keys) != len(set(dict_keys)):
                exc_args = {
                    'main_message': 'The expected key list contains duplicate keys. All keys must be unique.',
                    'returned_result': f'Expected Key(s) = {dict_keys}'
                }
                # Caller override two calls before.
                caller_override = {
                    'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                    'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                    'line': inspect.currentframe().f_back.f_back.f_lineno,
                    'tb_remove': 'validation_director'
                }
                raise FAttributeError(exc_args, None, caller_override)

        # Sets the keys in reverse order so the no-match is the last entry checked
        # but the first no-match in the list of keys.
        sorted_dict_keys = sorted(dict_keys, reverse=True)

        if isinstance(self._required_keys, list):
            for required_key in self._required_keys:
                # Checks if the validation requires all the required keys
                # to match all sorted_dict_keys or the required keys to match
                # some of the sorted_dict_keys.
                if self._all_key_check:
                    for dict_key in sorted_dict_keys:
                        # Checks for exact match.
                        if required_key == dict_key:
                            no_matching_key = None
                            break
                        else:
                            no_matching_key = required_key
                else:
                    if required_key in sorted_dict_keys:
                        no_matching_key = None
                    else:
                        no_matching_key = required_key
                # If a match is not found on the first required
                # key check the loop will exit and return the no-matched key.
                if no_matching_key:
                    break
        else:
            # Variable name swap for easier loop reading.
            required_key: str = self._required_keys
            for dict_key in sorted_dict_keys:
                if required_key == dict_key:
                    # Checks for exact match.
                    no_matching_key = None
                    break
                else:
                    no_matching_key = required_key

        # Checks if a no matching key exists, to output the error
        if no_matching_key:
            # Formats the output based on the check option.
            if self._all_key_check:
                main_message = (f'The dictionary key (\'{no_matching_key}\') '
                                'does not exist in the expected required key(s).\n')
                expected_result = f'Expected Key(s) = {expected_key_result}'
                returned_result = f'Failed Key(s) = {required_key_result}'
            else:
                main_message = (f'The dictionary key (\'{no_matching_key}\') '
                                'does not match any expected match option key(s).\n')
                expected_result = f'Match Option Key(s) = {expected_key_result}'
                returned_result = f'Failed Key(s) = {required_key_result}'

            exc_args = {
                'main_message': main_message,
                'custom_type': InvalidKeyError,
                'expected_result': expected_result,
                'returned_result': returned_result
            }
            # Caller override two calls before.
            caller_override = {
                'module': Path(inspect.currentframe().f_back.f_back.f_code.co_filename).stem,
                'name': inspect.currentframe().f_back.f_back.f_code.co_name,
                'line': inspect.currentframe().f_back.f_back.f_lineno,
                'tb_remove': 'validation_director'
            }
            raise FCustomException(exc_args, tb_limit=None, caller_override=caller_override)
