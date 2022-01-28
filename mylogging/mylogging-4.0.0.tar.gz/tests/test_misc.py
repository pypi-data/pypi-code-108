"""Tests for mylogging package. Usually runs from IDE, where configured via conftest."""
import sys
from pathlib import Path

import warnings
from io import StringIO

# mylogging is used in mypythontools, so need to be imported separately, not in setup_tests()
sys.path.insert(0, Path(__file__).parents[1].as_posix())
import mylogging

from help_file import info_outside, warn_outside, traceback_outside, warn_to_be_filtered
from conftest import get_stdout_and_stderr, setup_tests, logs_stream

setup_tests()

# pylint: disable=missing-function-docstring


def test_redirect_to_list():

    logs_list = []
    warnings_list = []

    redirect = mylogging.misc.redirect_logs_and_warnings(logs_list, warnings_list)
    assert get_stdout_and_stderr(warnings.warn, ["A warning."]), "No warn, but should"
    assert get_stdout_and_stderr(warnings.warn, ["A warning."]), "No warn, but should"
    assert warnings_list, "warning was not redirected to list"

    assert get_stdout_and_stderr(mylogging.warn, ["A warning."]), "No log, but should"
    assert logs_list, "logs was not redirected to list"

    redirect.close_redirect()

    assert get_stdout_and_stderr(mylogging.misc.log_and_warn_from_lists, [logs_list, warnings_list])

    # Now original warnings and logs are silenced and should be restored after close_redirect()
    redirect_silent = mylogging.misc.redirect_logs_and_warnings(
        logs_list, warnings_list, keep_logs_and_warnings=False
    )

    assert not get_stdout_and_stderr(warnings.warn, ["A warning."]), "Warn, but should not"
    assert not get_stdout_and_stderr(mylogging.warn, ["A warning."]), "Log, but should not"

    redirect_silent.close_redirect()

    assert get_stdout_and_stderr(warnings.warn, ["A warning."]), "No warn, but should"
    assert get_stdout_and_stderr(mylogging.warn, ["A warning."]), "No log, but should"


if __name__ == "__main__":
    pass

    # test_redirect_to_list()
