import wrapt

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor
from helios.instrumentation.helios_asgi_middleware import HeliosAsgiMiddleware


class HeliosStarletteInstrumentor(HeliosBaseHttpInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.starlette'
    INSTRUMENTOR_NAME = 'StarletteInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)
        self.tracer_provider = None
        self.instrumented_apps = set()

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return

        self.tracer_provider = tracer_provider
        wrapt.wrap_function_wrapper('starlette.applications', 'Starlette.__init__', self.starlette_instrument_and_run)

    def uninstrument(self):
        if self.get_instrumentor() is None:
            return

        for app in self.instrumented_apps:
            self.get_instrumentor().uninstrument()
        self.instrumented_apps = set()

    def starlette_instrument_and_run(self, wrapped, instance, args, kwargs):
        res = wrapped(*args, **kwargs)
        if instance not in self.instrumented_apps:
            self.instrumented_apps.add(instance)
            self.get_instrumentor().instrument_app(instance,
                                                   # server_request_hook=self.server_request_hook,
                                                   # client_request_hook=self.client_request_hook,
                                                   # client_response_hook=self.client_response_hook,
                                                   tracer_provider=self.tracer_provider)
            get_route_details = HeliosBaseHttpInstrumentor.import_attribute(self.MODULE_NAME, '_get_route_details')
            instance.add_middleware(HeliosAsgiMiddleware,
                                    tracer=self.tracer_provider.get_tracer(self.MODULE_NAME),
                                    get_span_details=get_route_details)
        return res
