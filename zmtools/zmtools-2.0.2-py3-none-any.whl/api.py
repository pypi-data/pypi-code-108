import logging
import os
import platform
import re
import subprocess
import sys
from contextlib import contextmanager
from typing import Optional

from click import getchar

LOGGER = logging.getLogger(__name__)

IS_WINDOWS = platform.system() == "Windows"


@contextmanager
def working_directory(path: str):
    """Context manager to run all code under it in a certain directory

    Args:
        path (str): The path to switch to for the scope of the context manager
    """
    owd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(owd)


def init_logging(level: int =logging.INFO, filename: str = None, filemode: str = None) -> None:
    """Set a logging.basicConfig's format to '%(asctime)s [%(levelname)s] %(message)s' and set a certain level

    Args:
        level (int, optional): Logging level. Defaults to logging.INFO.
        filename (str, optional): File to log to. Defaults to None.
        filemode (str, optional): File mode to use. Defaults to None.
    """
    logging.basicConfig(filename=filename, filemode=filemode,
                        format='%(asctime)s [%(levelname)s] %(message)s', force=True)
    logging.getLogger().setLevel(level)


def capitalize_each_word(s: str, delimiter: str) -> str:
    """Capitalize each word seperated by a delimiter

    Args:
        s (str): The string to capitalize each word in
        delimiter (str): The delimeter words are separated by

    Returns:
        str: The modified string
    """
    return delimiter.join([w.capitalize() for w in s.split(delimiter)])


def strip_each_line(s: str) -> str:
    """Strips each line of a string

    Args:
        s (str): The string to strip each line of

    Returns:
        str: The modified string
    """
    return "\n".join([line.strip() for line in s])


def y_to_continue(prompt: str = "Enter y to continue:", requires_enter: bool = False) -> bool:
    """Return True if the user enters "y" else False

    Args:
        prompt (str, optional): The prompt to display to the user. Defaults to "Enter y to continue:".
        requires_enter (bool, optional): If this prompt requires the user to hit enter. Defaults to False.

    Returns:
        bool: If the user entered True
    """
    print(prompt + " ", end="", flush=True)
    if not requires_enter:
        y = getchar().lower() == "y"
        print()
    else:
        y = input().lower() == "y"
    return y


def input_multiline(warn: Optional[bool] = None, default: str = "") -> str:
    """Get multiline user input until EOF is reached

    Args:
        warn (str, optional): Warn the user with this message if the input is empty. Defaults to None.
        default (str, optional): Default input to use if no input is read. Defaults to "".

    Returns:
        string: The string inputted
    """
    s = sys.stdin.read()
    s = s.strip()
    if not s.endswith("\n") or not s:
        print()
    if not s:
        if warn is not None:
            LOGGER.warning(warn)
        s = default
    return s


def exception_to_dict(error: Exception) -> dict:
    """Takes in an exception and outputs its details, excluding the stacktrace, to a dict

    Args:
        error (Exception): The exception to serialize

    Returns:
        dict: The serialized exception
    """
    return {"type": str(type(error).__name__), "message": str(error)}


def truncate(s: str, length: int = 25, elipsis: str = True) -> str:
    """Truncates a string. You can specify the length and to exclude the ending elipsis

    Args:
        s (str): The input string
        length (int, optional): The max length of the truncated string. Defaults to 25.
        elipsis (bool, optional): If an elipsis should be appended to the truncated string, if it is actually truncated. Defaults to True.

    Returns:
        str: The truncated string
    """
    if elipsis:
        test_length = length + 3
    else:
        test_length = length
    if len(s) > test_length:
        truncated = s[:length].strip()
        return truncated + "..." if elipsis else truncated
    else:
        return s


@contextmanager
def dummy_context_manager(*args, **kwargs) -> None:
    """Useless context manager"""
    yield


def get_dpkg_package_version(package_name: str) -> str:
    """Get the version of an installed package.

    Args:
        package_name (str): The package name

    Returns:
        str: The version of the package
    """
    return re.findall(r"(?<=Version: ).+", subprocess.check_output(["dpkg", "-s", package_name]).decode())[0]


def picker(items: list, item_name: str="choice") -> str:
    """A picker for a list of items

    Args:
        items (list[any]): The list to pick from
        item_name (str, optional): A friendly name of what an item is. Defaults to "choice".

    Raises:
        ValueError: If the user enters invalid input

    Returns:
        any: The picked item
    """
    if not items:
        raise TypeError(f"Not a single {item_name} to pick from")
    elif len(items) == 1:
        return items[0]
    for index, item in enumerate(items, start=1):
        print(f"{index}) {item}")
    try:
        choice_index = int(input(f"Select a {item_name}: "))
    except ValueError:
        raise ValueError("Invalid input")
    return items[choice_index - 1]


def read_text(file_location: str, not_exists_ok: bool = False) -> str:
    """Read text from a file

    Args:
        file_location (str): Location of file
        not_exists_ok (bool, optional): If True and file does not exist, will return "" instead of throw an exception. Defaults to False.

    Returns:
        str: The text in the file, stripped of whitepace at the end
    """
    try:
        with open(file_location, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        if not not_exists_ok:
            raise
        else:
            return ""


def write_text(file_location: str, content: str) -> None:
    """Write text to a file

    Args:
        file_location (str): Location of file
        content (str): The content to write to the file
    """
    with open(file_location, "w") as f:
        f.write(content)
