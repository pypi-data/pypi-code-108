#! /usr/bin/python
# -*- coding: utf-8 -*-

from collections.abc import Iterable


__all__ = [
    'flatten',
]


def flatten(structured_list: 'Iterable', ignore_types=(str, bytes)):
    for item in structured_list:
        if isinstance(item, Iterable) and not isinstance(item, ignore_types):
            yield from flatten(item)
        else:
            yield item
