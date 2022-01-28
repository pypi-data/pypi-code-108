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
from binascii import hexlify
from logging import DEBUG

from google.protobuf.message import DecodeError
from jomiel.cache import opts
from jomiel.dispatcher.media import script_dispatcher
from jomiel.error import InvalidInputError
from jomiel.log import lg
from jomiel.log import log_sanitize_string
from jomiel.subsys.broker.response import ResponseBuilder
from jomiel_comm.formatter import to_json
from jomiel_kore.app import exit_error
from jomiel_messages.protobuf.v1beta1.message_pb2 import Inquiry
from jomiel_messages.protobuf.v1beta1.message_pb2 import Response
from validators import url as is_url
from zmq import Context
from zmq import ContextTerminated
from zmq import REP
from zmq import ZMQError


class Worker:
    """The worker class.

    Args:
        worker_id (int): the worker ID

    """

    __slots__ = ["worker_id", "context", "socket", "dealer_endpoint"]

    def __init__(self, worker_id):
        self.dealer_endpoint = opts.broker_dealer_endpoint
        (self.context, self.worker_id) = (Context.instance(), worker_id)
        self.socket = self.new_socket()

    def new_socket(self):
        """Returns a new socket that is connected to the broker (via the
        dealer endpoint).

        """
        sck = self.context.socket(REP)
        try:
            sck.connect(self.dealer_endpoint)
        except ZMQError as error:
            self.log_error(f"{error} ({self.dealer_endpoint})")
            exit_error()
        self.log("connected to <%s>" % self.dealer_endpoint)
        return sck

    def renew_socket(self):
        """Renews the zmq socket.

        Disconnects and closes the existing socket connection (to the
        broker, via the dealer endpoint, and reconnects to the dealer
        using the same endpoint.

        """
        self.socket.disconnect(self.dealer_endpoint)
        self.socket.close()
        self.socket = self.new_socket()

    def io_loop(self):
        """The I/O loop."""
        while True:
            try:
                self.log("awaiting")
                self.message_receive()
            except DecodeError as error:
                self.log_error(
                    "received invalid message: %s" % (error),
                )
                self.message_send(ResponseBuilder(error).response)
                self.renew_socket()
            finally:
                self.log("reset")

    def _log(self, text, msgtype):
        """Write new log event to the logger."""
        logger = getattr(lg(), msgtype)
        logger(
            "subsystem/broker<worker#%03d>: %s",
            self.worker_id,
            text,
        )

    def log(self, text):
        """Write an "debug" event to the logger."""
        self._log(text, "debug")

    def log_error(self, text):
        """Write an "error" event to the logger."""
        self._log(text, "error")

    def run(self):
        """Runs the worker."""
        try:
            self.io_loop()
        except ContextTerminated as msg:
            self.log(msg)
        except KeyboardInterrupt:
            self.log("interrupted")
        finally:
            self.socket.close()
            self.log("exit")

    def message_dump(self, logtext, message):
        """Dump the message details in JSON to the logger

        Ignored unless application uses the debug level.

        Args:
            logtext (string): log entry text to write
            message (obj): the message to log

        """
        if lg().level <= DEBUG:
            json = to_json(message, minified=opts.debug_minify_json)
            self.log(logtext % log_sanitize_string(json))

    def message_log_serialized(self, prefix, message):
        """Logs the given serialized message in hex format.

        Args:
            message (obj): Message to be logged

        """
        if lg().level <= DEBUG:
            _len = len(message)
            _hex = hexlify(bytearray(message))
            self.log(
                "<%s:serialized> [%s] %s"
                % (prefix, _len, log_sanitize_string(_hex)),
            )

    def message_send(self, response):
        """Sends a response message back to the client.

        Args:
            response (obj): Response message to send

        """
        serialized_response = Response.SerializeToString(response)
        self.message_log_serialized("send", serialized_response)
        self.socket.send(serialized_response)
        self.message_dump("sent: %s", response)

    def message_receive(self):
        """Awaits for an inquiry request from a client."""
        recvd_data = self.socket.recv()
        inquiry = Inquiry()

        self.message_log_serialized("recvd", recvd_data)

        inquiry.ParseFromString(recvd_data)
        self.message_dump("received: %s", inquiry)

        if inquiry.WhichOneof("inquiry") == "media":
            self.handle_media_inquiry(inquiry.media)
        else:
            raise DecodeError("Invalid oneof field in Inquiry")

    def handle_media_inquiry(self, inquiry):
        """Handles the incoming inquiry requests."""

        def match_handler():
            """Matches the given input URI to a script.

            Returns:
                obj: A subclass of PluginMediaParser

                    The object data consists of parsed meta data as
                    returned for the input URI.

            """
            return script_dispatcher(inquiry.input_uri)

        def validate_input_uri():
            """Validate the input URI unless configured to skip this."""
            if opts.broker_input_allow_any:
                return

            if not is_url(inquiry.input_uri):
                raise InvalidInputError(
                    "Invalid input URI value given <%s>"
                    % inquiry.input_uri,
                )

        try:
            validate_input_uri()
            handler = match_handler()
            self.message_send(handler.response)
        except Exception as error:
            self.message_send(ResponseBuilder(error).response)


def worker_new(worker_id):
    """Creates a new worker objecta

    Args:
        worker_id (int): the worker ID

    """
    Worker(worker_id).run()


# vim: set ts=4 sw=4 tw=72 expandtab:
