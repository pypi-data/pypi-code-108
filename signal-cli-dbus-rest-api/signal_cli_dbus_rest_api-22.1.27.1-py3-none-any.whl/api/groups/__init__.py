"""
groups handler
"""

from base64 import b64encode
from dataclasses import dataclass, field
from enum import Enum
from os import remove as os_remove
from typing import Dict, List, Optional
from uuid import uuid4

from sanic import Blueprint, Sanic
from sanic.log import logger
from sanic.response import json, empty
from sanic_ext import openapi, validate
from signal_cli_dbus_rest_api.dataclasses import Error, GroupId
from signal_cli_dbus_rest_api.lib.dbus import SignalCLIDBus
from signal_cli_dbus_rest_api.lib.helper import (do_decode_attachments,
                                                 get_group_properties)

create_group_v1 = Blueprint("create_group_v1", url_prefix="/groups")
delete_group_v1 = Blueprint("delete_group_v1", url_prefix="/groups")
groups_for_number_v1 = Blueprint("groups_of_number_v1", url_prefix="/groups")
group_details_v1 = Blueprint("group_details_v1", url_prefix="/groups")
join_group_v1 = Blueprint("join_group_v1", url_prefix="/groups")
quit_group_v1 = Blueprint("quit_group_v1", url_prefix="/groups")
update_group_v1 = Blueprint("update_group_v1", url_prefix="/groups")


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
                return json({"error": data}, 400)
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
    description="Group ID",
)
@openapi.response(
    200,
    {"application/json": GroupsForNumberGetV1ResponseItem},
    description="OK",
)
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("List a Signal Group.")
async def groups_of_number_get(
        request, number: str, groupid: str
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

    DISABLED = "disabled"
    ENABLED = "enabled"
    ENABLED_WITH_APPROVAL = "enabled-with-approval"


def update_group_link(pydbusconn, setting):
    """
    return proper method to call for group link handling
    """
    # pylint: disable=no-member
    approvals = {
        GroupLinkV1Choices.ENABLED.value: False,
        GroupLinkV1Choices.ENABLED_WITH_APPROVAL.value: True,
    }
    methods = {
        GroupLinkV1Choices.DISABLED.value: pydbusconn.disableLink,
        GroupLinkV1Choices.ENABLED.value: pydbusconn.enableLink,
        GroupLinkV1Choices.ENABLED_WITH_APPROVAL.value: pydbusconn.enableLink,
    }
    method = methods.get(setting, None)
    if method is None:
        return
    approval = approvals.get(setting, None)
    if approval is None:
        method()
        return
    method(approval)
    return


@dataclass
class CreateGroupV1PostParamsDocs:  # pylint: disable=too-many-instance-attributes
    """
    CreateGroupV1PostParams
    """

    name: str
    members: List[str]
    permissions: Optional[CreateGroupV1Permissions]
    group_link: Optional[GroupLinkV1Choices]
    admins: Optional[List[str]] = field(default_factory=list)
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
        b64_groupid = b64encode(bytearray(groupid)).decode()
        dbus = SignalCLIDBus(
            number=number,
            groupid=b64_groupid
        )
        update_group_link(dbus.pydbusconn, body.group_link)
        dbus.pydbusconn.Description = body.description
        dbus.pydbusconn.MessageExpirationTimer = body.message_expiration_timer
        dbus.pydbusconn.PermissionAddMember = (
            body.permissions.add_members.upper().replace("-", "_")
        )
        dbus.pydbusconn.PermissionEditDetails = (
            body.permissions.edit_group.upper().replace("-", "_")
        )
        if body.admins:
            dbus.pydbusconn.addAdmins(body.admins)
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)
    finally:
        os_remove(avatar)
    return json({"id": b64_groupid}, 201)


@delete_group_v1.delete("/<number:path>/<groupid:path>", version=1)
@openapi.tag("Groups")
@openapi.parameter("number", str, required=True, location="path")
@openapi.parameter("groupid", str, required=True, location="path")
@openapi.response(204, None, description="OK")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Delete a Signal Group.")
async def delete_group_v1_delete(
    request, number: str, groupid: str
):  # pylint: disable=unused-argument
    """
    Delete the specified Signal Group.
    """
    try:
        dbus = SignalCLIDBus(number=number, groupid=groupid)
        dbus.pydbusconn.deleteGroup()
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)
    return empty


@dataclass
class UpdateGroupLinkV1Choices(Enum):
    """
    UpdateGroupLinkV1Choices
    """

    UNCHANGED = "unchanged"
    DISABLED = "disabled"
    ENABLED = "enabled"
    ENABLED_WITH_APPROVAL = "enabled-with-approval"


@dataclass
class UpdateGroupV1PatchParamsDocs:
    """
    UpdateGroupV1PatchParamsDocs
    """

    group_link: Optional[UpdateGroupLinkV1Choices]
    add_admins: Optional[List[str]] = field(default_factory=list)
    add_members: Optional[List[str]] = field(default_factory=list)


@dataclass
class UpdateGroupV1PatchParamsValidate(UpdateGroupV1PatchParamsDocs):
    """
    UpdateGroupV1PatchParamsValidate
    """

    group_link: str = "unchanged"


@update_group_v1.patch("/<number:path>/<groupid:path>", version=1)
@openapi.tag("Groups")
@openapi.parameter("number", str, required=True, location="path")
@openapi.parameter("groupid", str, required=True, location="path")
@openapi.body({"application/json": UpdateGroupV1PatchParamsDocs})
@openapi.response(
    200,
    {"application/json": GroupsForNumberGetV1ResponseItem},
    description="OK",
)
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Update an existing Signal Group.")
@validate(UpdateGroupV1PatchParamsValidate)
async def update_group_v1_patch(
        request, number: str, groupid: str, body: UpdateGroupV1PatchParamsValidate
):  # pylint: disable=unused-argument
    """
    Update an existing Signal Group.
    """
    try:
        dbus = SignalCLIDBus(number=number, groupid=groupid)
        if body.add_admins:
            dbus.pydbusconn.addAdmins(body.add_admins)
        if body.add_members:
            dbus.pydbusconn.addMembers(body.add_members)
        update_group_link(dbus.pydbusconn, body.group_link)
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
    return json(data, 200)


@quit_group_v1.post("/<number:path>/<groupid:path>/quit", version=1)
@openapi.tag("Groups")
@openapi.parameter("number", str, required=True, location="path")
@openapi.parameter("groupid", str, required=True, location="path")
@openapi.body({"application/json": UpdateGroupV1PatchParamsDocs})
@openapi.response(204, None, description="OK")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Quit (leave) a Signal Group.")
async def quit_group_v1_post(
        request, number: str, groupid: str
):  # pylint: disable=unused-argument
    """
    Quit (leave) a Signal Group.
    """
    try:
        dbus = SignalCLIDBus(number=number, groupid=groupid)
        dbus.pydbusconn.quitGroup()
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)
    return empty


@join_group_v1.post("/<number:path>/<groupid:path>/join", version=1)
@openapi.tag("Groups")
@openapi.parameter("number", str, required=True, location="path")
@openapi.parameter(
    "groupid",
    str,
    required=True,
    location="path",
    description="Get from invite link: https://signal.group/#`${groupid}`")
@openapi.response(204, None, description="OK")
@openapi.response(400, {"application/json": Error}, description="Bad Request")
@openapi.description("Join a Signal Group.")
async def join_group_v1_post(
        request, number: str, groupid: str
):  # pylint: disable=unused-argument
    """
    Join a Signal Group.
    """
    try:
        dbus = SignalCLIDBus(number=number)
        dbus.pydbusconn.joinGroup(f"https://signal.group/#{groupid}")
    # pylint: disable=broad-except
    except Exception as err:
        error = getattr(err, "message", repr(err))
        logger.error(error)
        return json({"error": error}, 400)
    return empty
