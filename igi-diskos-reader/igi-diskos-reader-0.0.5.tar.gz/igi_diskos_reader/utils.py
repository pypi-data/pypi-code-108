from typing import Tuple


def split_on_last_occurrence(val: str, delim: str) -> Tuple[str, str]:
    """
    Split on the last instance of the delimiter, if the delimiter is not found
    then returns the input value and an empty string.
    """
    idx = val.rfind(delim)
    if idx == -1:
        return val, ''
    return val[:idx], val[idx+1:]


def is_a_suffix(x: str):
    """
    Can be used with split_on_last_occurrence() to predict whether the res[-1] is a suffix.
    """
    return x and x.isdecimal()


def get_all_subclasses(cls):
    all_subclasses = set()
    for subclass in cls.__subclasses__():
        all_subclasses.add(subclass)
        all_subclasses.update(get_all_subclasses(subclass))
    return all_subclasses
