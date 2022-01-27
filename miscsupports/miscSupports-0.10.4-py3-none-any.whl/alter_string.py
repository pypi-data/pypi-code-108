from .Errors import TupleTypeError, InvalidBool

from distutils.util import strtobool
import re


def tuple_convert(str_of_tuple, convert_type=float, must_be_string=False):
    """Convert string representations of a tuple of floats back a tuple of convert_type"""
    if isinstance(str_of_tuple, str):
        split_values = str_of_tuple.split(",")
        return tuple([convert_type(value.replace("(", "").replace(")", "")) for value in split_values])
    elif isinstance(str_of_tuple, (tuple, list)) and not must_be_string:
        return str_of_tuple
    else:
        raise TupleTypeError(str_of_tuple)


def string_to_bool(value):
    """
    This will convert a string to a bool if it is a str, return the bool if it was a bool, and raise a TypeError
    otherwise
    """

    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return bool(strtobool(value))
    else:
        raise InvalidBool(value)


def sep_num(number, space=True):
    """
    Creates a string representation of a number with separators each thousand. If space is True, then it uses spaces for
    the separator otherwise it will use commas

    Note
    ----
    Source: https://stackoverflow.com/questions/16670125/python-format-string-thousand-separator-with-spaces

    :param number: A number
    :type number: int | float

    :param space: Separates numbers with spaces if True, else with commas
    :type space: bool

    :return: string representation with space separation
    :rtype: str
    """
    if space:
        return '{:,}'.format(number).replace(',', ' ')
    else:
        return '{:,}'.format(number)


def string_contains_numbers(string: str) -> bool:
    """
    Check to see if the string has a digit within it

    Source: https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
    """
    return any(char.isdigit() for char in string)


def simplify_string(string_to_simplify: str) -> str:
    """
    Strip a string of all non alphanumeric characters, white space, and capital letters
    """
    string_to_simplify = string_to_simplify.replace("&", "and")
    return re.sub(r"[\W]", "", string_to_simplify).lower()
