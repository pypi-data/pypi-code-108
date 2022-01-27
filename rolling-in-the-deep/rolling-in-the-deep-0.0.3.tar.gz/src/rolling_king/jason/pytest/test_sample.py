#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# pytest will run all files of the form test_*.py or *_test.py in the current directory and its subdirectories.

import pytest


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5


def f():
    raise SystemExit(1)


def test_mytest():
    with pytest.raises(SystemExit):
        f()

# The -q/--quiet flag keeps the output brief in this and following examples.
