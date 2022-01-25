"""
send messages to single contact or group
"""


from dataclasses import dataclass, field
from os import remove as os_remove
from typing import List, Optional
from uuid import uuid4

from sanic import Blueprint, Sanic
from sanic.log import logger
from sanic.response import json
from sanic_ext import openapi, validate
from signal_cli_dbus_rest_api.dataclasses import Error, ResponseTimestamp
from signal_cli_dbus_rest_api.lib.dbus import SignalCLIDBus
from signal_cli_dbus_rest_api.lib.helper import (get_groupid_as_bytes,
                                                 is_phone_number,
                                                 do_decode_attachments)

send_v1 = Blueprint("send_v1", url_prefix="/send")
send_v2 = Blueprint("send_v2", url_prefix="/send")


def do_send_message(
    recipients: list, number: str, message: str, attachments: list, version: int = 2
):
    """
    send message
    """
    try:
        dbus = SignalCLIDBus(number=number)
        real_recipients = is_phone_number(
            recipients=recipients, dbus_connection=dbus.dbusconn
        )
        method = dbus.dbusconn.sendMessage
        signature = "sasas"
        if not real_recipients:
            real_recipients = get_groupid_as_bytes(
                recipient=recipients[0], version=version
            )
            method = dbus.dbusconn.sendGroupMessage
            signature = "sasay"
        if not real_recipients:
            return (
                {
                    "error": f"{recipients} is neither a phone number nor a valid group id"
                },
                400,
            )
        timestamp = method(message, attachments, real_recipients, signature=signature)
        return {"timestamp": str(timestamp)}, 201
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, 'message', repr(err))
        logger.error(error)
        return {"error": error}, 400
    finally:
        for attachment in attachments:
            os_remove(attachment)


@dataclass
class SendV2PostParams:
    """
    SendV2PostParams
    """

    recipients: List[str]
    message: str
    number: Optional[str] = field(default_factory=str)
    base64_attachments: Optional[List[str]] = field(default_factory=list)


@send_v2.post("/", version=2)
@openapi.tag("Messages")
@openapi.body({"application/json": SendV2PostParams}, required=True)
@openapi.response(201, {"application/json": ResponseTimestamp}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description(
    (
        "Send a signal message."
        "`number` can be ommited if API is running w/ `SIGNAL_CLI_DBUS_REST_API_ACCOUNT`"
    )
)
@validate(SendV2PostParams)
async def send_v2_post(request, body: SendV2PostParams):  # pylint: disable=unused-argument
    """
    Send a signal message.
    """
    decoded_attachments = []
    app = Sanic.get_app()
    recipients = body.recipients
    try:
        number = body.number or app.config.ACCOUNT
    except AttributeError:
        return json(
            {
                "error": "number missing in request and SIGNAL_CLI_DBUS_REST_API_ACCOUNT unset "
            },
            400,
        )
    attachments = body.base64_attachments
    uuid = str(uuid4())
    if isinstance(attachments, list):
        decoded_attachments = do_decode_attachments(attachments, uuid)
    return_message, return_code = do_send_message(
        recipients, number, body.message, decoded_attachments
    )
    return json(return_message, return_code)


@dataclass
class SendV1PostParams:
    """
    SendV1PostParams
    """

    message: str
    number: Optional[str] = field(default_factory=str)
    base64_attachments: List[str] = field(default_factory=list)


@send_v1.post("/<recipient:path>", version=1)
@openapi.tag("Messages")
@openapi.parameter("recipient", str, required=True, location="path")
@openapi.body({"application/json": SendV1PostParams}, required=True)
@openapi.response(201, {"application/json": ResponseTimestamp}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description(
    (
        "Send a signal message."
        "`number` can be ommited if API is running w/ `SIGNAL_CLI_DBUS_REST_API_ACCOUNT`"
    )
)
@validate(SendV1PostParams)
async def send_v1_post(request, recipient, body: SendV1PostParams):  # pylint: disable=unused-argument
    """
    Send a signal message.
    """
    decoded_attachments = []
    app = Sanic.get_app()
    try:
        number = body.number or app.config.ACCOUNT
    except AttributeError:
        return json(
            {
                "error": "number missing in request and SIGNAL_CLI_DBUS_REST_API_ACCOUNT unset "
            },
            400,
        )
    attachments = body.base64_attachments
    uuid = str(uuid4())
    if isinstance(attachments, list):
        decoded_attachments = do_decode_attachments(attachments, uuid)
    return_message, return_code = do_send_message(
        [recipient], number, body.message, decoded_attachments, version=1
    )
    return json(return_message, return_code)
