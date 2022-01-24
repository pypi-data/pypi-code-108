from helios.instrumentation.base import HeliosBaseInstrumentor
from helios.instrumentation.botocore.consts import AwsAttribute
from helios.instrumentation.botocore.dynamodb import DynamoDBInstrumentor
from helios.instrumentation.botocore.s3 import S3Instrumentor
from helios.instrumentation.botocore.ses import SESInstrumentor
from helios.instrumentation.botocore.sns import SNSInstrumentor
from helios.instrumentation.botocore.sqs import SQSInstrumentor
from helios.instrumentation.urllib3 import HeliosUrllib3Instrumentor

from opentelemetry import context


class HeliosBotocoreInstrumentor(HeliosBaseInstrumentor):
    MODULE_NAME = 'opentelemetry.instrumentation.botocore'
    INSTRUMENTOR_NAME = 'BotocoreInstrumentor'

    def __init__(self):
        super().__init__(self.MODULE_NAME, self.INSTRUMENTOR_NAME)
        self.services = dict()
        self.context_token = None

    def instrument(self, tracer_provider=None):

        if self.get_instrumentor() is None:
            return

        self.services.update({
            'dynamodb': DynamoDBInstrumentor(),
            's3': S3Instrumentor(),
            'ses': SESInstrumentor(),
            'sns': SNSInstrumentor(),
            'sqs': SQSInstrumentor(tracer_provider=tracer_provider),
        })

        self.get_instrumentor().instrument(tracer_provider=tracer_provider,
                                           response_hook=self.response_hook,
                                           request_hook=self.request_hook)

    def request_hook(self, span, service_name, operation_name, api_params):

        if not span or not span.is_recording():
            return

        # botocore uses urllib3, which is also instrumented.
        # we add urllib3's http key to the context, which is later checked on and suppresses further instrumentations.
        suppress_key = (HeliosBaseInstrumentor
            .import_attribute(HeliosUrllib3Instrumentor.MODULE_NAME, '_SUPPRESS_HTTP_INSTRUMENTATION_KEY'))
        if suppress_key:
            self.context_token = context.attach(context.set_value(suppress_key, True))

        span.set_attribute(AwsAttribute.AWS_SERVICE, service_name)
        service_instrumentor = self.services.get(service_name)
        if service_instrumentor is not None:
            if callable(service_instrumentor.request_hook):
                return service_instrumentor.request_hook(span, operation_name, api_params)

    def response_hook(self, span, service_name, operation_name, result):
        if not span or not span.is_recording():
            return

        if self.context_token:
            context.detach(self.context_token)

        span.set_attribute(AwsAttribute.AWS_SERVICE, service_name)
        service_instrumentor = self.services.get(service_name)
        if service_instrumentor is not None:
            if callable(service_instrumentor.response_hook):
                return service_instrumentor.response_hook(span, operation_name, result)
