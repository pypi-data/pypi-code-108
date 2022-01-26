from collections import namedtuple
from inspect import getmembers, isroutine
from typing import Dict, Any, List


def to_identifier(s: str) -> str:
    """ Convert a string s into an valid identifier.
    :return: A str that can be used as a Python identifier.
    """
    s = 'n' + s if s and s[0].isdigit() else s
    return ''.join([c if c.isidentifier() or c.isdigit() else '_' for c in s])


def attributes2dict(obj: object) -> Dict[str, Any]:
    """ Convert an object with attributes into a dictionary. The attributes can be properties or public attributes.
    :param obj: The object to extract its attributes.
    :return: A dictionary with the name of the attribute and its value.
    """
    members = getmembers(obj, lambda member: not (isroutine(member)))
    return {att[0]: att[1] for att in members if not att[0].startswith('_')}


def attributes2list(obj: object) -> List[str]:
    """ Convert an object with attributes into a list of strings. The attributes can be properties or public
     attributes.
    :param obj: The object to extract its attributes.
    :return: A list with the name of attributes.
    """
    members = getmembers(obj, lambda member: not (isroutine(member)))
    return [att[0] for att in members if not att[0].startswith('_')]


def dict2obj(d: dict) -> object:
    """ Convert a dictionary in a Python object.
    :param d: The dictionary.
    :return: A Python object of type "Row" with the name of the keys as attributes and the values of the dictionary as
    the values of that attributes. If the dictionary has a key that is not a valid Python id, then, this method tries
    to convert it to an valid identifier replacing the incorrect characters by a _, or adding a _ at the start if
    the identifier starts with a number.
    """
    keys = [to_identifier(key) for key in d.keys()]
    return namedtuple('Row', keys)(*d.values()) if d else None


def dict2list(d: dict) -> List[Any]:
    """ Convert the values or a dictionary into a list.
    :param d: The dictionary.
    :return: A list with the values of that dictionary.
    """
    return [v for v in d.values()]


def dict_keys2list(d: dict) -> List[Any]:
    """ Convert the values or a dictionary into a list.
    :param d: The dictionary.
    :return: A list with the values of that dictionary.
    """
    return [v for v in d.keys()]
