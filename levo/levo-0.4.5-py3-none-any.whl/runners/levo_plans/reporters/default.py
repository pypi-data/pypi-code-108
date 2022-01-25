import time
from typing import Dict, List, Optional, Union

import click
from levo_commons import events
from levo_commons.models import (
    AfterTestExecutionPayload,
    AfterTestSuiteExecutionPayload,
    BeforeTestExecutionPayload,
    BeforeTestSuiteExecutionPayload,
    Status,
    TestResult,
)
from levo_commons.utils import format_exception
from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table

from ....handlers import EventHandler
from ....logger import get_logger
from ...utils import get_color_for_status
from ..context import ExecutionContext, TestSuiteExecutionContext

log = get_logger(__name__)
console = Console()


def handle_before_execution(
    context: ExecutionContext,
    event: events.BeforeTestCaseExecution[BeforeTestExecutionPayload],
) -> None:
    # Test case id here isn't ideal so we need to find what's better.
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    if event.payload.recursion_level > 0:
        # This value is not `None` - the value is set in runtime before this line
        suite_context.operations_processed += 1  # type: ignore


def handle_after_execution(
    context: ExecutionContext,
    event: events.AfterTestCaseExecution[AfterTestExecutionPayload],
) -> None:
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    suite_context.operations_processed += 1
    suite_context.results.append(event.payload.result)

    if event.payload.status == Status.error:
        suite_context.errored_count += 1
    elif event.payload.status == Status.failure:
        suite_context.failed_count += 1
    else:
        suite_context.success_count += 1


def handle_before_suite_execution(
    context: ExecutionContext,
    event: events.BeforeTestSuiteExecution[BeforeTestSuiteExecutionPayload],
) -> None:
    # Add a context at the test suite level and record the item id.
    context.test_suite_id_to_context[
        event.payload.test_suite_id
    ] = TestSuiteExecutionContext(name=event.payload.name)


def handle_after_suite_execution(
    context: ExecutionContext,
    event: events.AfterTestSuiteExecution[AfterTestSuiteExecutionPayload],
) -> None:
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    if suite_context.errored_count > 0:
        suite_context.status = Status.error
    elif suite_context.failed_count > 0:
        suite_context.status = Status.failure
    else:
        suite_context.status = Status.success

    context.success_count += suite_context.success_count
    context.errored_count += suite_context.errored_count
    context.failed_count += suite_context.failed_count
    context.skipped_count += suite_context.skipped_count

    # TODO: Display the progress of the overall test and also the suite testing status.
    if suite_context.errored_count > 0:
        display_errors(context, suite_context)


def handle_finished(
    context: ExecutionContext, running_time: Optional[float] = None
) -> str:
    """Show the outcome of the whole testing session."""
    suite_to_status_summary: Dict[str, Dict[Union[str, Status], int]] = {}
    has_errors = False
    has_failures = False
    for suite_id, suite_context in context.test_suite_id_to_context.items():
        suite_to_status_summary[suite_context.name] = {
            "total": (
                suite_context.success_count
                + suite_context.failed_count
                + suite_context.errored_count
            ),
            "skipped": suite_context.skipped_count,
            Status.success: suite_context.success_count,
            Status.error: suite_context.errored_count,
            Status.failure: suite_context.failed_count,
        }

        if not has_errors and suite_context.errored_count > 0:
            has_errors = True
        if not has_failures and suite_context.failed_count > 0:
            has_failures = True

    if has_errors and not context.show_errors_tracebacks:
        console.print(
            "[red]Add this option to your command line parameters to see full tracebacks: --show-errors-tracebacks"
        )
    console.rule("Summary", style="grey30")
    console.print(get_suites_summary_section(suite_to_status_summary))
    console.rule(get_run_summary(context, running_time), style="grey30")
    return (
        Status.error
        if has_errors
        else Status.failure
        if has_failures
        else Status.success
    )


def get_run_summary(
    context: ExecutionContext, running_time: Optional[float] = None
) -> str:
    parts = get_run_summary_message_parts(context)
    if not parts:
        message = "Empty test plan."
    elif running_time:
        message = f'{", ".join(parts)} in {running_time:.2f}s'
    else:
        message = f'{", ".join(parts)}'
    return message


def get_run_summary_message_parts(context: ExecutionContext) -> List[str]:
    parts = []
    passed = context.success_count
    if passed:
        parts.append(
            f"{passed} tests passed" if passed != 1 else f"{passed} test passed"
        )
    failed = context.failed_count
    if failed:
        parts.append(
            f"{failed} tests failed" if failed != 1 else f"{failed} test failed"
        )
    errored = context.errored_count
    if errored:
        parts.append(
            f"{errored} tests errored" if errored != 1 else f"{errored} test errored"
        )
    skipped = context.skipped_count
    if skipped:
        parts.append(
            f"{skipped} tests skipped" if skipped != 1 else f"{skipped} test skipped"
        )
    skipped_suites = context.skipped_suite_count
    if skipped_suites:
        parts.append(
            f"{skipped_suites} suites skipped"
            if skipped_suites != 1
            else f"{skipped_suites} suite skipped"
        )
    return parts


def get_section_name(title: str, separator: str = "=", extra: str = "") -> str:
    """Print section name with separators in terminal with the given title nicely centered."""
    extra = extra if not extra else f" [{extra}]"
    return f" {title}{extra} ".center(80, separator)


def get_suites_summary_section(
    suite_to_status_summary: Dict[str, Dict[Union[str, Status], int]]
) -> str:
    """Format and print statistic collected by :obj:`models.TestResult`."""
    if suite_to_status_summary:
        return get_all_suites_summary(suite_to_status_summary)
    else:
        return "No test suites were run."


def get_all_suites_summary(
    suite_to_status_summary: Dict[str, Dict[Union[str, Status], int]]
) -> str:
    results_table = Table(
        "Test Suite",
        "Passed",
        "Failed",
        "Errored",
        "Skipped",
        expand=True,
        box=box.ROUNDED,
        header_style=None,
    )
    for suite_name, results in suite_to_status_summary.items():
        if not results.get("total"):
            continue
        passed = str(results.get(Status.success, 0))
        failed = str(results.get(Status.failure, 0))
        errored = str(results.get(Status.error, 0))
        skipped = str(results.get("skipped", 0))
        results_table.add_row(suite_name, passed, failed, errored, skipped)

    suite_console = Console()
    with suite_console.capture() as capture:
        suite_console.print(results_table)
    return capture.get()


def display_errors(
    context: ExecutionContext, suite_context: TestSuiteExecutionContext
) -> None:
    """Display all errors in the test run."""
    displayed_errors_section = False
    for result in suite_context.results:
        if not result.has_errors:
            continue
        if not displayed_errors_section:
            displayed_errors_section = True
            console.rule(f"[red]Errors [{suite_context.name}]", style="grey30")
        display_single_error(context, result)


def display_single_error(context: ExecutionContext, result: TestResult) -> None:
    for error in result.errors:
        _display_error(context, error)


def display_generic_errors(context: ExecutionContext, errors: List[Exception]) -> None:
    for error in errors:
        _display_error(context, error)


def _display_error(
    context: ExecutionContext,
    error: Exception,
) -> None:
    console.print(format_exception(error, context.show_errors_tracebacks), style="red")


def handle_skipped(context, event):
    if event.test_suite_id:
        # If there is a test case id, we know it's a test case that got skipped.
        if event.test_case_id:
            suite_context = context.test_suite_id_to_context[event.test_suite_id]
            suite_context.skipped_count += 1
        else:
            # If it's the test suite that's skipped, we need to report that too.
            context.skipped_suite_count += 1


def handle_internal_error(
    context: ExecutionContext, event: events.InternalError
) -> None:
    console.print(event.message, style="red")
    if event.exception:
        if context.show_errors_tracebacks:
            message = event.exception_with_traceback
        else:
            message = event.exception
        console.print(f"[red]Error: {message}\n")
    if event.is_terminal:
        raise click.Abort


class TestPlanConsoleOutputHandler(EventHandler):
    start_time: float = time.monotonic()

    def __init__(self):
        self._live_console: Optional[Live] = None
        self._table: Optional[Table] = None
        self._test_spinner: Optional[Spinner] = None

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Choose and execute a proper handler for the given event."""
        if isinstance(event, events.Initialized):
            console.rule(
                f"[magenta]Test Plan: {event.payload.plan_name}", style="grey30"
            )
            self.start_time = event.start_time
            pass
        if isinstance(event, events.BeforeTestSuiteExecution):
            self._create_test_suite_table(event.payload.name)
            handle_before_suite_execution(context, event)
        if isinstance(event, events.AfterTestSuiteExecution):
            self._end_test_suite()
            handle_after_suite_execution(context, event)
        if isinstance(event, events.BeforeTestCaseExecution):
            self._add_test_case(event.payload.name)
            handle_before_execution(context, event)
        if isinstance(event, events.AfterTestCaseExecution):
            handle_after_execution(context, event)
            self._end_test_case(event.payload.status)
        if isinstance(event, events.BeforeTestStepExecution):
            pass
        if isinstance(event, events.AfterTestStepExecution):
            pass
        if isinstance(event, events.Skipped):
            handle_skipped(context, event)
        if isinstance(event, events.Finished):
            handle_finished(context, event.running_time)
        if isinstance(event, events.Interrupted):
            self._end_test_case("interrupted")
            self._end_test_suite()
            handle_finished(context, time.monotonic() - self.start_time)
        if isinstance(event, events.InternalError):
            handle_internal_error(context, event)

    def _create_test_suite_table(self, name: str):
        self._table = Table.grid(expand=True)
        self._table.add_column(ratio=7)
        self._table.add_column(ratio=3)
        panel = Panel(
            self._table,
            title=f"[deep_sky_blue1 i] Test Suite [{name}]",
            border_style="grey50",
        )
        self._live_console = Live(panel)
        self._live_console.start()

    def _add_test_case(self, name: str):
        if not self._table:
            self._create_test_suite_table("Unknown Test Suite")
        self._test_spinner = Spinner(name="line", text="RUNNING")
        self._table.add_row(name, self._test_spinner)  # type: ignore

    def _end_test_case(self, status: Union[Status, str]):
        if self._test_spinner:
            color = get_color_for_status(status)
            self._test_spinner.update(
                text=f"[{color}]{status.upper()}", style="black", speed=0
            )

    def _end_test_suite(self):
        if self._live_console and self._live_console.is_started:
            if self._table and self._table.row_count == 0:
                self._live_console.transient = True
            self._live_console.stop()
