from databricks_registry_webhooks.entities._webhooks_base_object import _WebhooksBaseObject


class TestWebhookResponse(_WebhooksBaseObject):
    """
    The response of a Registry Webhook Test.
    """

    def __init__(self, status_code, body):
        """
        :param status_code: The HTTP response status code from the test trigger invocation of the
                            Registry Webhook. For HTTP Registry Webhooks (Registry Webhooks with
                            HTTP URL Specs), this is the status code of the response to a request
                            sent to the supplied HTTPS URL. For Job Registry Webhooks (Registry
                            Webhooks with Job Specs), this is the status code of the response to an
                            HTTP request that is sent in order to run the associated Job.
        :param body: The HTTP response body from the test trigger invocation of the
                     Registry Webhook. For HTTP Registry Webhooks (Registry Webhooks with
                     HTTP URL Specs), this is the body of the response to a request sent to the
                     supplied HTTPS URL. For Job Registry Webhooks (Registry Webhooks with
                     Job Specs), this is the body of the response to an HTTP request that is sent
                     in order to run the associated Job.
        """
        self._status_code = status_code
        self._body = body

    @property
    def status_code(self):
        """
        The HTTP response status code from the test trigger invocation of the Registry Webhook. For
        HTTP Registry Webhooks (Registry Webhooks with HTTP URL Specs), this is the status code of
        the response to a request sent to the supplied HTTPS URL. For Job Registry Webhooks
        (Registry Webhooks with Job Specs), this is the status code of the response to an HTTP
        request that is sent in order to run the associated Job.
        """
        return self._status_code

    @property
    def body(self):
        """
        The HTTP response body from the test trigger invocation of the Registry Webhook. For HTTP
        Registry Webhooks (Registry Webhooks with HTTP URL Specs), this is the body of the response
        to a request sent to the supplied HTTPS URL. For Job Registry Webhooks (Registry Webhooks
        with Job Specs), this is the body of the response to an HTTP request that is sent in order
        to run the associated Job.
        """
        return self._body

    @classmethod
    def from_proto(cls, proto):
        return cls(
            status_code=proto.status_code,
            body=proto.body,
        )
