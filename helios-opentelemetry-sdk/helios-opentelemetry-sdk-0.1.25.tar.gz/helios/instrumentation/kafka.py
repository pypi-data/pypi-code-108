from helios.instrumentation.base import HeliosBaseInstrumentor


class HeliosKafkaInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'helios.kafka_instrumentation.src.kafka'
    INSTRUMENTOR_NAME = 'KafkaInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.get_instrumentor().instrument(tracer_provider=tracer_provider)
