from databricks_registry_webhooks.protos.databricks_pb2 import ErrorCode, INTERNAL_ERROR


class RegistryWebhooksException(Exception):
    """
    Generic exception thrown to surface failure information about external-facing operations.
    The error message associated with this exception may be exposed to clients in HTTP responses
    for debugging purposes. If the error text is sensitive, raise a generic `Exception` object
    instead.
    """

    def __init__(self, message, error_code=INTERNAL_ERROR):
        """
        :param message: The message describing the error that occured. This will be included in the
                        exception's serialized JSON representation.
        :param error_code: An appropriate error code for the error that occured; it will be included
                           in the exception's serialized JSON representation. This should be one of
                           the codes listed in the `databricks_registry_webhooks.protos.databricks_pb2` proto.
        """
        try:
            self.error_code = ErrorCode.Name(error_code)
        except (ValueError, TypeError):
            self.error_code = ErrorCode.Name(INTERNAL_ERROR)
        self.message = message
        super().__init__(message)


class RestException(RegistryWebhooksException):
    """Exception thrown on non 200-level responses from the REST API"""

    def __init__(self, json):
        self.error_code = json.get("error_code", ErrorCode.Name(INTERNAL_ERROR))
        self.message = "%s: %s" % (
            self.error_code,
            json["message"] if "message" in json else "Response: " + str(json),
        )
        super().__init__(self.message, ErrorCode.Value(self.error_code))
        self.json = json
