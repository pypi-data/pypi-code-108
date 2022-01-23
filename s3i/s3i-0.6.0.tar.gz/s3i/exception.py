import requests
import json
from schema import Schema, And, Or, Optional, SchemaError
import pika.exceptions as s3ib


class S3IError(Exception):
    def __init__(self, error_msg):
        Exception.__init__(self, error_msg)
        self.error_msg = error_msg

    def __str__(self):
        return str(self.error_msg)


class S3IDittoError(S3IError):
    def __init__(self, error_msg):
        S3IError.__init__(self, error_msg)
        self.error_msg = error_msg

    def __str__(self):
        if isinstance(self.error_msg, dict):
            return str(self.error_msg.get("message"))
        else:
            return str(self.error_msg)


class S3IDirectoryError(S3IDittoError):
    def __init__(self, error_msg):
        S3IDittoError.__init__(self, error_msg)
        self.error_msg = error_msg

    def __str__(self):
        def __str__(self):
            if isinstance(self.error_msg, dict):
                return str(self.error_msg.get("message"))
            else:
                return str(self.error_msg)


class S3IRepositoryError(S3IError):
    pass


class S3IIdentityProviderError(S3IError):
    def __init__(self, error_msg):
        Exception.__init__(self, error_msg)
        self.error_msg = error_msg

    def __str__(self):
        if isinstance(self.error_msg, dict):
            return str(self.error_msg.get("error"))
        else:
            return str(self.error_msg)


class S3IBMessageError(S3IError):
    def __init__(self, error_msg):
        S3IError.__init__(self, error_msg)
        self.error_msg = error_msg

    def __str__(self):
        return str(self.error_msg)


class S3IBrokerRESTError(S3IError):
    def __init__(self, error_msg):
        S3IError.__init__(self, error_msg)
        self.error_msg = error_msg

    def __str__(self):
        if isinstance(self.error_msg, dict):
            return str(self.error_msg.get("error"))
        elif isinstance(self.error_msg, list):
            for i in self.error_msg:
                return str(i.get("error"))


class S3IBrokerAMQPError(S3IError):
    def __init__(self, error_msg):
        S3IError.__init__(self, error_msg)
        self.error_msg = error_msg

    def __str__(self):
        if self.error_msg is None:
            return "unknown error"
        else:
            return str(self.error_msg)


def raise_error_from_s3ib_amqp(function, error, *args, **kwargs):
    try:
        r = function(*args, **kwargs)

    except (s3ib.AMQPChannelError, s3ib.AMQPConnectionError, s3ib.AMQPError,
            s3ib.AMQPHeartbeatTimeout, s3ib.AuthenticationError, s3ib.BodyTooLongError,
            s3ib.ChannelClosed, s3ib.ChannelClosedByBroker, s3ib.ChannelClosedByClient,
            s3ib.ChannelError, s3ib.ChannelWrongStateError, s3ib.ConnectionBlockedTimeout,
            s3ib.ConnectionClosed, s3ib.ConnectionClosedByBroker, s3ib.ConnectionClosedByClient,
            s3ib.ConnectionOpenAborted, s3ib.ConnectionWrongStateError, s3ib.ConsumerCancelled,
            s3ib.DuplicateConsumerTag, s3ib.DuplicateGetOkCallback, s3ib.IncompatibleProtocolError,
            s3ib.InvalidChannelNumber, s3ib.InvalidFieldTypeException, s3ib.InvalidFrameError,
            s3ib.MethodNotImplemented, s3ib.NackError, s3ib.NoFreeChannels, s3ib.ProbableAccessDeniedError,
            s3ib.ProbableAuthenticationError, s3ib.ProbableAccessDeniedError,
            s3ib.StreamLostError, s3ib.ShortStringTooLong, s3ib.ReentrancyError,
            s3ib.UnexpectedFrameError, s3ib.UnroutableError, s3ib.UnsupportedAMQPFieldException) as e:
        raise error(error_msg=e)
    if r is not None:
        return r


def raise_error_from_s3ib_msg(msg, error):
    user_msg_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i:" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers":  And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "userMessage"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            Optional("attachments"): And([{Optional(str): Or(str, bool, int, float, dict)}], lambda s: len(s) >= 0),
            "subject": And(str),
            "text": And(str)
        }, ignore_extra_keys=False
    )
    service_req_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "serviceRequest"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "serviceType": str,
            Optional("parameters"): And({Optional(str): Or(str, dict, int, float, bool, list)})
        }, ignore_extra_keys=False
    )
    service_reply_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "serviceReply"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "serviceType": str,
            Optional("results"): And({Optional(str): Or(str, dict, int, float, bool, list)})
        }, ignore_extra_keys=False
    )
    get_value_request_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "getValueRequest"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "attributePath": str
        }, ignore_extra_keys=False
    )
    get_value_reply_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "getValueReply"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "value": Or(str, dict, int, float, bool, list)
        }, ignore_extra_keys=False
    )
    set_value_request_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "setValueRequest"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "attributePath": str,
            "newValue": Or(str, dict, int, float, bool, list)
        }, ignore_extra_keys=False
    )
    set_value_reply_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "setValueReply"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "ok": bool
        }, ignore_extra_keys=False
    )
    create_attribute_request_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "createAttributeRequest"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "attributePath": str,
            "newValue": Or(str, int, float, dict, bool, list)
        }, ignore_extra_keys=False
    )
    create_attribute_reply_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "createAttributeReply"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "ok": bool
        }, ignore_extra_keys=False
    )
    delete_attribute_request_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "deleteAttributeRequest"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "attributePath": str,
        }, ignore_extra_keys=False
    )
    delete_attribute_reply_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "deleteAttributeReply"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "ok": bool
        }, ignore_extra_keys=False
    )

    custom_event_request_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "customEventRequest"),
            "filter": str,
            "attributePath": And([str], lambda s: len(s) > 0),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n)
        }, ignore_extra_keys=False
    )

    custom_event_reply_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "customEventReply"),
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            "status": Or(bool, str),
            "topic": str
        }, ignore_extra_keys=False
    )

    event_message_schema = Schema(
        {
            "sender": And(str, lambda n: "s3i" in n),
            "identifier": And(str, lambda n: "s3i:" in n),
            "receivers": And([And(str, lambda n: "s3i" in n)], lambda s: len(s) > 0),
            "messageType": And(str, lambda s: s == "eventMessage"),
            "topic": str,
            "timestamp": int,
            Optional("replyToEndpoint"): And(str, lambda n: "s3ib" in n),
            Optional("replyingToMessage"): And(str, lambda n: "s3i" in n),
            Optional("content"): And({Optional(str): Or(str, dict, int, float, bool, list)})
        }, ignore_extra_keys=False
    )

    try:
        if not isinstance(msg, dict):
            raise error(error_msg="S3IB Message should be formalized as dict")

        msg_type = msg.get("messageType")
        if msg_type == "userMessage":
            return user_msg_schema.validate(msg)
        elif msg_type == "serviceRequest":
            return service_req_schema.validate(msg)
        elif msg_type == "serviceReply":
            return service_reply_schema.validate(msg)
        elif msg_type == "getValueRequest":
            return get_value_request_schema.validate(msg)
        elif msg_type == "getValueReply":
            return get_value_reply_schema.validate(msg)
        elif msg_type == "setValueRequest":
            return set_value_request_schema.validate(msg)
        elif msg_type == "setValueReply":
            return set_value_reply_schema.validate(msg)
        elif msg_type == "createAttributeRequest":
            return create_attribute_request_schema.validate(msg)
        elif msg_type == "createAttributeReply":
            return create_attribute_reply_schema.validate(msg)
        elif msg_type == "deleteAttributeRequest":
            return delete_attribute_request_schema.validate(msg)
        elif msg_type == "deleteAttributeReply":
            return delete_attribute_reply_schema.validate(msg)
        elif msg_type == "customEventRequest":
            return custom_event_request_schema.validate(msg)
        elif msg_type == "customEventReply":
            return custom_event_reply_schema.validate(msg)
        elif msg_type == "eventMessage":
            return event_message_schema.validate(msg)
        else:
            error_msg = "Invalid type of S3I-B messages"
            raise error(error_msg=error_msg)

    except SchemaError as e:
        raise error(error_msg=e.autos)


def raise_error_from_response(response, error, expected_response_code):
    if response.status_code == expected_response_code:
        if expected_response_code == requests.codes.no_content:
            return {}
        else:
            try:
                return response.json()
            except json.decoder.JSONDecodeError:
                return {}
    else:
        try:
            error_msg = response.json()
        except json.decoder.JSONDecodeError:
            raise RuntimeError(response.text)
    raise error(error_msg=error_msg)
