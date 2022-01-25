from inspect import iscoroutinefunction
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

try:
    from opentelemetry.instrumentation.celery import CeleryInstrumentor

    CeleryInstrumentor().instrument()
except ImportError:
    pass


RequestsInstrumentor().instrument()
HTTPXClientInstrumentor().instrument()
tracer = trace.get_tracer(__name__)


def span(name: str = None):
    def _span(func):
        if iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):
                with tracer.start_as_current_span(name or func.__name__):
                    return await func(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                with tracer.start_as_current_span(name or func.__name__):
                    return func(*args, **kwargs)

        return wrapper

    return _span


def instrument_app(app: FastAPI):
    FastAPIInstrumentor().instrument_app(app)


def create_tracer(service_name, tempo):
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    )

    jaeger_exporter = JaegerExporter(
        collector_endpoint=tempo["host"] + "/api/traces",
    )

    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

    set_global_textmap(
        CompositePropagator(
            [
                B3MultiFormat(),
                JaegerPropagator(),
                TraceContextTextMapPropagator(),
                W3CBaggagePropagator(),
            ]
        )
    )
