"""Terminal reporter module"""

from typing import Any, Dict, List, Optional, Tuple

import pytest
from _pytest._io import TerminalWriter
from _pytest.config import Config
from _pytest.reports import TestReport
from _pytest.terminal import TerminalReporter

COLORMAP = {
    "passed": {"green": True, "bold": True},
    "failed": {"red": True, "bold": True},
    "blocked": {"blue": True, "bold": True},
    "skipped": {"yellow": True, "bold": True},
    "xfailed": {"yellow": True, "bold": True},
    "xpassed": {"yellow": True, "bold": True}
}


class PrettyTerminalReporter:
    """
    Terminal reporter class used for prettifying terminal output (also used for synchronization of xdist-worker nodes).

    :param config: The pytest config object
    """

    def __init__(self, config: Config):
        """Constructor"""
        self.config = config
        self.terminal_reporter: TerminalReporter = config.pluginmanager.getplugin("terminalreporter")
        self.terminal_reporter.showfspath = False

    def pytest_runtest_logreport(self, report: TestReport):
        """
        Process the test report.

        :param report: The report object to be processed
        """
        if not getattr(self.config.option, "pretty", False) or report.when == "teardown":
            return

        user_properties = dict(report.user_properties)
        worker_node_suffix = ""
        if getattr(report, "node", None):
            worker_node_suffix = " --> " + report.node.gateway.id

        title = report.nodeid.split("[", 1)[0].strip() + worker_node_suffix

        if report.when == "setup":
            if (getattr(self.config.option, "numprocesses", 0) or 0) < 2:
                self._print_docstring_and_params(title, user_properties)

            if not report.skipped:
                return

        if (getattr(self.config.option, "numprocesses", 0) or 0) > 1:
            self._print_docstring_and_params(title, user_properties)

        terminal_writer: TerminalWriter = self.config.get_terminal_writer()
        fill = terminal_writer.fullwidth - terminal_writer.width_of_current_line - 1
        if getattr(report, "blocked", False):
            outcome = "blocked"
        elif hasattr(report, "wasxfail") and report.outcome == "skipped":
            outcome = "xfailed"
        elif hasattr(report, "wasxfail") and report.outcome == "passed":
            outcome = "xpassed"
        else:
            outcome = report.outcome

        self.terminal_reporter.write_sep("-", bold=True)
        self.terminal_reporter.write_line(outcome.upper().rjust(fill), **COLORMAP.get(outcome, {}))

    @pytest.hookimpl()
    def pytest_report_teststatus(self, report: TestReport) -> Optional[Tuple[str, str, str]]:
        """
        Return result-category, shortletter and verbose word for status reporting.
        In our case, the shortletter shall always be empty.

        :param report: The report object whose status is to be returned
        """
        if not getattr(self.config.option, "pretty", False):
            return None

        outcome: str = report.outcome
        if report.when in ("collect", "setup", "teardown"):
            if hasattr(report, "wasxfail") and report.skipped:
                outcome = "xfailed"
            elif hasattr(report, "wasxfail") and report.passed:
                outcome = "xpassed"
            elif outcome == "failed":
                outcome = "error"
            elif getattr(report, "blocked", False):  # Establish compatibility to pytest-adaptavist
                outcome = "blocked"
            elif not report.skipped:
                outcome = ""
        return outcome, "", ""

    def _print_docstring_and_params(self, title: str, user_properties: Dict[str, Any]):
        """Print docstring and parameters of a test case."""
        self.terminal_reporter.line("")
        self.terminal_reporter.write_sep("-", title, bold=True)
        doc_splitted: List[str] = (user_properties.get("docstr") or "").split("\n")
        leading_spaces = 0
        for line in doc_splitted:
            if line:  # Ignore leading empty lines
                leading_spaces = len(line) - len(line.lstrip())
                break
        for i, line in enumerate(doc_splitted):
            doc_splitted[i] = line[leading_spaces:]
        user_properties["docstr"] = "\n".join(doc_splitted)
        self.terminal_reporter.write_line(user_properties["docstr"])

        # Print parameters
        for parameter, value in user_properties.get("params", {}).items():
            self.terminal_reporter.write_line(f"Parameterization: {parameter} = {value}")
