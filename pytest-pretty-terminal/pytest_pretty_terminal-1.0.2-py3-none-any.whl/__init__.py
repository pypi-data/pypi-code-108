"""pytest plugin for generating prettier terminal output"""

import logging
import shutil
from importlib.metadata import PackageNotFoundError, version

import pytest
from _pytest._io import TerminalWriter
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.logging import _LiveLoggingStreamHandler, get_log_level_for_setting
from _pytest.python import Function
from _pytest.reports import CollectReport, TestReport
from _pytest.runner import CallInfo

from ._pretty_terminal_reporter import PrettyTerminalReporter

try:
    __version__ = version("pytest_pretty_terminal")
except PackageNotFoundError:
    # package is not installed - e.g. pulled and run locally
    __version__ = "0.0.0"


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: Function, call: CallInfo):  # pylint: disable=unused-argument
    """
    Collect used parameters and test's docstring.
    This is called at setup, run/call and teardown of test items.

    :param item: A Function item
    :param call: The CallInfo for the phase
    """
    outcome: CollectReport = yield
    report: TestReport = outcome.get_result()
    if hasattr(item, 'callspec'):
        report.user_properties.append(("params", item.callspec.params))
    report.user_properties.append(("docstr", item.obj.__doc__))


def enable_terminal_report(config: Config):
    """
    Enable pretty terminal reporting and configure built-in plugins correspondingly.

    :param config: The pytest config object
    """

    # Register our own terminal reporter.
    pretty_terminal_reporter = PrettyTerminalReporter(config)
    config.pluginmanager.register(pretty_terminal_reporter, "pretty_terminal_reporter")

    capture_manager = config.pluginmanager.getplugin("capturemanager")

    # Capturing needs to be turned off. Otherwise additional output might mess up our terminal.
    if getattr(config.option, "capture") != "no":
        setattr(config.option, "capture", "no")
        capture_manager.stop_global_capturing()
        setattr(capture_manager, "_method", getattr(config.option, "capture"))
        capture_manager.start_global_capturing()

    # The original terminal reporter needs some overwrites because we want to suppress output made during log start and finish.
    # However, we need to reregister the terminalreporter to get the overwrites in place.
    terminal_reporter = config.pluginmanager.getplugin("terminalreporter")
    config.pluginmanager.unregister(terminal_reporter)
    terminal_reporter.pytest_runtest_logstart = lambda nodeid, location: None
    terminal_reporter.pytest_runtest_logfinish = lambda nodeid: None
    config.pluginmanager.register(terminal_reporter, "terminalreporter")

    # Enable logging and set the loglevel. Without this, live logging would be disabled.
    # Still we want to respect to settings made via config.
    logging_plugin = config.pluginmanager.getplugin("logging-plugin")
    logging_plugin.log_cli_handler = _LiveLoggingStreamHandler(terminal_reporter, capture_manager)
    logging_plugin.log_cli_level = get_log_level_for_setting(config, "log_cli_level", "log_level") or logging.INFO


def patch_terminal_size(config: Config):
    """
    Patch the terminal size and try to fix the layout issue related to Jenkins console.

    :param config: The pytest config object
    """
    terminal_reporter = config.pluginmanager.getplugin("pretty_terminal_reporter")
    terminal_writer: TerminalWriter = config.get_terminal_writer()

    if not terminal_reporter or not terminal_writer:
        return

    try:
        # Calculate terminal size from screen dimension (e.g. 1920 -> 192)
        import tkinter  # pylint: disable=import-outside-toplevel
        default_width = min(192, int((tkinter.Tk().winfo_screenwidth() + 9) / 10))
        default_height = int((tkinter.Tk().winfo_screenheight() + 19) / 20)
    except Exception:  # pylint: disable=broad-except
        # Tradeoff
        default_width = 152
        default_height = 24

    width, _ = shutil.get_terminal_size((default_width, default_height))
    terminal_writer.fullwidth = width


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config):
    """
    Perform initial configuration.

    :param config: The pytest config object
    """
    if (
        not hasattr(config, "workerinput")
        and getattr(config.option, "pretty", False)
    ):
        enable_terminal_report(config)
    patch_terminal_size(config)


def pytest_addoption(parser: Parser):
    """
    Add options to control the plugin.

    :param parser: Parser for command line arguments and ini-file values
    """
    group = parser.getgroup("pretty-terminal")
    group.addoption("--pretty", action="store_true", dest="pretty", default=False,
                    help="Make pytest terminal output more readable (default: False)")
