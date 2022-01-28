import base64
import enum
import time
import traceback
from typing import Dict, Optional, Union

from levo_commons import events
from levo_commons.models import (
    AfterTestExecutionPayload,
    AfterTestSuiteExecutionPayload,
    BeforeTestExecutionPayload,
    BeforeTestSuiteExecutionPayload,
    FinishedPayload,
    InitializedPayload,
    Response,
    SerializedTestResult,
    TestResult,
)
from levo_commons.status import Status
from reportportal_client import ReportPortalService

from ....apitesting.runs.api_test_runs_pb2 import (  # type: ignore
    CATEGORY_FAILED,
    CATEGORY_SUCCESS,
    ApiEndpointTestsCategory,
)
from ....env_constants import TEST_RUNS_SERVICE_URL, get_feature_testing_headers
from ....handlers import EventHandler
from ....logger import get_logger
from ....utils import format_exception
from ...utils import get_formatted_test_result
from ..context import ExecutionContext
from .default import get_run_summary, get_section_name, get_suites_summary_section

STATUS_DICT = {
    Status.success: "PASSED",
    Status.failure: "FAILED",
    Status.error: "ERRORED",
}

log = get_logger(__name__)


def timestamp():
    return str(int(time.time() * 1000))


def handle_before_execution(
    context: ExecutionContext,
    event: events.BeforeTestCaseExecution[BeforeTestExecutionPayload],
    service: ReportPortalService,
) -> None:
    # Test case id here isn't ideal so we need to find what's better.
    endpoint = f"{event.payload.method} {event.payload.relative_path}"
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    case_attr = {
        "case_id": event.payload.test_case_id,
        "category": event.payload.categories[0] if event.payload.categories else None,
    }
    item_id = service.start_test_item(
        name=event.payload.name,
        description=endpoint,
        start_time=timestamp(),
        item_type="TEST",
        test_case_id=event.payload.test_case_id,
        parent_item_id=suite_context.test_item_id,
        attributes=case_attr,
    )
    suite_context.test_case_id_to_item_id[event.payload.test_case_id] = item_id
    log.debug(
        "Starting to execute the test case.",
        item_id=item_id,
        test_case_id=event.payload.test_case_id,
        parent_item_id=suite_context.test_item_id,
        attributes=case_attr,
        endpoint=endpoint,
    )


def handle_after_execution(
    context: ExecutionContext,
    event: events.AfterTestCaseExecution[AfterTestExecutionPayload],
    service: ReportPortalService,
) -> None:
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]
    test_item_id = suite_context.test_case_id_to_item_id[event.payload.test_case_id]
    test_item_attributes = {
        "elapsed_time": event.payload.elapsed_time,
        "thread-id": event.payload.thread_id,
    }
    # If the test result has a summary, that gives a hint of what was the failure. Include it in the attributes.
    if event.payload.result.summary:
        test_item_attributes["summary"] = event.payload.result.summary

    service.finish_test_item(
        item_id=test_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[event.payload.status],
        attributes=test_item_attributes,
    )
    log.debug(
        "Finished executing the test case.",
        item_id=test_item_id,
        test_case_id=event.payload.test_case_id,
        attributes=test_item_attributes,
        test_suite_id=suite_context.test_item_id,
    )

    if event.payload.result.has_errors:
        report_log(
            message=_get_single_error(context, event.payload.result),
            service=service,
            level="ERROR",
            item_id=test_item_id,
        )
    if event.payload.result.has_failures:
        report_log(
            message=get_failures_for_single_test(context, event.payload.result),
            service=service,
            level="ERROR",
            item_id=test_item_id,
        )

    if event.payload.result:
        _send_result(event, service, test_item_id)


def _send_result(event, service, test_item_id) -> None:
    serialized_result = SerializedTestResult.from_test_result(event.payload.result)
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


def _get_single_error(
    context: ExecutionContext,
    result: TestResult,
) -> str:
    lines = [get_section_name("ERRORS")]
    for error in result.errors:
        lines.append(
            format_exception(error, context.show_errors_tracebacks)
            if isinstance(error, Exception)
            else error
        )
    return "\n".join(lines)


def get_failures(
    context: ExecutionContext, event: events.Finished[FinishedPayload]
) -> Optional[str]:
    """Get all failures in the test run."""
    if not event.payload.has_failures:
        return None
    relevant_results = [
        result
        for context in context.test_suite_id_to_context.values()
        for result in context.results
        if not result.is_errored
    ]
    if not relevant_results:
        return None
    lines = [get_section_name("FAILURES")]
    for result in relevant_results:
        if not result.has_failures:
            continue
        lines.append(get_failures_for_single_test(context, result))
    return "\n".join(lines)


def get_failures_for_single_test(
    context: ExecutionContext,
    result: TestResult,
) -> str:
    """Gets a failure for a single method / path."""
    lines = [get_section_name("FAILURES")]
    for idx, assertion in enumerate(result.assertions.values(), 1):
        message: Optional[str]
        if assertion.message:
            message = f"{idx}. {assertion.message}"
        else:
            message = None
        if len(assertion.interactions) > 0:
            lines.append(
                get_example(context, assertion.interactions[-1].response, message)
            )
    return "\n".join(lines)


def get_example(
    context: ExecutionContext,
    response: Optional[Response] = None,
    message: Optional[str] = None,
) -> str:
    lines = []
    if message is not None:
        if not context.verbosity:
            lines.append(message)

    if response is not None and response.body is not None:
        payload = base64.b64decode(response.body).decode(
            response.encoding or "utf8", errors="replace"
        )
        lines.append(f"----------\n\nResponse payload: `{payload}`\n")
    return "\n".join(lines)


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
    return message


def handle_finished(
    context: ExecutionContext,
    event: events.Finished[FinishedPayload],
    service: ReportPortalService,
) -> None:
    """Show the outcome of the whole testing session."""
    suite_to_status_summary: Dict[str, Dict[Union[str, Status], int]] = {}
    for suite_id, suite_context in context.test_suite_id_to_context.items():
        suite_to_status_summary[suite_context.name] = {
            "total": len(suite_context.test_case_id_to_item_id),
            Status.success: suite_context.success_count,
            Status.error: suite_context.errored_count,
            Status.failure: suite_context.failed_count,
        }

    report_log(get_suites_summary_section(suite_to_status_summary), service)
    report_log(get_run_summary(context, event.running_time), service)


def get_test_run_status(context: ExecutionContext):
    status = Status.success
    for suite_context in context.test_suite_id_to_context.values():
        if suite_context.errored_count > 0:
            # Test run is treated as errored out even if there was one test suite which errored
            status = Status.error
        elif suite_context.failed_count > 0 and status != Status.error:
            # Test run is treated as failed out even if there was one test suite which failed
            status = Status.failure
    return status


def report_log(
    message: str, service: ReportPortalService, level="INFO", item_id=None
) -> None:
    if message is None:
        return
    service.log(time=timestamp(), message=message, item_id=item_id, level=level)


def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
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
    log.info(f"Terminated the launch with status: {status}")
    service.terminate()


class HandlerState(enum.Enum):
    """Different states for ReportPortal handler lifecycle."""

    # Instance is created. The default state
    NEW = enum.auto()
    # Launch started, ready to handle events
    ACTIVE = enum.auto()
    # Launch is interrupted, no events will be processed after it
    INTERRUPTED = enum.auto()


def handle_before_suite_execution(
    context: ExecutionContext,
    event: events.BeforeTestSuiteExecution[BeforeTestSuiteExecutionPayload],
    service: ReportPortalService,
) -> None:
    # Start a test suite run in ReportPortal.
    suite_attr = {"suite_id": event.payload.test_suite_id}
    item_id = service.start_test_item(
        name=event.payload.name,
        description=event.payload.name,
        start_time=timestamp(),
        item_type="SUITE",
        attributes=suite_attr,
    )
    # Add a context at the test suite level and record the item id.
    context.test_suite_id_to_context[event.payload.test_suite_id].test_item_id = item_id
    log.info(
        "Starting to execute the test suite.",
        suite_id=event.payload.test_suite_id,
        suite_name=event.payload.name,
    )


def handle_after_suite_execution(
    context: ExecutionContext,
    event: events.AfterTestSuiteExecution[AfterTestSuiteExecutionPayload],
    service: ReportPortalService,
) -> None:
    suite_context = context.test_suite_id_to_context[event.payload.test_suite_id]

    test_item_attributes = {
        "elapsed_time": event.running_time,
        "thread-id": event.payload.thread_id,
        "success_count": suite_context.success_count,
        "failed_count": suite_context.failed_count,
        "errored_count": suite_context.errored_count,
    }
    service.finish_test_item(
        item_id=suite_context.test_item_id,
        end_time=timestamp(),
        status=STATUS_DICT[suite_context.status],
        attributes=test_item_attributes,
    )
    log.debug(
        "Finished executing the test suite.",
        item_id=suite_context.test_item_id,
        status=suite_context.status,
        attributes=test_item_attributes,
    )


def handle_initialized_event(
    plan_lrn: str,
    event: events.Initialized[InitializedPayload],
    service: ReportPortalService,
):
    # Create a launch in report portal
    launch_name = event.payload.plan_name
    launch_attr = {
        "plan_id": event.payload.plan_id,
        "target_url": event.payload.target_url,
    }
    if plan_lrn:
        launch_attr["plan_lrn"] = plan_lrn
    init_attrs = event.payload.attributes
    # Copy the app_id and service_id from the generic attributes coming in the event payload.
    # Although the event contains the app and service ids as lists, we don't support test plan across
    # multiple apps today, hence we only use one app id.
    if "app_ids" in init_attrs and init_attrs["app_ids"]:
        launch_attr["app_id"] = init_attrs["app_ids"][0]
    launch_attr["service_ids"] = (
        init_attrs["service_ids"] if "service_ids" in init_attrs else []
    )

    launch_id = service.start_launch(
        name=launch_name,
        start_time=timestamp(),
        description=launch_name,
        attributes=launch_attr,
    )
    log.info(
        "Started the test launch.",
        name=launch_name,
        id=launch_id,
        attributes=launch_attr,
    )


class TestPlanReportPortalHandler(EventHandler):
    def __init__(self, plan, token):
        self.service = ReportPortalService(
            endpoint=TEST_RUNS_SERVICE_URL,
            project=plan.workspace_id,
            token=token,
            log_batch_size=1,
        )
        feature_testing_headers = get_feature_testing_headers()
        if feature_testing_headers:
            for k, v in feature_testing_headers:
                self.service.session.headers[k] = v
        self.plan = plan
        self.state = HandlerState.NEW

    def _set_state(self, state: HandlerState) -> None:
        self.state = state

    def _terminate_launch(
        self, status: str, success_count: int, failed_count: int, errored_count: int
    ) -> None:
        if self.state == HandlerState.ACTIVE:
            terminate_launch(
                self.service, status, success_count, failed_count, errored_count
            )
        elif self.state == HandlerState.INTERRUPTED:
            log.info("The test launch is interrupted.")
            terminate_launch(
                self.service, "INTERRUPTED", success_count, failed_count, errored_count
            )

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Reports the test results to ReportPortal service."""
        if isinstance(event, events.Initialized):
            handle_initialized_event(self.plan.lrn, event, self.service)
            self._set_state(HandlerState.ACTIVE)
        if isinstance(event, events.BeforeTestSuiteExecution):
            handle_before_suite_execution(context, event, self.service)
        if isinstance(event, events.AfterTestSuiteExecution):
            handle_after_suite_execution(context, event, self.service)
        if isinstance(event, events.BeforeTestCaseExecution):
            handle_before_execution(context, event, self.service)
        if isinstance(event, events.AfterTestCaseExecution):
            handle_after_execution(context, event, self.service)
        if isinstance(event, events.Finished):
            handle_finished(context, event, self.service)
            status = STATUS_DICT[get_test_run_status(context)]
            status = {
                HandlerState.ACTIVE: status,
                HandlerState.INTERRUPTED: "INTERRUPTED",
            }[self.state]
            self._terminate_launch(
                status,
                context.success_count,
                context.failed_count,
                context.errored_count,
            )
        if isinstance(event, events.Interrupted):
            self._set_state(HandlerState.INTERRUPTED)
        if isinstance(event, events.InternalError):
            if event.is_terminal:
                self._terminate_launch(
                    "FAILED",
                    context.success_count,
                    context.failed_count,
                    context.errored_count,
                )
            else:
                # Report the test case error to SaaS.
                pass
