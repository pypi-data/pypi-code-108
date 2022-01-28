#
# jomiel
#
# Copyright
#  2019-2021 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""
from re import compile as rxc
from traceback import format_exc

import jomiel_messages.protobuf.v1beta1.status_pb2 as Status
from google.protobuf.message import DecodeError
from jomiel.error import InvalidInputError
from jomiel.error import NoParserError
from jomiel.error import ParseError
from jomiel_messages.protobuf.v1beta1.message_pb2 import Response
from requests.exceptions import RequestException


class ResponseBuilder:
    """Builds a new Response (protobuf) message which is sent back to to
    client.

    Determines the message content based on the exception passed to the
    class.

    Args:
        error (obj): an exception that occurred while processing the
            input URI (or leave None, if none occurred)

    Attributes:
        response (obj): the created Response object

    """

    __slots__ = ["response"]

    def __init__(self, error=None):
        self.response = Response()
        self.init(
            "Not an error",
            Status.STATUS_CODE_OK,
            Status.ERROR_CODE_UNSPECIFIED,
        )
        if error:
            self.determine(error)

    def determine(self, error):
        """Determine error, and set the response values to indicates
        this.

        Args:
            error (obj): the raised exception

        """
        error_type = type(error)

        if error_type == ParseError:
            self.parse_failed(error)
        elif error_type == NoParserError:
            self.handler_not_found(error)
        elif (
            error_type == InvalidInputError or error_type == DecodeError
        ):
            self.invalid_input_given(error)
        else:
            if not self.is_requests_error(error, error_type):
                self.fail_with_traceback()

    def init(self, msg, status, error, http=200):
        """Initialize the response with the given values.

        Args:
            msg (string): explanation of the error
            status (int): status code (see status.proto)
            error (int): error code (see status.proto)
            http (int): HTTP code (default is 200)

        """
        self.response.status.http.code = http
        self.response.status.message = msg
        self.response.status.code = status
        self.response.status.error = error
        return True

    def parse_failed(self, error):
        """System raised ParseError, initalize response accordingly."""
        self.init(
            error.message,
            Status.STATUS_CODE_INTERNAL_SERVER,
            Status.ERROR_CODE_PARSE,
        )

    def handler_not_found(self, error):
        """System raised NoParserError, initalize response accordingly."""
        self.init(
            error.message,
            Status.STATUS_CODE_NOT_IMPLEMENTED,
            Status.ERROR_CODE_NO_PARSER,
        )

    def invalid_input_given(self, error):
        """System raised InvalidInputError, e.g.

        - failed to decode the incoming Inquiry message (DecodeError was
          raised because of an invalid or otherwise corrupted message)

        - client sent unexpected input (e.g. input URI was not an URI)

        """
        self.init(
            error.message if hasattr(error, "message") else str(error),
            Status.STATUS_CODE_BAD_REQUEST,
            Status.ERROR_CODE_INVALID_INPUT,
        )

    def is_requests_error(self, error, error_type):
        """Handle Requests error (if any)

        If Requests error occurred, initialize response accordingly,
        otherwise fall through.

        Args:
            error (obj): the raised exception
            error_type (obj): the type of the exception

        """
        if issubclass(error_type, RequestException):

            def get_http_code():
                """Return HTTP code from the HTTP header."""
                regex = rxc(r"^(\d{3}) Server Error:")
                result = regex.match(message)
                return result.group(1) if result else 200

            message = str(error)
            code = get_http_code()

            return self.init(
                message,
                Status.STATUS_CODE_INTERNAL_SERVER,
                Status.ERROR_CODE_HTTP,
                code,
            )
        return False

    def fail_with_traceback(self):
        """Pass the Python stack traceback to the client."""
        self.init(
            format_exc(),
            Status.STATUS_CODE_INTERNAL_SERVER,
            Status.ERROR_CODE_UNKNOWN_SEE_MESSAGE,
        )
