"""
groups handler
"""

from dataclasses import dataclass
from typing import List

from sanic import Blueprint
from sanic.log import logger
from sanic.response import json
from sanic_ext import openapi
from signal_cli_dbus_rest_api.dataclasses import Error
from signal_cli_dbus_rest_api.lib.dbus import SignalCLIDBus
from signal_cli_dbus_rest_api.lib.helper import get_group_properties

groups_for_number = Blueprint("groups_of_number", url_prefix="/groups")
group_details = Blueprint("group_details", url_prefix="/groups")


@dataclass
class GroupsForNumberGetV1Params:
    """
    GroupsForNumberGetV1Params
    """

    number: str


@dataclass
class GroupsForNumberGetV1ResponseItem:  # pylint: disable=too-many-instance-attributes
    """
    GroupsForNumberGetV1ResponseItem
    """

    blocked: bool
    id: str  # pylint: disable=invalid-name
    internal_id: str
    invite_link: str
    members: List[str]
    name: str
    pending_invites: List[str]
    pending_requests: List[str]
    message_expiration_timer: int
    admins: List[str]
    description: str


@groups_for_number.get("/<number>", version=1)
@openapi.tag("Groups")
@openapi.parameter(
    "number",
    str,
    required=True,
    location="query",
    description="Registered Phone Number",
)
@openapi.response(
    200,
    {"application/json": List[GroupsForNumberGetV1ResponseItem]},
    description="OK",
)
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("List all Signal Groups.")
async def groups_for_number_get(request, number):  # pylint: disable=unused-argument
    """
    List all Signal Groups.
    """
    try:
        dbus = SignalCLIDBus(number=number)
        groups = dbus.pydbusconn.listGroups()
        result = []
        for group in groups:
            success, data = get_group_properties(
                systembus=dbus.pydbus,
                objectpath=group[0],
            )
            if not success:
                return json({"error": result}, 400)
            result.append(data)
        return json(result, 200)
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, 'message', repr(err))
        logger.error(error)
        return json({"error": error}, 400)


@group_details.get("/<number>/<groupid:path>", version=1)
@openapi.tag("Groups")
@openapi.parameter(
    "number",
    str,
    required=True,
    location="path",
    description="Registered Phone Number",
)
@openapi.parameter(
    "groupid",
    str,
    required=True,
    location="path",
    description="Group ID (hint: you'll need to replace forwards slash / with underscore _)",
)
@openapi.response(
    200,
    {"application/json": GroupsForNumberGetV1ResponseItem},
    description="OK",
)
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("List a Signal Group.")
async def groups_of_number_get(
    request, number, groupid
):  # pylint: disable=unused-argument
    """
    List a Signal Group.
    """
    try:
        dbus = SignalCLIDBus()
        success, data = get_group_properties(
            systembus=dbus.pydbus,
            number=number,
            groupid=groupid,
        )
        if not success:
            return json({"error": data}, 400)
        return json(data, 200)
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, 'message', repr(err))
        logger.error(error)
        return json({"error": error}, 400)
