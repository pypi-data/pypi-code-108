from helios.instrumentation.botocore.consts import AwsOperation, AwsParam, AwsAttribute


class SESInstrumentor(object):

    def __init__(self):
        pass

    def request_hook(self, span, operation_name, api_params):
        if operation_name != AwsOperation.SEND_EMAIL:
            return
        destination = api_params.get(AwsParam.DESTINATION, dict())
        message = api_params.get(AwsParam.MESSAGE, dict())
        body = message.get(AwsParam.BODY, dict())

        attributes = {
            AwsAttribute.SES_SENDER: api_params.get(AwsParam.SOURCE),
            AwsAttribute.SES_RECIPIENTS: destination.get(AwsParam.TO_ADDRESSES),
            AwsAttribute.SES_CC_RECIPIENTS: destination.get(AwsParam.CC_ADDRESSES),
            AwsAttribute.SES_BCC_RECIPIENTS: destination.get(AwsParam.BCC_ADDRESSES),
            AwsAttribute.SES_SUBJECT: message.get(AwsParam.SUBJECT, dict()).get(AwsParam.DATA),
            AwsAttribute.SES_HTML_BODY: body.get(AwsParam.HTML, dict()).get(AwsParam.DATA),
            AwsAttribute.SES_TEXT_BODY: body.get(AwsParam.TEXT, dict()).get(AwsParam.DATA)
        }
        attributes = {k: v for k, v in attributes.items() if v is not None}
        span.set_attributes(attributes)

    def response_hook(self, span, operation_name, result):
        pass
