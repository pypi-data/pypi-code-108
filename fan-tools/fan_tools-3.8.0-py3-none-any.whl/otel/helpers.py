from contextlib import contextmanager
from typing import Any, Dict

from opentelemetry.propagate import extract, inject
from opentelemetry.trace import get_tracer, SpanKind


@contextmanager
def extract_span(
    headers: Dict[str, Any], mod_name: str, name: str, kind: SpanKind = SpanKind.CLIENT
):
    ctx = extract(headers)
    tracer = get_tracer(mod_name)
    with tracer.start_as_current_span(name, context=ctx, kind=kind) as span:
        yield span
