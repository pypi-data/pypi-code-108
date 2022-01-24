import json

from opentelemetry.semconv.trace import SpanAttributes

from helios.instrumentation.botocore.consts import AwsParam, AwsService, AwsAttribute, MAX_PAYLOAD_SIZE


class DynamoDBInstrumentor(object):

    def __init__(self):
        pass

    def request_hook(self, span, operation_name, api_params):
        if AwsParam.TABLE_NAME in api_params:
            table_name = api_params[AwsParam.TABLE_NAME]
            span.set_attribute(SpanAttributes.DB_NAME, table_name) if table_name else None
        db_statement = dict(api_params)
        db_statement['operation'] = operation_name
        span.set_attributes({
            SpanAttributes.DB_SYSTEM: AwsService.DYNAMO_DB,
            SpanAttributes.DB_STATEMENT: json.dumps(db_statement)
        })

    def response_hook(self, span, operation_name, result):
        query_result = json.dumps(result, default=str)
        if len(query_result) < MAX_PAYLOAD_SIZE:
            span.set_attribute(AwsAttribute.DB_QUERY_RESULT, query_result)
