from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosPySparkInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'helios.pyspark_instrumentation.src.pyspark'
    INSTRUMENTOR_NAME = 'PySparkInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)
