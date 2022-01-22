#!/usr/bin/env python3
# coding: utf-8

from collections import OrderedDict


def flatten(tup):
    if isinstance(tup, tuple) and len(tup) == 1:
        return tup[0]
    return tup


def unflatten(obj):
    if isinstance(obj, tuple):
        return obj
    return obj,


def impose_order(dic, order):
    items = []
    for k in order:
        items.append((k, dic.get(k)))
    remained = set(dic) - set(order)
    for k in remained:
        items.append((k, dic[k]))
    return OrderedDict(items)


def human_lang_join(phrases: list, conj='and', punct=',', sep=' '):
    if not phrases:
        return ''
    if len(phrases) == 1:
        return phrases[0]
    parts = [s + punct for s in phrases[:-2]]
    parts.extend([phrases[-2], conj, phrases[-1]])
    return sep.join(parts)


class ColumnAlias:
    __slots__ = ['column', 'name']

    def __init__(self, column):
        self.column = column

    def __set_name__(self, _, name: str):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self.column.label(self.name)
        return getattr(instance, self.column.key)
