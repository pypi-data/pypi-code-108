import inspect
from types import FrameType
from inspect import currentframe
from typing import cast, Union, Optional


def get_line_number() -> int:
    """Returns the calling function's line number."""
    cf = currentframe()
    return cf.f_back.f_lineno


def get_function_name() -> str:
    """Return the calling function's name."""
    return cast(FrameType, cast(FrameType, inspect.currentframe()).f_back).f_code.co_name


class InvalidKeyError(Exception):
    """
    Exception raised for an invalid dictionary key.

    Built in KeyErrors do not format cleanly.

    Attributes:
        error_message: The invalid key reason.
    """
    error_message: str

    def __ini__(self, error_message: str) -> None:
        self.error_message = error_message


class KeyCheck():
    """
    An advanced dictionary key checker that offers two different check options.

    Raises an exception if the key validation is unsuccessful. No return output.

    Options:\\
    \t\\- contains_keys():\\
    \t\t\\- Checks if some required keys exist in the dictionary.\\
    \t\\- all_keys():\\
    \t\t\\- Checks if all required keys exist in the dictionary.

    Args:
        values (dict): A dictionary that needs the keys validated.
        caller_module (str): The name of the caller module. Use '__name__'.
        caller_name (str): The name of the caller (func or method).
        caller_line (int): The calling function line.
    """
    def __init__(self, values: dict,
                 caller_module: str,
                 caller_name: str,
                 caller_line: int
                 ) -> None:
        self._values = values
        self._caller_module = caller_module
        self._caller_name = caller_name
        self._caller_line = caller_line

    def contains_keys(self, required_keys: Union[str, list], reverse_output: Optional[bool] = False) -> None:
        """
        Checks if some required keys exist in the dictionary.

        Args:
            self._required_keys (Union[str, list])):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or list of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            AttributeError:
            \t\\- The input keys have inconsistent value and requirement keys.
            AttributeError:
            \t\\- The expected key list contains duplicate keys. All keys must be unique.
            InvalidKeyError:
            \t\\- The dictionary key (\'{no_matching_key}\') does not exist in the expected required key(s).
            InvalidKeyError:
            \t\\- The dictionary key (\'{no_matching_key}\') does not match any expected match option key(s).
        """
        self._required_keys = required_keys
        self._all_key_check = False
        self.reverse_output = reverse_output
        self._key_validation()

    def all_keys(self, required_keys: Union[str, list], reverse_output: Optional[bool] = False) -> None:
        """
        Checks if all required keys exist in the dictionary

        Args:
            self._required_keys (Union[str, list])):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or list of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            AttributeError:\\
            \t\\- The input keys have inconsistent value and requirement keys.
            AttributeError:\\
            \t\\- The expected key list contains duplicate keys. All keys must be unique.
            InvalidKeyError:\\
            \t\\- The dictionary key (\'{no_matching_key}\') does not exist in the expected required key(s).
            InvalidKeyError:\\
            \t\\- The dictionary key (\'{no_matching_key}\') does not match any expected match option key(s).
        """
        self._required_keys = required_keys
        self._all_key_check = True
        self.reverse_output = reverse_output
        self._key_validation()

    def _key_validation(self) -> None:
        """
        Performs the key validation.

        Raises:
            AttributeError:\\
            \t\\- No key(s) were sent.
            AttributeError:\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            AttributeError:\\
            \t\\- The required key list contains duplicate keys. All keys must be unique.\\
            InvalidKeyError:\\
            \t\\- The dictionary key (\'{no_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        """
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
                expected_result = f'  - Expected Match Option Key(s) = {expected_key_result}'

            error_message = (
                f'No key(s) were sent.\n'
                + (('-' * 150) + '\n')
                + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                + (('-' * 150) + '\n')
                + 'Returned Result:\n'
                f'{expected_result}\n\n'
                'Returned Result:\n'
                f'  - None\n\n'
                + f'Trace Details:\n'
                f'  - Exception: AttributeError\n'
                f'  - Module: {self._caller_module}\n'
                f'  - Name: {self._caller_name}\n'
                f'  - Line: {self._caller_line}\n'
                + (('-' * 150) + '\n') * 2
            )
            raise AttributeError(error_message)

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
                error_message = (
                    f'The input keys have inconsistent value and requirement keys.\n'
                    + (('-' * 150) + '\n')
                    + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                    + (('-' * 150) + '\n')
                    + 'Expected Result:\n'
                    f'  - Required Key(s) = {expected_key_result}\n\n'
                    'Returned Result:\n'
                    f'  - Failed Key(s) = {required_key_result}\n\n'
                    + f'Trace Details:\n'
                    f'  - Exception: AttributeError\n'
                    f'  - Module: {self._caller_name}\n'
                    f'  - Name: {self._caller_name}\n'
                    f'  - Line: {self._caller_line}\n'
                    + (('-' * 150) + '\n') * 2
                )
                raise AttributeError(error_message)
        else:
            mismatched_input = False

        # Checks for duplicate values.
        if isinstance(self._required_keys, list):
            if len(self._required_keys) != len(set(self._required_keys)):
                error_message = (
                    f'The required key list contains duplicate keys. All keys must be unique.\n'
                    + (('-' * 150) + '\n')
                    + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                    + (('-' * 150) + '\n')
                    + 'Returned Result:\n'
                    f'  - Required Key(s) = {required_key_result}\n\n'
                    + f'Trace Details:\n'
                    f'  - Exception: AttributeError\n'
                    f'  - Module: {self._caller_module}\n'
                    f'  - Name: {self._caller_name}\n'
                    f'  - Line: {self._caller_line}\n'
                    + (('-' * 150) + '\n') * 2
                )
                raise AttributeError(error_message)

        if isinstance(dict_keys, list):
            if len(dict_keys) != len(set(dict_keys)):
                error_message = (
                    f'The expected key list contains duplicate keys. All keys must be unique.\n'
                    + (('-' * 150) + '\n')
                    + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                    + (('-' * 150) + '\n')
                    + 'Returned Result:\n'
                    f'  - Expected Key(s) = {expected_key_result}\n\n'
                    + f'Trace Details:\n'
                    f'  - Exception: AttributeError\n'
                    f'  - Module: {self._caller_module}\n'
                    f'  - Name: {self._caller_name}\n'
                    f'  - Line: {self._caller_line}\n'
                    + (('-' * 150) + '\n') * 2
                )
                raise AttributeError(error_message)

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
                expected_result = f'  - Expected Key(s) = {expected_key_result}'
                returned_result = f'  - Failed Key(s) = {required_key_result}'
            else:
                main_message = (f'The dictionary key (\'{no_matching_key}\') '
                                'does not match any expected match option key(s).\n')
                expected_result = f'  - Match Option Key(s) = {expected_key_result}'
                returned_result = f'  - Failed Key(s) = {required_key_result}'

            error_message = (
                f'{main_message}'
                + (('-' * 150) + '\n')
                + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                + (('-' * 150) + '\n')
                + 'Expected Result:\n'
                f'{expected_result}\n\n'
                'Returned Result:\n'
                f'{returned_result}\n\n'
                + f'Trace Details:\n'
                f'  - Exception: AttributeError\n'
                f'  - Module: {self._caller_module}\n'
                f'  - Name: {self._caller_name}\n'
                f'  - Line: {self._caller_line}\n'
                + (('-' * 150) + '\n') * 2
            )
            raise InvalidKeyError(error_message)
