from opentelemetry.propagate import inject
from opentelemetry.propagators import textmap
from opentelemetry.trace import set_span_in_context
from opentelemetry.semconv.trace import SpanAttributes, MessagingDestinationKindValues

from helios.instrumentation.botocore.consts import AwsAttribute, AwsOperation, AwsParam, AwsService


class SNSContextSetter(textmap.Setter):
    def set(self, carrier: textmap.CarrierT, key: str, value: str) -> None:
        if carrier and key and value:
            carrier[key] = {
                AwsParam.STRING_VALUE: value,
                AwsParam.DATA_TYPE: 'String'
            }


class SNSInstrumentor(object):

    def __init__(self):
        pass

    def request_hook(self, span, operation_name, api_params):
        if operation_name.lower() != AwsOperation.PUBLISH.lower():
            return

        attributes = {
            SpanAttributes.MESSAGING_SYSTEM: AwsService.SNS,
            SpanAttributes.MESSAGING_DESTINATION: api_params.get(AwsParam.TOPIC_ARN),
            SpanAttributes.MESSAGING_DESTINATION_KIND: MessagingDestinationKindValues.TOPIC.value,
            SpanAttributes.MESSAGING_OPERATION: AwsOperation.SEND,
            AwsAttribute.MESSAGING_PAYLOAD: api_params.get(AwsParam.MESSAGE),
        }
        attributes = {k: v for k, v in attributes.items() if v is not None}
        span.set_attributes(attributes)
        message_attributes = api_params.get(AwsParam.MESSAGE_ATTRIBUTES, dict())
        inject(message_attributes, context=set_span_in_context(span), setter=SNSContextSetter())
        api_params[AwsParam.MESSAGE_ATTRIBUTES] = message_attributes

    def response_hook(self, span, operation_name, result):
        pass
