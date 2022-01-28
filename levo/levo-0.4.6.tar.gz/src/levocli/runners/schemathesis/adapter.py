from levo_commons import events
from levo_commons.failures import Evidence
from levo_commons.models import (
    AssertionResult,
    Confidence,
    Interaction,
    Request,
    Response,
    SerializedError,
    Status,
)
from schemathesis.failures import RequestTimeout
from schemathesis.models import Status as SeStatus
from schemathesis.runner import events as se
from schemathesis.runner.serialization import SerializedCheck
from schemathesis.runner.serialization import SerializedError as SeSerializedError
from schemathesis.runner.serialization import SerializedInteraction

from .models import (
    AfterExecutionPayload,
    BeforeExecutionPayload,
    FinishedPayload,
    InitializedPayload,
    SchemaConformanceCheck,
)

STATUS_MAP = {
    SeStatus.success: Status.success,
    SeStatus.error: Status.error,
    SeStatus.failure: Status.failure,
}


def _convert_status(status: SeStatus) -> Status:
    if STATUS_MAP[status]:
        return STATUS_MAP[status]
    return Status.error


def _convert_interaction(
    interaction: SerializedInteraction, elapsed: float
) -> Interaction:
    return Interaction(
        request=Request(
            method=interaction.request.method,
            uri=interaction.request.uri,
            body=interaction.request.body,
            headers=interaction.request.headers,
        ),
        response=Response(
            method=interaction.request.method,
            uri=interaction.request.uri,
            body=interaction.response.body,
            status_code=interaction.response.status_code,
            message=interaction.response.message,
            headers=interaction.response.headers,
            http_version=interaction.response.http_version,
            encoding=interaction.response.encoding,
        ),
        status=_convert_status(interaction.status),
        recorded_at=interaction.recorded_at,
        elapsed=elapsed,
    )


def _convert_initialized(
    event: se.Initialized,
) -> events.Initialized[InitializedPayload]:
    return events.Initialized(
        start_time=event.start_time,
        payload=InitializedPayload(
            operations_count=event.operations_count,
            location=event.location,
            base_url=event.base_url,
            specification_name=event.specification_name,
        ),
    )


def _convert_before_execution(
    event: se.BeforeExecution,
) -> events.BeforeTestCaseExecution[BeforeExecutionPayload]:
    return events.BeforeTestCaseExecution(
        payload=BeforeExecutionPayload(
            correlation_id=event.correlation_id,
            method=event.method,
            relative_path=event.relative_path,
            verbose_name=event.verbose_name,
            recursion_level=event.recursion_level,
        ),
    )


def _get_duration(check) -> int:
    if isinstance(check.context, RequestTimeout):
        return check.context.timeout
    if check.response is not None:
        return int(check.response.elapsed * 1000)
    # Practically not possible as the request timeout is the only case when response is absent
    raise ValueError("Can not detect check duration")


def _convert_after_execution(
    event: se.AfterExecution,
) -> events.AfterTestCaseExecution[AfterExecutionPayload]:
    assertions = []
    for interaction in event.result.interactions:
        for check in interaction.checks:
            assertions.append(_convert_check(check, interaction))

    return events.AfterTestCaseExecution(
        payload=AfterExecutionPayload(
            method=event.method,
            relative_path=event.relative_path,
            status=_convert_status(event.status),
            elapsed_time=event.elapsed_time,
            correlation_id=event.correlation_id,
            hypothesis_output=event.hypothesis_output,
            assertions=assertions,
            errors=[_convert_error(error) for error in event.result.errors],
            data_generation_method=event.data_generation_method.as_short_name(),
        ),
    )


def _convert_check(
    se_check: SerializedCheck, interaction: SerializedInteraction
) -> AssertionResult:
    check = SchemaConformanceCheck[se_check.name.upper()]  # type: ignore
    status = _convert_status(se_check.value)
    evidence_msg = (
        se_check.message if se_check.message else "Check logs for specific instances."
    )
    evidence = (
        Evidence(title=evidence_msg, param_type=check.param_type, param_path="")
        if check.param_type
        else None
    )
    return AssertionResult(
        name=check.readable_name,
        status=status,
        interactions=[_convert_interaction(interaction, _get_duration(se_check))],
        elapsed=_get_duration(se_check),
        recorded_at=interaction.recorded_at,
        # TODO: Fix this later.
        confidence=Confidence.high,
        risk=check.risk,
        message=se_check.message,
        solution=check.solution,
        cwe=check.cwe,
        reference=check.cwe_url,
        evidence=evidence,
    )


def _convert_internal_error(event: se.InternalError) -> events.InternalError:
    return events.InternalError(
        message=event.message,
        exception_type=event.exception_type,
        exception=event.exception,
        exception_with_traceback=event.exception_with_traceback,
    )


def _convert_finished(event: se.Finished) -> events.Finished[FinishedPayload]:
    # Convert the Schemathesis Status enum to levo-commons Status enum.
    total = {}
    if event.total:
        for key, value in event.total.items():
            inner_dict = {}
            for k, v in value.items():
                if type(k) == str:
                    inner_dict[k] = v
                else:
                    inner_dict[_convert_status(k)] = v
            total[key] = inner_dict

    return events.Finished(
        running_time=event.running_time,
        payload=FinishedPayload(
            has_failures=event.has_failures,
            has_errors=event.has_errors,
            is_empty=event.is_empty,
            total=total,
            generic_errors=[_convert_error(error) for error in event.generic_errors],
        ),
    )


def _convert_error(error: SeSerializedError) -> SerializedError:
    return SerializedError(
        exception=error.exception,
        exception_with_traceback=error.exception_with_traceback,
        title=error.title,
    )


def convert_event(event: se.ExecutionEvent) -> events.Event:
    """Convert Schemathesis events to Levo events."""
    handler = {
        se.Initialized: _convert_initialized,
        se.BeforeExecution: _convert_before_execution,
        se.AfterExecution: _convert_after_execution,
        se.Interrupted: lambda e: events.Interrupted(),
        se.InternalError: _convert_internal_error,
        se.Finished: _convert_finished,
    }[event.__class__]
    return handler(event)
