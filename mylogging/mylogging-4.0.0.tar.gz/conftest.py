"""Runs before every pytest test. Used automatically (at least at VS Code)."""


import warnings
from io import StringIO
from pathlib import Path
import sys
from typing import Callable, Any

import pytest

# mylogging is used in mypythontools, so need to be imported separately, not in setup_tests()
sys.path.insert(0, Path(__file__).parent.as_posix())


import mylogging
from mypythontools.tests import setup_tests

setup_tests()

# from mypythontools import cicd  # pylint: disable=wrong-import-order

# cicd.tests.setup_tests()

logs_stream = StringIO()


@pytest.fixture(autouse=True)
def setup_tests_fixture():
    """Reset some settings before tests start."""
    setup_tests()


def setup_tests():
    """Setup test usually runs from fixture."""

    warnings.filterwarnings("always")

    showwarning_backup = warnings.showwarning

    def custom_warn(message, category, filename, lineno, file=None, line=None):
        print(message)
        showwarning_backup(message, category, filename, lineno, file=None, line=None)

    # Monkeypatch so warnings also print to stdout so it's testable including the filters
    warnings.showwarning = custom_warn

    mylogging.config.level = "INFO"
    mylogging.config.console_log_or_warn = "log"
    mylogging.config.stream = logs_stream
    mylogging.config.output = "console"
    mylogging.config.filter = "always"
    logs_stream.truncate(0)


def get_stdout_and_stderr(func: Callable, args: list[Any] = None, kwargs: dict[str, Any] = None):
    """Check stdout, stdin and logs outputs and if detect some message, return all the logged content.
    It's reset at the end.

    Args:
        func (Callable): Function, that should log something.
        args (list[Any], optional): Args used in function. Defaults to None.
        kwargs (dict[str, Any], optional): [description]. Defaults to None.

    Returns:
        str: Logged message.
    """
    if not args:
        args = []
    if not kwargs:
        kwargs = {}

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    my_stdout = StringIO()
    my_stderr = StringIO()
    sys.stdout = my_stdout
    sys.stderr = my_stderr

    func(*args, **kwargs)

    output = my_stdout.getvalue() + my_stderr.getvalue() + logs_stream.getvalue()

    logs_stream.truncate(0)

    my_stdout.close()
    my_stderr.close()

    sys.stdout = old_stdout
    sys.stderr = old_stderr

    return output
