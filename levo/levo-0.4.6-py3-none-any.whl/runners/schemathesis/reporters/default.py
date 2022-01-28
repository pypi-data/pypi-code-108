import base64
import os
import platform
import shutil
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

import click
from hypothesis import settings
from levo_commons import events
from levo_commons.models import AssertionResult, Interaction, SerializedError
from schemathesis._compat import metadata

from ....handlers import EventHandler
from ....logger import get_logger
from ..context import EndpointExecutionContext, ExecutionContext
from ..models import (
    AfterExecutionPayload,
    BeforeExecutionPayload,
    FinishedPayload,
    InitializedPayload,
    Status,
)

DISABLE_SCHEMA_VALIDATION_MESSAGE = (
    "\nYou can disable input schema validation with --validate-schema=false "
    "command-line option\nIn this case, the test cannot guarantee proper"
    " behavior during the test run"
)

log = get_logger(__name__)


def _get_endpoint_name(method, relative_path):
    return f"{method} {relative_path}"


def get_terminal_width() -> int:
    # Some CI/CD providers (e.g. CircleCI) return a (0, 0) terminal size so provide a default
    return shutil.get_terminal_size((80, 24)).columns


def get_unique_failures(assertions: List[AssertionResult]) -> List[AssertionResult]:
    """Return only unique checks that should be displayed in the output."""
    seen: Set[Tuple[str, Optional[str]]] = set()
    unique_assertions = []
    for check in reversed(assertions):
        # There could be assertions that didn't fail as well
        if check.status == Status.failure:
            key = _get_failure_key(check)
            if (check.name, key) not in seen:
                unique_assertions.append(check)
                seen.add((check.name, key))
    return unique_assertions


def _get_failure_key(check: AssertionResult) -> Optional[str]:
    return check.name


def display_section_name(
    title: str, separator: str = "=", extra: str = "", **kwargs: Any
) -> None:
    """Print section name with separators in terminal with the given title nicely centered."""
    extra = extra if not extra else f" [{extra}]"
    message = f" {title}{extra} ".center(get_terminal_width(), separator)
    kwargs.setdefault("bold", True)
    click.secho(message, **kwargs)


def display_subsection(result: AssertionResult, color: Optional[str] = "red") -> None:
    display_section_name(result.name, fg=color)


def get_percentage(position: int, length: int) -> str:
    """Format completion percentage in square brackets."""
    percentage_message = f"{position * 100 // length}%".rjust(4)
    return f"[{percentage_message}]"


def display_execution_result(
    context: ExecutionContext,
    event: events.AfterTestCaseExecution[AfterExecutionPayload],
) -> None:
    """Display an appropriate symbol for the given event's execution result."""
    symbol, color = {
        Status.success: (".", "green"),
        Status.failure: ("F", "red"),
        Status.error: ("E", "red"),
    }[event.payload.status]
    context.current_line_length += len(symbol)
    click.secho(symbol, nl=False, fg=color)


def display_percentage(
    context: ExecutionContext,
    endpoint_context: EndpointExecutionContext,
) -> None:
    """Add the current progress in % to the right side of the current line."""
    operations_count = cast(
        int, context.operations_count
    )  # is already initialized via `Initialized` event
    current_percentage = get_percentage(
        endpoint_context.operations_processed, operations_count
    )
    styled = click.style(current_percentage, fg="cyan")
    # Total length of the message, so it will fill to the right border of the terminal.
    # Padding is already taken into account in `context.current_line_length`
    length = max(
        get_terminal_width()
        - context.current_line_length
        + len(styled)
        - len(current_percentage),
        1,
    )
    template = f"{{:>{length}}}"
    click.echo(template.format(styled))


def display_summary(event: events.Finished[FinishedPayload]) -> None:
    message, color = get_summary_output(event)
    display_section_name(message, fg=color)


def get_summary_message_parts(event: events.Finished[FinishedPayload]) -> List[str]:
    passed = 0
    failed = 0
    errored = 0
    if event.payload.total:
        for check_name, results in event.payload.total.items():
            success = results.get(Status.success, 0)
            total = results.get("total", 0)
            error = results.get(Status.error, 0)

            # If there were any failures under a check, mark that check as a failure.
            if total > success:
                failed += 1
                # check_to_status[check_name] = Status.failure
            else:
                passed += 1

            if error:
                errored += 1

    parts = []
    if passed:
        parts.append(f"{passed} passed")
    if failed:
        parts.append(f"{failed} failed")
    if errored:
        parts.append(f"{errored} errored")
    return parts


def get_summary_output(event: events.Finished[FinishedPayload]) -> Tuple[str, str]:
    parts = get_summary_message_parts(event)
    if not parts:
        message = "Empty test suite"
        color = "yellow"
    else:
        message = f'{", ".join(parts)} in {event.running_time:.2f}s'
        if event.payload.has_failures or event.payload.has_errors:
            color = "red"
        else:
            color = "green"
    return message, color


def display_hypothesis_output(hypothesis_output: List[str]) -> None:
    """Show falsifying examples from Hypothesis output if there are any."""
    if hypothesis_output:
        display_section_name("HYPOTHESIS OUTPUT")
        output = "\n".join(hypothesis_output)
        click.secho(output, fg="red")


def display_errors(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> None:
    """Display all errors in the test run."""
    if not event.payload.has_errors:
        return

    display_section_name("ERRORS")
    for endpoint_context in context.endpoint_to_context.values():
        if endpoint_context.errored_count > 0:
            display_single_error(context, endpoint_context)
    if event.payload.generic_errors:
        display_generic_errors(context, event.payload.generic_errors)
    if not context.show_errors_tracebacks:
        click.secho(
            "Add this option to your command line parameters to see full tracebacks: --show-errors-tracebacks",
            fg="red",
        )


def display_single_error(
    context: ExecutionContext, endpoint_context: EndpointExecutionContext
) -> None:
    # Get the first error from the list of errors.
    errors = endpoint_context.errors
    if not errors:
        return

    display_subsection(errors[0])
    # TODO: Fix this
    # _display_error(context, errors[0], result.seed)


def display_generic_errors(
    context: ExecutionContext, errors: List[SerializedError]
) -> None:
    for error in errors:
        display_section_name(error.title or "Generic error", "_", fg="red")
        _display_error(context, error)


def _display_error(
    context: ExecutionContext,
    error: SerializedError,
    seed: Optional[int] = None,
) -> None:
    if context.show_errors_tracebacks:
        message = error.exception_with_traceback
    else:
        message = error.exception
    if error.exception.startswith("InvalidSchema") and context.validate_schema:
        message += DISABLE_SCHEMA_VALIDATION_MESSAGE + "\n"
    click.secho(message, fg="red")
    # if error.example is not None:
    #     display_example(context, error.example, seed=seed)


def display_failures(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> None:
    """Display all failures in the test run."""
    if not event.payload.has_failures:
        return

    failed_assertions = []
    for endpoint_context in context.endpoint_to_context.values():
        for (
            assertions
        ) in endpoint_context.data_generation_method_to_assertions.values():
            failed_assertions.extend(
                [
                    assertion
                    for assertion in assertions
                    if assertion.status == Status.failure
                ]
            )
    if not failed_assertions:
        return

    display_section_name("FAILURES")
    for endpoint_context in context.endpoint_to_context.values():
        display_failures_for_single_test(context, endpoint_context)


def display_failures_for_single_test(
    context: ExecutionContext,
    endpoint_context: EndpointExecutionContext,
) -> None:
    """Gets a failure for a single method / path."""
    failed_assertions = []
    for assertions in endpoint_context.data_generation_method_to_assertions.values():
        for assertion in assertions:
            if assertion.status == Status.failure:
                failed_assertions.append(assertion)
    if not failed_assertions:
        return
    failed_assertions = get_unique_failures(failed_assertions)
    if not failed_assertions:
        raise ValueError("No failures found")
    assertion = failed_assertions[0]
    display_subsection(assertion)

    for idx, assertion in enumerate(failed_assertions, 1):
        message: Optional[str]
        if assertion.message:
            message = f"{idx}. {assertion.message}"
        else:
            message = None
        interaction = assertion.interactions[0] if assertion.interactions else None
        if interaction:
            display_example(context, interaction, message)
            click.echo("\n")


def reduce_schema_error(message: str) -> str:
    """Reduce the error schema output."""
    end_of_message_index = message.find(":", message.find("Failed validating"))
    if end_of_message_index != -1:
        return message[:end_of_message_index]
    return message


def display_example(
    context: ExecutionContext,
    interaction: Interaction,
    message: Optional[str] = None,
    seed: Optional[int] = None,
) -> None:
    if message is not None:
        if not context.verbosity:
            message = reduce_schema_error(message)
        click.secho(message, fg="red")
        click.echo()

    if interaction.response is not None and interaction.response.body is not None:
        payload = (
            base64.b64decode(interaction.response.body)
            .decode(interaction.response.encoding or "utf8", errors="replace")
            .rstrip()
        )
        click.secho(f"----------\nResponse payload: `{payload}`\n", fg="red")

    # if context.code_sample_style == CodeSampleStyle.python:
    #     click.secho(
    #         f"Run this Python code to reproduce this failure: \n\n    {interaction.requests_code}\n",
    #         fg="red",
    #     )

    click.secho(
        f"Run this cURL command to reproduce this failure: \n    {interaction.request.as_curl_command()}\n",
        fg="red",
    )

    if seed is not None:
        click.secho(
            f"Or add this option to your command line parameters: --hypothesis-seed={seed}",
            fg="red",
        )


def display_statistic(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> None:
    """Format and print statistic collected by :obj:`TestResult`."""
    display_section_name("SUMMARY")
    click.echo()
    total = event.payload.total
    if event.payload.is_empty or not total:
        click.secho("No checks were performed.", bold=True)

    if total:
        display_checks_statistics(total)

    if context.cassette_file_name or context.junit_xml_file:
        click.echo()

    if context.cassette_file_name:
        category = click.style("Network log", bold=True)
        click.secho(f"{category}: {context.cassette_file_name}")

    if context.junit_xml_file:
        category = click.style("JUnit XML file", bold=True)
        click.secho(f"{category}: {context.junit_xml_file}")


def display_checks_statistics(total: Dict[str, Dict[Union[str, Status], int]]) -> None:
    padding = 20
    col1_len = max(map(len, total.keys())) + padding
    col2_len = (
        len(str(max(total.values(), key=lambda v: v["total"])["total"])) * 2 + padding
    )
    col3_len = padding
    click.secho("Performed tests:", bold=True)
    template = f"    {{:{col1_len}}}{{:{col2_len}}}{{:{col3_len}}}"
    for check_name, results in total.items():
        display_check_result(check_name, results, template)


def display_check_result(
    check_name: str,
    results: Dict[Union[str, Status], int],
    template: str,
) -> None:
    """Show results of single check execution."""
    if Status.failure in results:
        verdict = "FAILED"
        color = "red"
    else:
        verdict = "PASSED"
        color = "green"
    success = results.get(Status.success, 0)
    total = results.get("total", 0)
    click.echo(
        template.format(
            check_name,
            f"{success} / {total} passed",
            click.style(verdict, fg=color, bold=True),
        )
    )


def display_internal_error(
    context: ExecutionContext, event: events.InternalError
) -> None:
    click.secho(event.message, fg="red")
    if event.exception:
        if context.show_errors_tracebacks:
            message = event.exception_with_traceback
        else:
            message = event.exception
        message = (
            f"Error: {message}\n"
            f"Add this option to your command line parameters to see full tracebacks: --show-errors-tracebacks"
        )
        if event.exception_type == "jsonschema.exceptions.ValidationError":
            message += "\n" + DISABLE_SCHEMA_VALIDATION_MESSAGE
        click.secho(message, fg="red")


def handle_initialized(
    context: ExecutionContext, event: events.Initialized[InitializedPayload]
) -> None:
    """Display information about the test session."""
    context.operations_count = cast(
        int, event.payload.operations_count
    )  # INVARIANT: should not be `None`
    display_section_name("Running conformance tests")
    versions = (
        f"platform {platform.system()} -- "
        f"Python {platform.python_version()}, "
        f"hypothesis-{metadata.version('hypothesis')}, "
        f"hypothesis_jsonschema-{metadata.version('hypothesis_jsonschema')}, "
        f"jsonschema-{metadata.version('jsonschema')}"
    )
    log.debug(versions)
    log.debug(f"rootdir: {os.getcwd()}")
    log.debug(
        f"hypothesis profile '{settings._current_profile}' "  # type: ignore
        f"-> {settings.get_profile(settings._current_profile).show_changed()}"
    )
    if event.payload.location is not None:
        click.echo(f"Schema location: {event.payload.location}")
    log.debug(f"Base URL: {event.payload.base_url}")
    log.debug(f"Specification version: {event.payload.specification_name}")
    log.debug(f"Workers: {context.workers_num}")
    click.secho(f"Collected API operations: {context.operations_count}", bold=True)
    if context.operations_count >= 1:
        click.echo()


TRUNCATION_PLACEHOLDER = "[...]"


def handle_before_execution(
    context: ExecutionContext,
    event: events.BeforeTestCaseExecution[BeforeExecutionPayload],
) -> None:
    """Display what method / path will be tested next."""
    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )
    if endpoint_name not in context.endpoint_to_context:
        context.endpoint_to_context[endpoint_name] = EndpointExecutionContext(
            name=endpoint_name
        )

    # We should display execution result + percentage in the end. For example:
    max_length = get_terminal_width() - len(" . [XXX%]") - len(TRUNCATION_PLACEHOLDER)
    message = event.payload.verbose_name
    if event.payload.recursion_level > 0:
        message = f"{'    ' * event.payload.recursion_level}-> {message}"
        # This value is not `None` - the value is set in runtime before this line
        context.operations_count += 1  # type: ignore

    message = message[:max_length] + (message[max_length:] and "[...]") + " "
    context.current_line_length = len(message)
    click.echo(message, nl=False)


def handle_after_execution(
    context: ExecutionContext,
    event: events.AfterTestCaseExecution[AfterExecutionPayload],
) -> None:
    """Display the execution result + current progress at the same line with the method / path names."""
    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )
    endpoint_context = context.endpoint_to_context[endpoint_name]
    endpoint_context.operations_processed += 1

    datagen_method = event.payload.data_generation_method
    if (
        datagen_method
        and datagen_method not in endpoint_context.data_generation_method_to_assertions
    ):
        endpoint_context.data_generation_method_to_assertions[datagen_method] = []
    endpoint_context.data_generation_method_to_assertions[datagen_method].extend(
        event.payload.assertions
    )

    endpoint_context.errors.extend(event.payload.errors)
    display_execution_result(context, event)
    display_percentage(context, endpoint_context)


def _get_endpoint_check_status(assertions: List[AssertionResult]) -> Status:
    for assertion in assertions:
        if assertion.status == Status.error:
            return Status.error
    for assertion in assertions:
        if assertion.status == Status.failure:
            return Status.failure
    return Status.success


def _finish_endpoint(
    context: ExecutionContext, endpoint_context: EndpointExecutionContext
) -> None:
    check_name_to_assertions: Dict[str, List[AssertionResult]] = {}
    for assertions in endpoint_context.data_generation_method_to_assertions.values():
        for assertion in assertions:
            if assertion.name not in check_name_to_assertions:
                check_name_to_assertions[assertion.name] = []
            check_name_to_assertions[assertion.name].append(assertion)
            endpoint_context.duration += assertion.elapsed

    for check_name, assertions in check_name_to_assertions.items():
        status = _get_endpoint_check_status(assertions)
        if status == Status.error:
            endpoint_context.errored_count += 1
        elif status == Status.failure:
            endpoint_context.failed_count += 1
        else:
            endpoint_context.success_count += 1

    if endpoint_context.errored_count > 0:
        endpoint_context.status = Status.error
    elif endpoint_context.failed_count > 0:
        endpoint_context.status = Status.failure
    else:
        endpoint_context.status = Status.success

    context.success_count += endpoint_context.success_count
    context.failed_count += endpoint_context.failed_count
    context.errored_count += endpoint_context.errored_count


def finish_all_endpoints(context: ExecutionContext):
    for endpoint_name, endpoint_context in context.endpoint_to_context.items():
        _finish_endpoint(context, endpoint_context)


def handle_finished(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> None:
    """Show the outcome of the whole testing session."""
    finish_all_endpoints(context)
    status = Status.success
    for endpoint_context in context.endpoint_to_context.values():
        if endpoint_context.status == Status.error:
            status = Status.error
            break
        elif endpoint_context.status == Status.failure and status != Status.error:
            status = Status.failure
    context.status = status

    click.echo()
    display_hypothesis_output(context.hypothesis_output)
    display_errors(context, event)

    # Display the failures at endpoint level.
    display_failures(context, event)

    display_statistic(context, event)
    click.echo()
    display_summary(event)


def handle_interrupted(context: ExecutionContext) -> None:
    finish_all_endpoints(context)
    click.echo()
    display_section_name("KeyboardInterrupt", "!", bold=False)


def handle_internal_error(
    context: ExecutionContext, event: events.InternalError
) -> None:
    finish_all_endpoints(context)
    display_internal_error(context, event)
    raise click.Abort


class SchemathesisConsoleOutputHandler(EventHandler):
    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Choose and execute a proper handler for the given event."""
        if isinstance(event, events.Initialized):
            handle_initialized(context, event)
        if isinstance(event, events.BeforeTestCaseExecution):
            handle_before_execution(context, event)
        if isinstance(event, events.AfterTestCaseExecution):
            context.hypothesis_output.extend(event.payload.hypothesis_output)
            handle_after_execution(context, event)
        if isinstance(event, events.Finished):
            handle_finished(context, event)
        if isinstance(event, events.Interrupted):
            handle_interrupted(context)
        if isinstance(event, events.InternalError):
            handle_internal_error(context, event)
