# -*- coding: utf-8 -*-

from pip_services3_components.trace.NullTracer import NullTracer


class TestNullTracer:
    _tracer: NullTracer

    def setup_method(self):
        self._tracer = NullTracer()

    def test_simple_tracing(self):
        self._tracer.trace("123", "mycomponent", "mymethod", 123456)
        self._tracer.failure("123", "mycomponent", "mymethod", Exception("Test error"), 123456)

    def test_trace_timing(self):
        timing = self._tracer.begin_trace("123", "mycomponent", "mymethod")
        timing.end_trace()

        timing = self._tracer.begin_trace("123", "mycomponent", "mymethod")
        timing.end_failure(Exception("Test error"))
