from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosAiosmtplibInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'helios.aiosmtplib_instrumentation.src.aiosmtplib'
    INSTRUMENTOR_NAME = 'AiosmtplibInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)
