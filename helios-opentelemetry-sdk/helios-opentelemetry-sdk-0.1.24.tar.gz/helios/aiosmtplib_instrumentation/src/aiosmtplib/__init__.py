import aiosmtplib
from wrapt import wrap_function_wrapper
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from helios.aiosmtplib_instrumentation.src.aiosmtplib.package import _instruments


class AttributeNames:
    SENDER = 'aiosmtplib.sender'
    RECIPIENTS = 'aiosmtplib.recipients'
    MESSAGE = 'aiosmtplib.message'


def extract_span_parameters(args):
    if len(args) > 0:
        sender = args[0]
    if len(args) > 1:
        recipients = args[1]
    if len(args) > 2 and type(args[2]) == bytes:
        message = args[2].decode()

    return sender, recipients, message


class AiosmtplibInstrumentor(BaseInstrumentor):
    SPAN_NAME = 'aiosmtplib.sendmail'

    def _instrument(self, **kwargs):
        tracer_provider = kwargs.get('tracer_provider')
        tracer = trace.get_tracer(
            'opentelemetry.instrumentation.aiosmtplib', aiosmtplib.__version__, tracer_provider=tracer_provider
        )

        def send_wrapper(wrapped, _instance, args, kwargs):
            with tracer.start_as_current_span(self.SPAN_NAME, kind=trace.SpanKind.CLIENT) as span:
                sender, recipients, message = extract_span_parameters(args)
                span.set_attribute(AttributeNames.SENDER, sender) if sender else None
                span.set_attribute(AttributeNames.RECIPIENTS, recipients) if recipients else None
                span.set_attribute(AttributeNames.MESSAGE, message) if message else None

                return wrapped(*args, **kwargs)

        wrap_function_wrapper("aiosmtplib", "SMTP.sendmail", send_wrapper)

    def _uninstrument(self, **kwargs):
        unwrap(aiosmtplib.SMTP, "sendmail")

    def instrumentation_dependencies(self):
        return _instruments
