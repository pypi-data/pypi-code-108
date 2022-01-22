"""
send message reactions to single contact
"""


from typing import Optional, List
from dataclasses import dataclass, field
from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic_ext import openapi, validate
from signal_cli_dbus_rest_api.lib.dbus import SignalCLIDBus
from signal_cli_dbus_rest_api.lib.helper import get_groupid_as_bytes, is_phone_number
from signal_cli_dbus_rest_api.dataclasses import Error

reactions_v1 = Blueprint("reactions_v1", url_prefix="/reactions")


def send_reaction(
    number: str,
    reaction: str,
    remove: bool,
    recipients: str,
    target_author: str,
    timestamp: int,
):  # pylint: disable=too-many-arguments
    """
    send reaction
    """
    try:
        if not isinstance(recipients, list):
            recipients = [recipients]
        dbus = SignalCLIDBus(number=number)
        real_recipients = is_phone_number(
            recipients=recipients, dbus_connection=dbus.dbusconn
        )
        method = dbus.dbusconn.sendMessageReaction
        signature = "sbsxas"
        if not real_recipients:
            real_recipients = get_groupid_as_bytes(recipient=recipients[0])
            method = dbus.dbusconn.sendGroupMessageReaction
            signature = "sbsxay"
        if not real_recipients:
            return (
                {
                    "error": f"{recipients} is neither a phone number nor a valid group id"
                },
                400,
            )
        result = method(
            reaction,
            remove,
            target_author,
            timestamp,
            real_recipients,
            signature=signature,
        )
        return {"timestamp": str(result)}, 201
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, 'message', repr(err))
        logger.error(error)
        return {"error": error}, 400


@dataclass
class ReactionsV1PostParams:
    """
    ReactionsV1PostParams
    """

    reaction: str
    target_author: str
    timestamp: int
    recipients: Optional[List[str]] = field(default_factory=list)
    recipient: Optional[str] = field(default_factory=str)
    remove: Optional[bool] = False


@dataclass
class ReactionsV1PostResponse:
    """
    ReactionsV1PostResponse
    """

    timestamp: str


@reactions_v1.post("/<number:path>", version=1)
@openapi.tag("Reactions")
@openapi.parameter("number", str, required=True, location="path")
@openapi.body({"application/json": ReactionsV1PostParams}, required=True)
@openapi.response(201, {"application/json": ReactionsV1PostResponse}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description(
    "Send a reaction. Request must include either `recipient` or `recipients`!"
)
@validate(json=ReactionsV1PostParams)
async def reactions_v1_post(request, number, body: ReactionsV1PostParams):  # pylint: disable=unused-argument
    """
    Send a reaction.
    """
    if not request.json.get("recipient") or request.json.get("recipients"):
        return json(
            {
                "error": "missing either parameter recipient (str) or recipients (list of strings)"
            },
            400,
        )
    return_message, return_code = send_reaction(
        number=number,
        reaction=request.json.get("reaction"),
        remove=request.json.get("remove"),
        target_author=request.json.get("target_author"),
        timestamp=request.json.get("timestamp"),
        recipients=request.json.get("recipients", request.json.get("recipient")),
    )
    return json(return_message, return_code)
