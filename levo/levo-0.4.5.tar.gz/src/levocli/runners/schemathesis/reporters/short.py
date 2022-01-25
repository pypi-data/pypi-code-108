from levo_commons import events

from ....handlers import EventHandler
from ..context import EndpointExecutionContext, ExecutionContext
from . import default


def _get_endpoint_name(method, relative_path):
    return f"{method} {relative_path}"


def handle_before_execution(
    context: ExecutionContext, event: events.BeforeTestCaseExecution
) -> None:
    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )
    context.endpoint_to_context[endpoint_name] = EndpointExecutionContext(
        name=endpoint_name
    )

    if event.payload.recursion_level > 0:
        context.operations_count += 1  # type: ignore


def handle_after_execution(
    context: ExecutionContext, event: events.AfterTestCaseExecution
) -> None:
    endpoint_name = _get_endpoint_name(
        event.payload.method, event.payload.relative_path
    )
    endpoint_context = context.endpoint_to_context[endpoint_name]
    endpoint_context.operations_processed += 1

    datagen_method = event.payload.data_generation_method
    if datagen_method not in endpoint_context.data_generation_method_to_assertions:
        endpoint_context.data_generation_method_to_assertions[datagen_method] = []
    endpoint_context.data_generation_method_to_assertions[datagen_method].extend(
        event.payload.assertions
    )

    context.hypothesis_output.extend(event.payload.hypothesis_output)
    default.display_execution_result(context, event)


class ShortOutputStyleHandler(EventHandler):
    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        """Short output style shows single symbols in the progress bar.

        Otherwise, identical to the default output style.
        """
        if isinstance(event, events.Initialized):
            default.handle_initialized(context, event)
        if isinstance(event, events.BeforeTestCaseExecution):
            handle_before_execution(context, event)
        if isinstance(event, events.AfterTestCaseExecution):
            handle_after_execution(context, event)
        if isinstance(event, events.Finished):
            default.handle_finished(context, event)
        if isinstance(event, events.Interrupted):
            default.handle_interrupted(context)
        if isinstance(event, events.InternalError):
            default.handle_internal_error(context, event)
