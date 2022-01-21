r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IscsiCredentialsChapInbound", "IscsiCredentialsChapInboundSchema"]
__pdoc__ = {
    "IscsiCredentialsChapInboundSchema.resource": False,
    "IscsiCredentialsChapInbound": False,
}


class IscsiCredentialsChapInboundSchema(ResourceSchema):
    """The fields of the IscsiCredentialsChapInbound object"""

    password = fields.Str(data_key="password")
    r""" The inbound CHAP password. Write-only; optional in POST and PATCH. """

    user = fields.Str(data_key="user")
    r""" The inbound CHAP user name. Optional in POST and PATCH. """

    @property
    def resource(self):
        return IscsiCredentialsChapInbound

    gettable_fields = [
        "user",
    ]
    """user,"""

    patchable_fields = [
        "password",
        "user",
    ]
    """password,user,"""

    postable_fields = [
        "password",
        "user",
    ]
    """password,user,"""


class IscsiCredentialsChapInbound(Resource):

    _schema = IscsiCredentialsChapInboundSchema
