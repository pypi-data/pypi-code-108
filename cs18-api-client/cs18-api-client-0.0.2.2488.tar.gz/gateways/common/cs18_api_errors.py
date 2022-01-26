"""
Container for Error classes used in cs18-api-client
"""
import json

from requests import Response
from typing import List


class Error:
    def __init__(self, json_data: dict):
        self.code = json_data["code"]
        self.name = json_data["name"]
        self.message = json_data["message"]

    def __eq__(self, other):
        if isinstance(other, Error):
            return (
                self.code == other.code
                and self.name == other.name
                and self.message == other.message
            )
        return False


class SandboxError:
    def __init__(self, time: str, code: str, message: str):
        self.message = message
        self.code = code
        self.time = time


class GeneralHttpException(Exception):
    """
    General HTTP Exception.
    Loads additional information we want to be passed with the error.
    """

    def __init__(self, response: Response):
        super(GeneralHttpException, self).__init__(
            "Request to '{url}' ended with wrong status_code '{status_code}'. "
            "Message {message}. "
            "TraceID: {trace}.".format(
                url=response.url,
                status_code=response.status_code,
                message=response.text,
                trace=response.headers.get("X-Correlation-ID"),
            )
        )
        self.status_code = response.status_code
        self.trace_id = response.headers.get("X-Correlation-ID")


class DevboxHttpException(GeneralHttpException):
    """
    Devbox HTTP Exception
    """

    def __init__(self, response: Response):
        super(DevboxHttpException, self).__init__(response)
        self.errors = [Error(x) for x in json.loads(response.text).get("errors")]


class UnauthorizedException(Exception):
    def __init__(
            self,
            credentials: dict
    ):
        super(UnauthorizedException, self).__init__(
            "Failed to authenticate Colony client. Should provide either an access_token or both email and password."
            "Provided credentials: {credentials}".format(credentials=credentials)
        )


class MaxRetriesException(Exception):
    def __init__(self, max_retries, subject):
        super(MaxRetriesException, self).__init__(
            f"Timeout: {max_retries} attempts were exhausted waiting for '{subject}'"
        )


class SandboxEndingFailed(Exception):
    def __init__(self, sandbox_id: str, ending_errors: List[SandboxError]):
        super(SandboxEndingFailed, self).__init__(
            "Sandbox '{SANDBOX_ID}' failed to end with those errors: {ERRORS}".format(
                SANDBOX_ID=sandbox_id,
                ERRORS=", ".join("{CODE} ({MESSAGE})".format(CODE=error.code,
                                                             MESSAGE=error.message)
                                 for error in ending_errors))
        )


class SandboxNotFound(Exception):
    pass
