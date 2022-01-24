from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosSentryInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'helios.sentry_instrumentation.src.sentry'
    INSTRUMENTOR_NAME = 'SentrySdkInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is not None:
            self.get_instrumentor().instrument()

    def uninstrument(self):
        if self.get_instrumentor() is not None:
            self.get_instrumentor().uninstrument()
