import os
import sentry_sdk

from typing import Collection
from wrapt import wrap_function_wrapper

from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap

from helios.defaults import DEFAULT_HS_API_ENDPOINT
from helios.sentry_instrumentation.src.sentry.package import _instruments
from helios.utils import encode_id_as_hex_string

HS_API_ENDPOINT = os.environ.get('HS_API_ENDPOINT') or DEFAULT_HS_API_ENDPOINT


def _instrument():

    def wrap_capture_call(func, instance, args, kwargs):
        span = trace.get_current_span()
        if span and span.is_recording():
            trace_id = encode_id_as_hex_string(span.get_span_context().trace_id)
            with sentry_sdk.push_scope() as scope:
                scope.set_context('Helios', {'Trace visualization': f'{HS_API_ENDPOINT}?actionTraceId={trace_id}'})
                scope.set_tag('helios-trace-id', trace_id)
                return func(*args, **kwargs)
        return func(*args, **kwargs)

    wrap_function_wrapper('sentry_sdk', 'capture_event', wrap_capture_call)
    wrap_function_wrapper('sentry_sdk', 'capture_exception', wrap_capture_call)
    wrap_function_wrapper('sentry_sdk', 'capture_message', wrap_capture_call)


class SentrySdkInstrumentor(BaseInstrumentor):

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        _instrument()

    def _uninstrument(self, **kwargs):
        unwrap(sentry_sdk, 'capture_event')
        unwrap(sentry_sdk, 'capture_exception')
        unwrap(sentry_sdk, 'capture_message')
