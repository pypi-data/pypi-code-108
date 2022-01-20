#!/usr/bin/env python
# coding: utf-8

from inspect import getsource as src


__all__ = [
    "srcMe",
]


def srcMe(function):
    return src(function)