import wrapt

from helios.instrumentation.base_http_instrumentor import HeliosBaseHttpInstrumentor
from helios.instrumentation.helios_asgi_middleware import HeliosAsgiMiddleware


class HeliosFastAPIInstrumentor(HeliosBaseHttpInstrumentor):

    MODULE_NAME = 'opentelemetry.instrumentation.fastapi'
    INSTRUMENTOR_NAME = 'FastAPIInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)
        self.tracer_provider = None
        self.instrumented_apps = set()

    def instrument(self, tracer_provider=None):
        if self.get_instrumentor() is None:
            return
        self.tracer_provider = tracer_provider
        wrapt.wrap_function_wrapper('fastapi', 'FastAPI.__init__', self.fastapi_instrument_and_init)

    def uninstrument(self):
        if self.get_instrumentor() is None:
            return

        for app in self.instrumented_apps:
            self.get_instrumentor().uninstrument_app(app)
        self.instrumented_apps = set()

    def fastapi_instrument_and_init(self, wrapped, instance, args, kwargs):
        init_response = wrapped(*args, **kwargs)
        if instance not in self.instrumented_apps:
            self.instrumented_apps.add(instance)
            self.get_instrumentor().instrument_app(instance, tracer_provider=self.tracer_provider)

            get_route_details = HeliosBaseHttpInstrumentor.import_attribute(self.MODULE_NAME, '_get_route_details')
            instance.add_middleware(HeliosAsgiMiddleware,
                                    tracer=self.tracer_provider.get_tracer(self.MODULE_NAME),
                                    get_span_details=get_route_details)
        return init_response
