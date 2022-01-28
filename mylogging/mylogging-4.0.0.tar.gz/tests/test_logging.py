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


def test_logs_to_file():

    log_path = Path("tests/utils/delete.log")
    log_path.unlink()
    mylogging.config.level = "WARNING"
    mylogging.config.output = log_path

    def check_log():
        with open(log_path, "r") as log:
            log_content = log.read()

        # Clear content before next run
        # To generate example log comment it out
        open(log_path, "w").close()

        if log_content:
            return True
        else:
            return False

    mylogging.info("Message")
    assert not check_log()  # Level filter not working

    mylogging.config.level = "INFO"
    mylogging.config.filter = "once"

    mylogging.info("Message")
    assert check_log()  # Level filter not working

    mylogging.info("Message")
    assert not check_log()  # Filter once not working

    mylogging.config.filter = "always"

    try:
        print(10 / 0)
    except ZeroDivisionError:
        mylogging.traceback("No zero.")

    assert check_log(), "Traceback not working"

    for i in [info_outside, warn_outside, traceback_outside]:
        i("Message")
        assert check_log(), "Function outside not working"


def test_logs_to_console():

    mylogging.config.filter = "ignore"

    assert not get_stdout_and_stderr(mylogging.warn, ["Dummy"]), "Printed, but should not."

    try:
        print(10 / 0)
    except ZeroDivisionError:
        assert not get_stdout_and_stderr(mylogging.traceback, ["No zero."]), "Printed, but should not"

    mylogging.config.filter = "once"

    assert get_stdout_and_stderr(mylogging.warn, ["Hello unique"]), "Not printed, but should."
    assert not get_stdout_and_stderr(mylogging.warn, ["Hello unique"]), "Printed, but should not."

    mylogging.config.filter = "always"

    assert get_stdout_and_stderr(mylogging.warn, ["Dummy"]), "Not printed, but should."
    assert get_stdout_and_stderr(mylogging.warn, ["Dummy"]), "Not printed, but should."

    # Test outer file
    mylogging.config.filter = "once"

    assert get_stdout_and_stderr(info_outside, ["Info outside"]), "Outside info not printed, but should"
    assert not get_stdout_and_stderr(info_outside, ["Info outside"]), "Outside printed, but should not"


def warn_mode():
    mylogging.config.console_log_or_warn = "warn"

    with warnings.catch_warnings(record=True) as warned:

        warn_outside("Warn outside")
        traceback_outside("Traceback outside")

        assert len(warned) == 2, "Warn from other file not working"


def test_log_levels():

    # Logging to file is already tested, because level filtering occur before division console or file

    all__levels_warnings_functions = [
        mylogging.critical,
        mylogging.error,
        mylogging.warn,
        mylogging.info,
        mylogging.debug,
    ]

    message_number_should_pass = 1

    for i in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:

        mylogging.config.level = i  # type: ignore
        logs_list = []

        for j in all__levels_warnings_functions:
            output = get_stdout_and_stderr(j, ["Message"])
            if output:
                logs_list.append("Message")
        assert len(logs_list) == message_number_should_pass, "Logger level not working properly"

        message_number_should_pass = message_number_should_pass + 1


def test_stream():
    stream = StringIO()
    mylogging.config.stream = stream
    mylogging.warn("Another warning")
    assert stream.getvalue()


def test_blacklist():

    mylogging.config.blacklist = ["Test blacklist one"]

    assert not get_stdout_and_stderr(mylogging.warn, ["Test blacklist one"]), "Should be blacklisted"
    assert get_stdout_and_stderr(mylogging.warn, ["Test not blacklisted"]), "Should not be blacklisted"


# def test_config():
#     # TODO
#     # Test color and debug
#     pass


if __name__ == "__main__":
    pass
    # test_logs_to_file()
    # test_logs_to_console()
    # test_log_levels()
    # warn_mode()
    # test_blacklist()
    # test_log_levels()
