"""
groups handler
"""

from base64 import b64encode
from dataclasses import dataclass, field
from enum import Enum
from os import remove as os_remove
from re import sub
from typing import Dict, List, Optional
from uuid import uuid4

from sanic import Blueprint, Sanic
from sanic.log import logger
from sanic.response import json
from sanic_ext import openapi, validate
from signal_cli_dbus_rest_api.dataclasses import Error, GroupId
from signal_cli_dbus_rest_api.lib.dbus import SignalCLIDBus
from signal_cli_dbus_rest_api.lib.helper import (do_decode_attachments,
                                                 get_group_properties)

groups_for_number_v1 = Blueprint("groups_of_number_v1", url_prefix="/groups")
group_details_v1 = Blueprint("group_details_v1", url_prefix="/groups")
create_group_v1 = Blueprint("create_group_v1", url_prefix="/groups")
delete_group_v1 = Blueprint("delete_group_v1", url_prefix="/groups")


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


@groups_for_number_v1.get("/<number:path>", version=1)
@openapi.tag("Groups")
@openapi.parameter(
    "number",
    str,
    required=True,
    location="path",
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
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)


@group_details_v1.get("/<number:path>/<groupid:path>", version=1)
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
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)


@dataclass
class CreateGroupV1Permissions:
    """
    CreateGroupV1Permissions
    """

    add_members: str = "only-admins"
    edit_group: str = "only-admins"


@dataclass
class GroupLinkV1Choices(Enum):
    """
    GroupLinkV1Choices
    """

    FIRST = "disabled"
    SECOND = "enabled"
    THIRD = "enabled-with-approval"


@dataclass
class CreateGroupV1PostParamsDocs:
    """
    CreateGroupV1PostParams
    """

    name: str
    members: List[str]
    permissions: Optional[CreateGroupV1Permissions]
    group_link: Optional[GroupLinkV1Choices] = field(default="enabled")
    description: Optional[str] = field(default_factory=str)
    base64_avatar: Optional[str] = field(default_factory=str)
    message_expiration_timer: Optional[int] = 0


@dataclass
class CreateGroupV1PostParamsValidate(CreateGroupV1PostParamsDocs):
    """
    CreateGroupV1PostParamsValidate
    """

    group_link: str = "disabled"
    permissions: Optional[Dict[str, CreateGroupV1Permissions]] = field(
        default_factory=dict
    )

    def __post_init__(self):
        if isinstance(self.permissions, dict):
            self.permissions = CreateGroupV1Permissions(**self.permissions)


@create_group_v1.post("/<number:path>", version=1)
@openapi.tag("Groups")
@openapi.parameter("number", str, required=True, location="path")
@openapi.body({"application/json": CreateGroupV1PostParamsDocs}, required=True)
@openapi.response(201, {"application/json": GroupId}, description="Created")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Create a new Signal Group.")
@validate(CreateGroupV1PostParamsValidate)
async def create_group_v1_post(
    request, number, body: CreateGroupV1PostParamsValidate
):  # pylint: disable=unused-argument
    """
    Create a new Signal Group with the specified members.
    """
    avatar = ""
    app = Sanic.get_app()
    try:
        number = number or app.config.ACCOUNT
    except AttributeError:
        return json(
            {
                "error": "number missing in request and SIGNAL_CLI_DBUS_REST_API_ACCOUNT unset "
            },
            400,
        )
    uuid = str(uuid4())
    try:
        avatar = do_decode_attachments([body.base64_avatar], uuid)[0]
    # pylint: disable=broad-except
    except IndexError:
        pass
    try:
        dbus = SignalCLIDBus(number=number)
        groupid = dbus.pydbusconn.createGroup(
            body.name,
            body.members,
            avatar,
        )
        groupid = b64encode(bytearray(groupid)).decode()
        dbus = SignalCLIDBus(number=number, groupid=sub(r"[+|=|/]", "_", groupid))
        if body.group_link in ["enabled", "enabled-with-approval"]:
            approval = False
            if body.group_link == "enabled-with-approval":
                approval = True
            dbus.pydbus.enableLink(approval)
        dbus.pydbusconn.Description = body.description
        dbus.pydbusconn.MessageExpirationTimer = body.message_expiration_timer
        dbus.pydbusconn.PermissionAddMember = (
            body.permissions.add_members.upper().replace("-", "_")
        )
        dbus.pydbusconn.PermissionEditDetails = (
            body.permissions.edit_group.upper().replace("-", "_")
        )
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)
    finally:
        os_remove(avatar)
    return json({"id": groupid}, 201)


@delete_group_v1.delete("/<number:path>", version=1)
@openapi.tag("Groups")
@openapi.parameter("number", str, required=True, location="path")
@openapi.parameter("groupid", str, required=True, location="path")
@openapi.response(204, None, description="Deleted")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Delete a Signal Group.")
@validate(CreateGroupV1PostParamsValidate)
async def delete_group_v1_delete(
    number, groupid
):  # pylint: disable=unused-argument
    """
    Delete the specified Signal Group.
    """
    try:
        dbus = SignalCLIDBus(number=number, groupid=sub(r"[+|=|/]", "_", groupid))
        dbus.pydbusconn.deleteGroup()
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)
    return json(None, 204)
