"""Tests for mylogging package. Usually runs from IDE, where configured via conftest."""
import sys
from pathlib import Path

import warnings
from io import StringIO

# mylogging is used in mypythontools, so need to be imported separately, not in setup_tests()
sys.path.insert(0, Path(__file__).parents[1].as_posix())
import mylogging

from help_file import warn_to_be_filtered
from conftest import get_stdout_and_stderr, setup_tests

setup_tests()

# pylint: disable=missing-function-docstring


def test_filter_once():
    mylogging.my_warnings.filter_once()
    assert get_stdout_and_stderr(warnings.warn, ["Just once"]), "filtered, but should not"
    assert not get_stdout_and_stderr(warnings.warn, ["Just once"]), "not filtered, but should"
    mylogging.my_warnings.reset_filter_once()
    assert get_stdout_and_stderr(warnings.warn, ["Just once"]), "filtered, but should not"
    assert get_stdout_and_stderr(warnings.warn, ["Just once"]), "filtered, but should not"


def test_filter_always():

    ignored_warnings = ["mean of empty slice"]

    # Sometimes only message does not work, then ignore it with class and warning type
    ignored_warnings_class_type = [
        ("TestError", FutureWarning),
    ]

    with warnings.catch_warnings(record=True) as warned:
        warn_to_be_filtered()

    assert warned, "Filter but should not"

    mylogging.my_warnings.filter_always(ignored_warnings, ignored_warnings_class_type)

    with warnings.catch_warnings(record=True) as warned:
        warn_to_be_filtered()

    assert not warned, "Doesn't filter"

    mylogging.my_warnings.reset_filter_always()

    with warnings.catch_warnings(record=True) as warned:
        warn_to_be_filtered()

    assert warned, "Filter but should not - not restarted."


if __name__ == "__main__":
    pass

    # test_filter_once()
    # test_filter_always()
