"""Tests for mylogging package. Usually runs from IDE, where configured via conftest."""
import sys
from pathlib import Path

# mylogging is used in mypythontools, so need to be imported separately, not in setup_tests()
sys.path.insert(0, Path(__file__).parents[1].as_posix())
import mylogging

from help_file import warn_outside, traceback_outside
from conftest import setup_tests

setup_tests()

# pylint: disable=missing-function-docstring


def display_logs(output: str):
    """If want to display check of logs (not tested).
    Also log images from readme and example log are generated here.

    Args:
        output (str, optional): "console" or "example.log". Defaults to "console".
    """
    mylogging.config.colorize = "auto"

    if output == "console":
        mylogging.config.output = "console"

    if output == "example":
        try:
            Path("example.log").unlink()  # from 3.8
        except FileNotFoundError:
            pass
        mylogging.config.output = "example.log"

    warn_outside("I am interesting warning.")

    mylogging.print("I am just printed.")

    traceback_outside("No zero.")

    mylogging.critical("This is critical", caption="You can use captions")


if __name__ == "__main__":
    display_logs(output="console")
    display_logs(output="example")
