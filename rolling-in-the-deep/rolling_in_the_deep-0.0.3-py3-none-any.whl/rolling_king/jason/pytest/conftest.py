#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import pytest

# in or below the directory where conftest.py is located

# 若加上scope，则代码在某scope范围内，该fixture被调用多次的情况下，仅执行一次。创建一个share_fixture_func object实例。
# Fixtures are created when first requested by a test, and are destroyed based on their scope
@pytest.fixture(scope="module")
def share_fixture_func():
    print("This is shared fixture")


# Pytest only caches one instance of a fixture at a time, which means that when using a parametrized fixture, pytest may invoke a fixture more than once in the given scope.