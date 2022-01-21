import enum
import time
import traceback
from typing import Dict, List, Optional, Union, cast

import click
from levo_commons import events
from levo_commons.models import (
    AssertionResult,
    SerializedError,
    SerializedTestResult,
    Step,
    StepRecord,
    StepRecordType,
    TestResult,
)
from reportportal_client import ReportPortalService

from ....apitesting.runs.api_test_runs_pb2 import (  # type: ignore
    CATEGORY_FAILED,
    CATEGORY_SUCCESS,
    ApiEndpointTestsCategory,
)
from ....env_constants import TEST_RUNS_SERVICE_URL
from ....handlers import EventHandler
from ....logger import get_logger
from ....utils import fetch_schema_as_lines
from ...utils import get_formatted_test_result
from ..context import EndpointExecutionContext, ExecutionContext
from ..models import BeforeExecutionPayload, FinishedPayload, Status
from .default import get_summary_message_parts

log = get_logger(__name__)

DISABLE_SCHEMA_VALIDATION_MESSAGE = (
    "\nYou can disable input schema validation with --validate-schema=false "
    "command-line option\nIn this case, Schemathesis cannot guarantee proper"
    " behavior during the test run"
)

STATUS_DICT = {
    Status.success: "PASSED",
    Status.failure: "FAILED",
    Status.error: "ERRORED",
}


class HandlerState(enum.Enum):
    """Different states for ReportPortal handler lifecycle."""

    # Instance is created. The default state
    NEW = enum.auto()
    # Launch started, ready to handle events
    ACTIVE = enum.auto()
    # Launch is interrupted, no events will be processed after it
    INTERRUPTED = enum.auto()


def timestamp():
    return str(int(time.time() * 1000))


def _get_endpoint_name(method, relative_path):
    return f"{method} {relative_path}"


def handle_before_execution(
    context: ExecutionContext,
    event: events.BeforeTestCaseExecution[BeforeExecutionPayload],
    service: ReportPortalService,
) -> None:
    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )

    if endpoint_name not in context.endpoint_to_context:
        # Ideally this shouldn't happen because the default handler should have added the context for endpoint already.
        # For now log the information and exit so that we can debug it further.
        click.secho(
            "Handler configuration seems to be wrong. Endpoint context is missing for Schemathesis run.",
            fg="red",
        )
        raise click.exceptions.Exit(1)

    endpoint_context = context.endpoint_to_context[endpoint_name]
    if endpoint_context.operations_processed == 0:
        item_id = service.start_test_item(
            name=endpoint_name,
            description=endpoint_name,
            start_time=timestamp(),
            item_type="SUITE",
        )
        endpoint_context.test_item_id = item_id
        log.info(
            f"Started the test suite for endpoint: {endpoint_name}",
            context=endpoint_context,
        )

    if event.payload.recursion_level > 0:
        # This value is not `None` - the value is set in runtime before this line
        context.operations_count += 1  # type: ignore


def _convert_to_test_result(
    datagen_to_assertions: Dict[str, List[AssertionResult]],
    status: Status,
    summary: Optional[str],
) -> TestResult:
    assertions_map = {}
    interactions_map = {}
    for datagen, assertions in datagen_to_assertions.items():
        if assertions:
            # Copy only one assertion from each data generation method because we don't want to duplicate
            assertions_map[assertions[0].id] = assertions[0]

            for assertion in assertions:
                # Copy the id as interaction name
                assertion.interactions[0].name = assertion.interactions[0].id
                interactions_map[assertion.interactions[0].id] = assertion.interactions[
                    0
                ]

    # Create a separate step for each datagen method.
    steps = []
    for datagen_method, assertions in datagen_to_assertions.items():
        steps.append(
            Step(
                title="Positive data generation method"
                if datagen_method == "P"
                else "Negative data generation method",
                status=Status.success,
                records=[
                    StepRecord(
                        record_id=assertion.interactions[0].id,
                        type=StepRecordType.interaction,
                        summary=assertion.name,
                    )
                    for assertion in assertions
                ],
            )
        )

    return TestResult(
        # TODO: There could be 100s of assertions and interactions in a single test case. We should limit the number.
        assertions=assertions_map,
        errors=[],
        interactions=interactions_map,
        logs={},
        steps=steps,
        is_errored=status == Status.error,
        summary=summary,
        overridden_headers={},
    )


def _report_check_as_test_case(
    endpoint_name: str,
    check_name: str,
    datagen_to_assertions: Dict[str, List[AssertionResult]],
    endpoint_context: EndpointExecutionContext,
    service,
):
    test_case_item_id = service.start_test_item(
        name=check_name,
        description=check_name,
        start_time=timestamp(),
        item_type="TEST",
        # Mark the test suite item id as parent_item_id
        parent_item_id=endpoint_context.test_item_id,
    )

    duration = 0
    successful_tests = 0
    failed_tests = 0
    errored_tests = 0
    assertions = []
    for assertions_list in datagen_to_assertions.values():
        assertions.extend(assertions_list)

    for assertion in assertions:
        duration += assertion.elapsed
        if assertion.status == Status.error:
            errored_tests += 1
        elif assertion.status == Status.failure:
            failed_tests += 1
        else:
            successful_tests += 1

    status = (
        Status.error
        if errored_tests > 0
        else Status.failure
        if failed_tests > 0
        else Status.success
    )
    summary = (
        "API Endpoint conforms to the schema as specified in the spec file."
        if status == Status.success
        else "Runtime behavior of the API Endpoint was not conforming to the spec."
        " Please check the log for more details."
    )
    test_item_attributes = {
        "elapsed_time": duration,
        "success_count": successful_tests,
        "failed_count": failed_tests,
        "errored_count": errored_tests,
        "summary": summary,
    }
    service.finish_test_item(
        item_id=test_case_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[status],
        attributes=test_item_attributes,
    )
    log.debug(
        f"Finished the test case for check: {check_name} and endpoint: {endpoint_name}",
        attributes=test_item_attributes,
        item_id=test_case_item_id,
        status=status,
    )

    # Send the test case result at the end to SaaS.
    result = _convert_to_test_result(datagen_to_assertions, status, summary)
    _send_result(result, service, test_case_item_id)
    return status


def _send_result(
    result: TestResult, service: ReportPortalService, test_item_id: str
) -> None:
    serialized_result = SerializedTestResult.from_test_result(result)
    json_attachment = {
        "name": f"case-result-{test_item_id}",
        "data": get_formatted_test_result(serialized_result),
        "mime": "application/json",
    }
    service.log(timestamp(), json_attachment["name"], attachment=json_attachment)

    log.debug(
        "Sending the result for test case.",
        item_id=test_item_id,
        attachment=json_attachment,
    )


def get_hypothesis_output(hypothesis_output: List[str]) -> Optional[str]:
    """Show falsifying examples from Hypothesis output if there are any."""
    if hypothesis_output:
        return get_section_name("HYPOTHESIS OUTPUT") + "\n".join(hypothesis_output)
    return None


def get_errors(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> Optional[str]:
    """Get all errors in the test run."""
    if not event.payload.has_errors:
        return None

    lines = [get_section_name("ERRORS")]
    for endpoint_context in context.endpoint_to_context.values():
        if endpoint_context.errors:
            lines.append(
                get_single_error(
                    context, endpoint_context.name, endpoint_context.errors[0]
                )
            )
    if event.payload.generic_errors:
        lines.append(get_generic_errors(context, event.payload.generic_errors))
    return "\n".join(lines)


def get_single_error(
    context: ExecutionContext,
    endpoint_name: str,
    error: SerializedError,
) -> str:
    lines = [get_section_name(endpoint_name), _get_error(context, error)]
    return "\n".join(lines)


def get_generic_errors(
    context: ExecutionContext,
    errors: List[SerializedError],
) -> str:
    lines = []
    for error in errors:
        lines.append(get_section_name(error.title or "Generic error", "_"))
        lines.append(_get_error(context, error))
    return "\n".join(lines)


def _get_error(
    context: ExecutionContext,
    error: SerializedError,
) -> str:
    if context.show_errors_tracebacks:
        message = error.exception_with_traceback
    else:
        message = error.exception
    if error.exception.startswith("InvalidSchema") and context.validate_schema:
        message += DISABLE_SCHEMA_VALIDATION_MESSAGE + "\n"
    return message


def reduce_schema_error(message: str) -> str:
    """Reduce the error schema output."""
    end_of_message_index = message.find(":", message.find("Failed validating"))
    if end_of_message_index != -1:
        return message[:end_of_message_index]
    return message


def get_checks_statistics(total: Dict[str, Dict[Union[str, Status], int]]) -> str:
    lines = []
    for check_name, results in total.items():
        lines.append(get_check_result(check_name, results))
    return "Performed checks:" + "\n".join(lines)


def get_check_result(
    check_name: str,
    results: Dict[Union[str, Status], int],
) -> str:
    """Show results of single check execution."""
    success = results.get(Status.success, 0)
    total = results.get("total", 0)
    return check_name + ": " + f"{success} / {total} passed"


def get_internal_error(
    context: ExecutionContext, event: events.InternalError
) -> Optional[str]:
    message = None
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
    return message


def get_summary(event: events.Finished[FinishedPayload]) -> str:
    message = get_summary_output(event)
    return get_section_name(message)


def get_summary_output(event: events.Finished[FinishedPayload]) -> str:
    parts = get_summary_message_parts(event)
    if not parts:
        message = "Empty test suite"
    else:
        message = f'{", ".join(parts)} in {event.running_time:.2f}s'
    return message


def get_section_name(title: str, separator: str = "=", extra: str = "") -> str:
    """Print section name with separators in terminal with the given title nicely centered."""
    extra = extra if not extra else f" [{extra}]"
    return f" {title}{extra} ".center(80, separator)


def handle_finished(
    context: ExecutionContext,
    event: events.Finished[FinishedPayload],
    service: ReportPortalService,
):
    """Report the outcome of the whole testing session to Levo SaaS."""
    # Report each check for each endpoint as a test case.
    for endpoint_name, endpoint_context in context.endpoint_to_context.items():
        _report_finish_endpoint(endpoint_context, endpoint_name, service)
    report_log(get_summary(event), service)


def _report_finish_endpoint(
    endpoint_context: EndpointExecutionContext, endpoint_name, service
):
    # Report all the checks for this endpoint as test cases first.
    check_name_to_assertions: Dict[str, Dict[str, List[AssertionResult]]] = {}
    for (
        datagen_method,
        assertions,
    ) in endpoint_context.data_generation_method_to_assertions.items():
        for assertion in assertions:
            if assertion.name not in check_name_to_assertions:
                check_name_to_assertions[assertion.name] = {}

            if datagen_method not in check_name_to_assertions[assertion.name]:
                check_name_to_assertions[assertion.name][datagen_method] = []
            check_name_to_assertions[assertion.name][datagen_method].append(assertion)

    for check_name, datagen_to_assertions in check_name_to_assertions.items():
        _report_check_as_test_case(
            endpoint_context.name,
            check_name,
            datagen_to_assertions,
            endpoint_context,
            service,
        )

    # Finish the test suite for this endpoint.
    test_item_attributes = {
        "elapsed_time": endpoint_context.duration,
        "success_count": endpoint_context.success_count,
        "failed_count": endpoint_context.failed_count,
        "errored_count": endpoint_context.errored_count,
    }
    service.finish_test_item(
        item_id=endpoint_context.test_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[endpoint_context.status],
        attributes=test_item_attributes,
    )
    log.info(
        f"Test Suite for endpoint: {endpoint_name} finished with status: {endpoint_context.status}"
    )


def report_log(
    message: str, service: ReportPortalService, level="INFO", item_id=None
) -> None:
    if message is None:
        return
    service.log(time=timestamp(), message=message, item_id=item_id, level=level)
    log.debug("Reporting the log.", message=message, item_id=item_id)


def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical, and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    traceback.print_exception(*exc_info)


def terminate_launch(
    service: ReportPortalService,
    status="PASSED",
    success_count=0,
    failed_count=0,
    errored_count=0,
) -> None:
    launch_attributes = {
        "success_count": success_count,
        "failed_count": failed_count,
        "errored_count": errored_count,
    }
    service.finish_launch(
        end_time=timestamp(), status=status, attributes=launch_attributes
    )
    log.info(f"Finished the launch with status: {status}")
    service.terminate()


class SchemathesisReportPortalHandler(EventHandler):
    def __init__(self, project, token, spec_path):
        self.service = ReportPortalService(
            endpoint=TEST_RUNS_SERVICE_URL, project=project, token=token
        )
        self.state = HandlerState.NEW
        self.spec = fetch_schema_as_lines(spec_path)

    def _set_state(self, state: HandlerState) -> None:
        self.state = state

    def _terminate_launch(
        self, status: str, success_count: int, failed_count: int, errored_count: int
    ) -> None:
        if self.state == HandlerState.ACTIVE:
            terminate_launch(
                self.service, status, success_count, failed_count, errored_count
            )

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Reports the test results to ReportPortal service."""
        if isinstance(event, events.Initialized):
            # Create a launch in report portal
            launch_name = "Schema conformance test"
            launch_attr = {
                "target_url": event.payload.base_url,
            }
            self.service.start_launch(
                name=launch_name,
                start_time=timestamp(),
                description=launch_name,
                attributes=launch_attr,
            )
            self._set_state(HandlerState.ACTIVE)
            context.operations_count = cast(
                int, event.payload.operations_count
            )  # INVARIANT: should not be `None`
            log.info(
                f"Test is ready to be run with {context.operations_count} endpoints."
            )
        if isinstance(event, events.BeforeTestCaseExecution):
            handle_before_execution(context, event, self.service)
        if isinstance(event, events.AfterTestCaseExecution):
            pass
        if isinstance(event, events.Finished):
            # Send the schema as an attachment.
            attachment = {
                "name": "schema",
                "data": "".join(self.spec),
                "mime": "text/plain",
            }
            self.service.log(timestamp(), "schema", attachment=attachment)
            handle_finished(context, event, self.service)
            status = {
                HandlerState.ACTIVE: STATUS_DICT[context.status],
                HandlerState.INTERRUPTED: "INTERRUPTED",
            }[self.state]
            self._terminate_launch(
                status,
                context.success_count,
                context.failed_count,
                context.errored_count,
            )
        if isinstance(event, events.Interrupted):
            log.info("Test run is interrupted.")
            self._set_state(HandlerState.INTERRUPTED)
        if isinstance(event, events.InternalError):
            self._terminate_launch(
                "FAILED",
                context.success_count,
                context.failed_count,
                context.errored_count,
            )
