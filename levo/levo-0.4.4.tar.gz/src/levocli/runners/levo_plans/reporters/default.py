import time
from typing import Dict, List, Optional, Union, cast

import click
from levo_commons import events
from levo_commons.models import (
    AfterTestExecutionPayload,
    AfterTestSuiteExecutionPayload,
    BeforeTestExecutionPayload,
    BeforeTestSuiteExecutionPayload,
    FinishedPayload,
    Status,
    TestResult,
)
from levo_commons.utils import format_exception

from ....handlers import EventHandler
from ....logger import get_logger
from ...utils import get_color_for_status
from ..context import ExecutionContext, TestSuiteExecutionContext

log = get_logger(__name__)


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
        click.secho(
            "Add this option to your command line parameters to see full tracebacks: --show-errors-tracebacks",
            fg="red",
        )
    click.echo(get_suites_summary_section(suite_to_status_summary))
    click.echo()
    click.echo(get_run_summary(context, running_time))
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
    return get_section_name(message)


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
    lines = [get_section_name("SUMMARY")]

    if suite_to_status_summary:
        lines.append(get_all_suites_summary(suite_to_status_summary))
    else:
        lines.append("No test suites were run.")

    return "\n".join(lines)


def get_all_suites_summary(
    suite_to_status_summary: Dict[str, Dict[Union[str, Status], int]]
) -> str:
    lines = []
    for suite_name, results in suite_to_status_summary.items():
        suite_result = get_test_suite_result_summary(suite_name, results)
        if suite_result:
            lines.append(suite_result)
    return "Tested the suites:\n" + "\n".join(lines)


def get_test_suite_result_summary(
    suite_name: str,
    results: Dict[Union[str, Status], int],
) -> Optional[str]:
    """Show results of single test suite execution."""
    success = results.get(Status.success, 0)
    total = results.get("total", 0)
    if not total:
        return None
    line = f"{suite_name}: {success} / {total} passed"
    failed = results.get(Status.failure, 0)
    if failed:
        line += f", {failed} failed"
    errored = results.get(Status.error, 0)
    if errored:
        line += f", {errored} errored"
    skipped = results.get("skipped", 0)
    if skipped:
        line += f", {skipped} skipped"
    return line


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
            click.echo(get_section_name("ERRORS", extra=suite_context.name))
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
    click.secho(format_exception(error, context.show_errors_tracebacks), fg="red")


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
    click.secho(event.message, fg="red")
    if event.exception:
        if context.show_errors_tracebacks:
            message = event.exception_with_traceback
        else:
            message = event.exception
        click.secho(f"Error: {message}\n", fg="red")
    if event.is_terminal:
        raise click.Abort


class TestPlanConsoleOutputHandler(EventHandler):
    start_time: float = time.monotonic()

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Choose and execute a proper handler for the given event."""
        if isinstance(event, events.Initialized):
            click.echo("Running test plan: {}".format(event.payload.plan_name))
            self.start_time = event.start_time
            pass
        if isinstance(event, events.BeforeTestSuiteExecution):
            click.echo(get_section_name("TEST SUITE", extra=event.payload.name))
            handle_before_suite_execution(context, event)
        if isinstance(event, events.AfterTestSuiteExecution):
            handle_after_suite_execution(context, event)
        if isinstance(event, events.BeforeTestCaseExecution):
            click.echo("Running the test case: {}".format(event.payload.name))
            handle_before_execution(context, event)
        if isinstance(event, events.AfterTestCaseExecution):
            handle_after_execution(context, event)
            click.secho(
                f"Finished the test case: {event.payload.name}, status: {event.payload.status.upper()}\n",
                fg=get_color_for_status(event.payload.status),
            )
        if isinstance(event, events.BeforeTestStepExecution):
            pass
        if isinstance(event, events.AfterTestStepExecution):
            pass
        if isinstance(event, events.Skipped):
            handle_skipped(context, event)
        if isinstance(event, events.Finished):
            status = handle_finished(context, event.running_time)
            click.secho(
                f"Finished running the test plan. status={status}",
                fg=get_color_for_status(status),
            )
        if isinstance(event, events.Interrupted):
            click.secho("Test plan run is interrupted.", fg="red")
            handle_finished(context, time.monotonic() - self.start_time)
        if isinstance(event, events.InternalError):
            handle_internal_error(context, event)
