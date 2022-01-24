from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.botocore.consts import AwsParam, AwsAttribute, MAX_PAYLOAD_SIZE, AwsService


class S3Instrumentor(object):

    def __init__(self):
        pass

    def request_hook(self, span, operation_name, api_params):
        bucket = api_params.get(AwsParam.BUCKET)
        key = api_params.get(AwsParam.KEY)
        value = api_params.get(AwsParam.BODY)

        attributes = dict({
            SpanAttributes.DB_SYSTEM: AwsService.S3
        })
        if bucket:
            attributes[AwsAttribute.S3_BUCKET] = bucket
        if key:
            attributes[AwsAttribute.S3_KEY] = key
        if value:
            value = value.decode()
            if len(value) < MAX_PAYLOAD_SIZE:
                attributes[AwsAttribute.DB_QUERY_RESULT] = value

        span.set_attributes(attributes)

    def response_hook(self, span, operation_name, result):
        body_stream = result.get(AwsParam.BODY)
        attributes = dict({
            SpanAttributes.DB_SYSTEM: AwsService.S3
        })
        if body_stream:
            value = body_stream.read()
            if len(value) < MAX_PAYLOAD_SIZE:
                attributes[AwsAttribute.DB_QUERY_RESULT] = value
        span.set_attributes(attributes)
