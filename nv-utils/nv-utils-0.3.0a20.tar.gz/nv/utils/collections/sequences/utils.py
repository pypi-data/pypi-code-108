from collections.abc import Iterable


from nv.utils.parsers import BASIC_SEQUENCES


__ALL__ = ['flatten', ]


def flatten(iterable, ignore_types=BASIC_SEQUENCES):
    for i in iterable:
        if isinstance(i, Iterable) and not isinstance(i, ignore_types):
            yield from flatten(i)
        else:
            yield i
