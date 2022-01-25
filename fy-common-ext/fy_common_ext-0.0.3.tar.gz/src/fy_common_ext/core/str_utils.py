#! /usr/bin/python
# -*- coding: utf-8 -*-

from typing import AnyStr

__all__ = [
    'remove_prefix', 'remove_suffix',
]


def remove_prefix(s: AnyStr, t: AnyStr):
    if s.startswith(t):
        return s[len(t):]
    return s


def remove_suffix(s: AnyStr, t: AnyStr):
    if not t:
        return s
    if s.endswith(t):
        return s[:-len(t)]
    return s
