"""
the pistar executor for python

modules provided as follow:
    base testcase class: _testcase.case.py
    test step decorator: _testcase.decorator.py
    test case exception: _testcase.exceptions.py
    action word self checker: action_word.checker
    action word self checker decorator: action_word.decorator.py
    action word exception handle: action_word.exceptions.py
    assert module: assertion.assert_that.py
    assert exception handle: assertion.exceptions.py
"""
from .testcase import BaseTestCase
from .testcase import teststep
from _pistar.utilities.testcase import control
from .condition import condition
