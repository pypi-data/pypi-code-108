import textwrap

import zerohash


class ZerohashError(Exception):
    def __init__(
        self,
        messages=None,
        errors=None,
        body=None,
        status_code=None,
        headers=None,
    ):
        # self._messages = messages
        # self.errors = errors
        if headers is None:
            headers = {}
        if body is None:
            body = {}
        self._body = body
        self.status_code = status_code
        self.headers = headers or {}
        self.request_id = self.headers.get("X-Request-Id", None)

        self.messages = self.construct_messages()
        self.errors = self.construct_errors()

    def construct_messages(self):

        # if self._body is None or "messages" not in self._body:
        #     return self._messages

        # messages = getattr(self._body, "messages", self._messages)
        if isinstance(self._body, str):
            return [self._body]
        messages = self._body.get("messages", [])
        if isinstance(messages, str):
            return [messages]
        return messages

    def construct_errors(self):

        errors = []

        # Append an error object for each  message
        for msg in self.messages:
            errors.append(
                zerohash.resources.error_object.ErrorObject.construct_from(
                    dict(message=msg), zerohash.credentials
                )
            )

        # Now append an error object for each item in "errors" or the string in "error" in the body
        for msg in self._body.get("errors", []):
            errors.append(
                zerohash.resources.error_object.ErrorObject.construct_from(
                    dict(message=msg), zerohash.credentials
                )
            )
        # if hasattr(self._body, "error"):
        if self._body.get("error"):
            errors.append(
                zerohash.resources.error_object.ErrorObject.construct_from(
                    dict(message=self._body["error"]), zerohash.credentials
                )
            )
        return errors

    def __str__(self):
        msg = self.messages
        for e in self.errors:
            if isinstance(e, dict):
                msg.append(e.get("message", e))
        if self.request_id:
            return f"Request {self.request_id}: {msg}"

        else:
            return "Unknown Zero Hash Error"


class APIError(ZerohashError):
    """Used for 5XX errors received from the Zero Hash API"""

    pass


class ClientError(ZerohashError):
    """Used for 4XX errors received from the Zero Hash API"""

    pass


class UnknownError(ZerohashError):
    pass


class AuthenticationError(ZerohashError):
    pass


class MalformedAuthorizationError(ZerohashError):
    pass


class APIConnectionError(ZerohashError):
    def __init__(
        self,
        message_body,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
        code=None,
        should_retry=False,
    ):
        message_body = textwrap.fill(message_body)
        super().__init__(message_body, http_body, http_status, headers, code)
        self.should_retry = should_retry
