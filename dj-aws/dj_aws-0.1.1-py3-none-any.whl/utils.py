from djstarter import utils as core_utils


class ClientErrorResponse(core_utils.SerializerMixin):
    class Error:
        def __init__(self, data):
            self.code = data['Code']
            self.message = data['Message']

    class ResponseMetadata:
        def __init__(self, data):
            self.host_id = data.get('HostId')
            self.http_headers = data['HTTPHeaders']
            self.http_status_code = data['HTTPStatusCode']
            self.request_id = data['RequestId']
            self.retry_attempts = data['RetryAttempts']

    def __init__(self, data):
        self.error = self.Error(data['Error'])
        self.message = data.get('message')
        self.response_metadata = self.ResponseMetadata(data['ResponseMetadata'])

    @property
    def exception_class(self):
        return self.error.code
