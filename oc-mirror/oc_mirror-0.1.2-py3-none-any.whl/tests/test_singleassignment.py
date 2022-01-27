#!/usr/bin/env python

"""Manifest tests."""

import logging

from _pytest.logging import LogCaptureFixture

from oc_mirror.singleassignment import SingleAssignment


def test_get_set(caplog: LogCaptureFixture):
    """Tests double assignment."""

    caplog.clear()
    caplog.set_level(logging.DEBUG)

    name = "myvarname"
    value1 = "first value"
    single_assignment = SingleAssignment(name)
    single_assignment.set(value1)
    assert single_assignment.get() == value1
    assert "Overriding previously value of" not in caplog.text

    value2 = "second value"
    single_assignment.set(value2)
    assert "Overriding previously value of" in caplog.text
    assert name in caplog.text

    caplog.clear()

    assert single_assignment.get() == value2
    assert "Overriding previously value of" not in caplog.text


def test_accessor_methods(caplog: LogCaptureFixture):
    """Tests double assignment."""

    caplog.clear()
    caplog.set_level(logging.DEBUG)

    name = "myvarname"
    value1 = "first value"
    single_assignment = SingleAssignment(name)
    single_assignment.myvarname = value1
    assert single_assignment.myvarname == value1
    assert "Overriding previously value of" not in caplog.text

    value2 = "second value"
    single_assignment.myvarname = value2
    assert "Overriding previously value of" in caplog.text
    assert name in caplog.text

    caplog.clear()

    assert single_assignment.myvarname == value2
    assert "Overriding previously value of" not in caplog.text
