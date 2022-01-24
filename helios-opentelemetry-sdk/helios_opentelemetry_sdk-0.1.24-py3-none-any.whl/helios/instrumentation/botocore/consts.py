from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from helios.instrumentation import HeliosBaseInstrumentor

MAX_PAYLOAD_SIZE = HeliosBaseInstrumentor.MAX_PAYLOAD_SIZE

INJECTED_MESSAGE_ATTRIBUTE_NAMES = [
    W3CBaggagePropagator._BAGGAGE_HEADER_NAME,
    TraceContextTextMapPropagator._TRACEPARENT_HEADER_NAME,
    TraceContextTextMapPropagator._TRACESTATE_HEADER_NAME
]


class AwsAttribute:
    AWS_SERVICE = 'aws.service_id'
    MESSAGING_PAYLOAD = 'messaging.payload'
    SES_SUBJECT = 'aws.ses.subject'
    SES_HTML_BODY = 'aws.ses.body.html'
    SES_TEXT_BODY = 'aws.ses.body'
    SES_SENDER = 'aws.ses.sender'
    SES_RECIPIENTS = 'aws.ses.recipients'
    SES_CC_RECIPIENTS = 'aws.ses.recipients.cc'
    SES_BCC_RECIPIENTS = 'aws.ses.recipients.bcc'
    S3_BUCKET = 'aws.s3.bucket'
    S3_KEY = 'aws.s3.key'
    DB_QUERY_RESULT = 'db.query_result'


class AwsParam:
    BUCKET = 'Bucket'
    KEY = 'Key'
    DESTINATION = 'Destination'
    HTML = 'Html'
    DATA = 'Data'
    TO_ADDRESSES = 'ToAddresses'
    CC_ADDRESSES = 'CcAddresses'
    BCC_ADDRESSES = 'BccAddresses'
    SOURCE = 'Source'
    TEXT = 'Text'
    TOPIC_ARN = 'TopicArn'
    MESSAGE = 'Message'
    MESSAGES = 'Messages'
    SUBJECT = 'Subject'
    BODY = 'Body'
    QUEUE_NAME = 'QueueName'
    QUEUE_URL = 'QueueUrl'
    ENTRIES = 'Entries'
    MESSAGE_BODY = 'MessageBody'
    MESSAGE_ATTRIBUTES = 'MessageAttributes'
    MESSAGE_ATTRIBUTE_NAMES = 'MessageAttributeNames'
    STRING_VALUE = 'StringValue'
    DATA_TYPE = 'DataType'
    TABLE_NAME = 'TableName'


class AwsOperation:
    PUBLISH = 'publish'
    SEND = 'send'
    SEND_MESSAGE = 'SendMessage'
    SEND_MESSAGE_BATCH = 'SendMessageBatch'
    RECEIVE_MESSAGE = 'ReceiveMessage'
    SEND_EMAIL = 'SendEmail'


class AwsService:
    S3 = 'aws.s3'
    SNS = 'aws.sns'
    SQS = 'aws.sqs'
    DYNAMO_DB = 'aws.dynamodb'
