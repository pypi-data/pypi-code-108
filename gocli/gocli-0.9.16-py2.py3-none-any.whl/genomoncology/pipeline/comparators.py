from glom import glom
from cytoolz.curried import curry
from genomoncology.parse.ensures import ensure_collection
from .converters import fint


@curry
def cmp(x, y):
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.
    """
    return (x > y) - (x < y)


def safe_lower(val):
    val = "|".join(map(str, ensure_collection(val)))
    return val.lower()


@curry
def compare_contains(glom_path, cmp_value, obj):
    # todo: need proper unit tests. currently only supports string contains
    # case insensitive: the string "Likely benign" does contain "Benign"
    obj_value = glom(obj, glom_path, default=None)

    if obj_value is not None:
        return safe_lower(cmp_value) in safe_lower(obj_value)


@curry
def compare_in(glom_path: str, s: set, obj):
    obj_value = glom(obj, glom_path, default=None)
    return s.intersection(ensure_collection(obj_value))


@curry
def compare(glom_path: str, cmp_set: set, cmp_value, obj):
    cmp_value = None if cmp_value == "." else cmp_value
    obj_value = glom(obj, glom_path, default=None)

    # todo: this isn't correct, using first item as representative
    # todo: switch to a loop and return True if ANY (?)
    if obj_value and isinstance(obj_value, (list,)):
        obj_value = obj_value[0]

    if isinstance(obj_value, (int, float)):
        cmp_value = fint(cmp_value)

    if None in {obj_value, cmp_value}:
        return obj_value is None and cmp_value is None
    else:
        return cmp(obj_value, cmp_value) in cmp_set


LT = {-1}
LTE = {-1, 0}
GT = {1}
GTE = {1, 0}
EQ = {0}
NE = {1, -1}

COMPARE_LOOKUP = {
    "<": LT,
    ">": GT,
    ">=": GTE,
    "<=": LTE,
    "==": EQ,
    "=": EQ,
    "!=": NE,
    "<>": NE,
    "LT": LT,
    "GT": GT,
    "GTE": GTE,
    "LTE": LTE,
    "EQ": EQ,
    "NE": NE,
}
