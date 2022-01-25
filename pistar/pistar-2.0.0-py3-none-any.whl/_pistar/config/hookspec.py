from typing import TYPE_CHECKING, Optional

from pluggy import HookspecMarker

if TYPE_CHECKING:
    from _pistar.config import Config
    from _pistar.main import Session
    from _pistar.utilities.testcase.case import TestCase

hookspec = HookspecMarker("pistar")


@hookspec
def pistar_add_option(config: "Config") -> None:
    """
    the function is used to register the command and arguments
    """
    ...


@hookspec
def pistar_config(config: "Config"):
    """
    the function is used to get the pluginmanager from config, and register the plugin's hook.
    """
    ...


@hookspec
def pistar_main(config: "Config"):
    """
    the function is the entry of the execution.
    """
    ...


@hookspec
def pistar_collection(session: "Session"):
    """
    the function is used to collect the testcases, conditions.
    """
    ...


@hookspec
def pistar_modify_case(case: "TestCase"):
    ...


@hookspec
def pistar_collect_finish(session: "Session"):
    """
    the function is used to collect the testcases, conditions.
    """
    ...


@hookspec
def pistar_run_loop(session: "Session"):
    """
    the function is the entry of executing the cases
    """
    ...


@hookspec
def pistar_run_procedure(case: "TestCase", next_case: Optional["TestCase"]):
    ...


@hookspec
def pistar_run_log_begin(case: "TestCase"):
    ...


@hookspec
def pistar_run_log_end(case: "TestCase"):
    ...
