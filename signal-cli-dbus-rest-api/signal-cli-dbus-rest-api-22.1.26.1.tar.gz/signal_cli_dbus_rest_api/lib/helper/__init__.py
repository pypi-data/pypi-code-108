"""
helpers
"""

from base64 import b64decode, b64encode
from binascii import Error as binascii_Error
from io import BytesIO
from mimetypes import guess_extension
from re import sub
from tempfile import mkstemp

from magic import from_buffer
from sanic.log import logger


def get_groupid_as_bytes(recipient: str, version: int = 2):
    """
    convert base64 encoded group id to bytes
    see https://github.com/AsamK/signal-cli/issues/272
    and https://github.com/AsamK/signal-cli/wiki/DBus-service
    """
    if version == 1:
        recipient = recipient.replace("_", "/")
    try:
        return b64decode(
            recipient, validate=True
        )
    except binascii_Error:
        return None


def is_phone_number(recipients: list, dbus_connection: object):
    """
    check if recipient is a valid phone number
    """
    if not isinstance(recipients, list):
        return None
    if isinstance(recipients[0], bytes):
        return None
    for recipient in recipients:
        if not (recipient.startswith("0") or recipient.startswith("+")):
            recipient = f"+{recipient}"
        if not dbus_connection.isRegistered(recipient):
            return None
    return recipients


def get_group_properties(systembus: object, number: str = "",
                         objectpath: str = "", groupid: str = ""):
    """
    get group properties
    """
    if not objectpath:
        if not number and groupid:
            return (False, "Missing number and groupid")
        objectpath = (
            f"/org/asamk/Signal/_{number.strip('+')}/"
            f"Groups/{sub(r'[+|=|/]', '_', groupid)}"
        )
    try:
        result = systembus.get(
            "org.asamk.Signal",
            objectpath,
        ).GetAll("org.asamk.Signal.Group")
        return (
            True,
            {
                "blocked": result.get("IsBlocked"),
                "id": b64encode(bytearray(result.get("Id"))).decode(),
                "internal_id": result.get("Id"),
                "invite_link": result.get("GroupInviteLink"),
                "members": result.get("Members"),
                "name": result.get("Name"),
                "pending_invites": result.get("PendingMembers"),
                "pending_requests": result.get("RequestingMembers"),
                "message_expiration_timer": result.get("MessageExpirationTimer"),
                "admins": result.get("Admins"),
                "description": result.get("Description"),
            }
        )
    # pylint: disable=broad-except
    except Exception as err:
        return (False, err)


def do_decode_attachments(attachments, uuid):
    """
    decode base64 attachments and dump the decoded
    content to disk for sending out later
    """
    decoded_attachments = []
    for index, attachment in enumerate(attachments):
        try:
            attachment_io_bytes = BytesIO()
            attachment_io_bytes.write(b64decode(attachment))
            extension = guess_extension(
                from_buffer(attachment_io_bytes.getvalue(), mime=True)
            )
            _, filename = mkstemp(prefix=f"{uuid}_{index}_", suffix=f".{extension}")
            with open(filename, "wb") as f_h:
                f_h.write(b64decode(attachment))
            decoded_attachments.append(filename)
        # pylint: disable=broad-except
        except Exception as err:
            logger.error("unable to decode attachment: %s", err)
    return decoded_attachments
