r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IscsiCredentialsChapOutbound", "IscsiCredentialsChapOutboundSchema"]
__pdoc__ = {
    "IscsiCredentialsChapOutboundSchema.resource": False,
    "IscsiCredentialsChapOutbound": False,
}


class IscsiCredentialsChapOutboundSchema(ResourceSchema):
    """The fields of the IscsiCredentialsChapOutbound object"""

    password = fields.Str(data_key="password")
    r""" The outbound CHAP password. Write-only; optional in POST and PATCH. """

    user = fields.Str(data_key="user")
    r""" The outbound CHAP user name. Optional in POST and PATCH. """

    @property
    def resource(self):
        return IscsiCredentialsChapOutbound

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


class IscsiCredentialsChapOutbound(Resource):

    _schema = IscsiCredentialsChapOutboundSchema
