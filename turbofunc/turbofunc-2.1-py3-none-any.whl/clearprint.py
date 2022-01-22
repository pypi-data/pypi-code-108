import os, sys
from enum import Enum

class StringStatus(Enum):
    SUCCESS = True
    CANT_GET_COLUMNS = False
    STRING_TOO_BIG = None

def clear_length(string):
    try:
        size = os.get_terminal_size().columns
    except OSError:
        return -1
    if size - len(string) < 0:
        return 0
    return size - len(string)

def string_plus_clear(string, status=False):
    """
    Returns the string plus the amount of spaces necessary to clear the line without breaking.
    Helpful in combination with escape codes such as \\r.
    No effect to the string if we can't count the terminal width (e.g. not a TTY).
    No effect to the string if the string is longer than the terminal width.
    If status is set to True, it will return a tuple in the format of:
        (string, status)
    where string is the finalised string and status is an item of the StringStatus enum.
    """
    try:
        size = os.get_terminal_size().columns
    except OSError:
        ret = (string, StringStatus.CANT_GET_COLUMNS) if status else string
    else:
        le = len(string)
        if le > size:
            ret = (string, StringStatus.STRING_TOO_BIG) if status else string
        else:
            fin = string + " " * (size - le)
            ret = (fin, StringStatus.SUCCESS) if status else fin
    return ret

def clear_print(*args, function=print):
    our_args = []
    for string in args:
        our_args.append(string_plus_clear(string))
    function(*our_args)
