from cytoolz.curried import curry, assoc

from genomoncology.parse import DocType
from . import comparators


RETAIN = "__RETAIN__"


def is_keep(obj):
    return obj.get(RETAIN, False) or DocType.HEADER.is_a(obj)


@curry
def or_(filter_1, filter_2, obj):
    return filter_1(obj) or filter_2(obj)


@curry
def or_not2_(filter_1, filter_2, obj):
    return filter_1(obj) or not filter_2(obj)


def glom_include(glom_path: str, cmp_str: str, cmp_value: str):
    glom_comparator = get_glom_comparator(glom_path, cmp_str, cmp_value)
    return or_(is_keep, glom_comparator)


def glom_exclude(glom_path: str, cmp_str: str, cmp_value: str):
    glom_comparator = get_glom_comparator(glom_path, cmp_str, cmp_value)
    return or_not2_(is_keep, glom_comparator)


def get_glom_comparator(glom_path: str, cmp_str: str, cmp_value: str):
    cmp_str = cmp_str.upper()
    cmp_set = comparators.COMPARE_LOOKUP.get(cmp_str, None)

    if cmp_set:
        return comparators.compare(glom_path, cmp_set, cmp_value)

    if cmp_str in "IN":
        cmp_value = load_data_set(cmp_value)
        return comparators.compare_in(glom_path, cmp_value)

    if cmp_str in ("HAS", "CONTAINS"):
        return comparators.compare_contains(glom_path, cmp_value)


def load_data_set(literal_str_or_file_path: str) -> set:
    if literal_str_or_file_path.startswith("@"):
        file_path = literal_str_or_file_path[1:]
        return set([line.strip() for line in open(file_path).readlines()])
    else:
        return set(
            [string.strip() for string in literal_str_or_file_path.split(",")]
        )


@curry
def mark_retain(glom_path: str, cmp_str: str, cmp_value: str, obj):
    glom_comparator = get_glom_comparator(glom_path, cmp_str, cmp_value)
    if glom_comparator(obj):
        obj = assoc(obj, RETAIN, True)
    return obj
