from databricks_registry_webhooks.entities._webhooks_base_object import _WebhooksBaseObject
from databricks_registry_webhooks.protos.webhooks_pb2 import HttpUrlSpec as ProtoHttpUrlSpec


class HttpUrlSpec(_WebhooksBaseObject):
    """
    Attributes (e.g. URL) of an HTTPS request for a Registry Webhook to send when one or more
    associated events occurs.
    """

    def __init__(self, url, secret, authorization=None, enable_ssl_verification=True):
        """
        :param url: HTTPS URL to which an associated Registry Webhook sends event messages.
        :param secret: Shared secret string for validating the authenticity of an associated
                       Registry Webhook event message. The secret is not returned when querying
                       Registry Webhooks.
        :param authorization: Optional `Authorization` header for validating the authenticity
                              of an associated Registry Webhook event message. If specified, should
                              be formatted as `<auth type> <credentials>`. If unspecified, an
                              `Authorization` header is not be included in event message requests.
                              The `Authorization` header is not returned when querying Registry
                              Webhooks.
        :param enable_ssl_verification: If `True`, an associated Registry Webhook performs SSL
                                        certificate validation on the specified `url` when sending
                                        event messages. If `False`, SSL certificate validation is
                                        not performed.
        """
        self._url = url
        self._secret = secret
        self._authorization = authorization
        self._enable_ssl_verification = enable_ssl_verification

    @property
    def url(self):
        """
        HTTPS URL to which an associated Registry Webhook sends event messages.
        """
        return self._url

    @property
    def secret(self):
        """
        Shared secret string for validating the authenticity of an associated Registry Webhook
        event message. The secret is not returned when querying Registry Webhooks.
        """
        return self._secret

    @property
    def authorization(self):
        """
        Optional `Authorization` header for validating the authenticity of an associated Registry
        Webhook event message.
        """
        return self._authorization

    @property
    def enable_ssl_verification(self):
        """
        If `True`, an associated Registry Webhook performs SSL certificate validation on the
        specified `url` when sending event messages. If `False`, SSL certificate validation is
        not performed.
        """
        return self._enable_ssl_verification

    def to_proto(self):
        proto = ProtoHttpUrlSpec()
        proto.url = self.url
        proto.secret = self.secret
        proto.enable_ssl_verification = self.enable_ssl_verification
        if self.authorization is not None:
            proto.authorization = self.authorization
        return proto

    @classmethod
    def from_proto(cls, proto):
        authorization = proto.authorization
        # If the authorization is a falsy string, this means that the field was not
        # set on the proto (i.e. is empty) and should be represented as `None`
        if not authorization:
            authorization = None

        return cls(
            url=proto.url,
            secret=proto.secret,
            authorization=authorization,
            enable_ssl_verification=proto.enable_ssl_verification,
        )
