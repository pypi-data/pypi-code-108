r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FpolicyConnectionDisconnectedReason", "FpolicyConnectionDisconnectedReasonSchema"]
__pdoc__ = {
    "FpolicyConnectionDisconnectedReasonSchema.resource": False,
    "FpolicyConnectionDisconnectedReason": False,
}


class FpolicyConnectionDisconnectedReasonSchema(ResourceSchema):
    """The fields of the FpolicyConnectionDisconnectedReason object"""

    code = Size(data_key="code")
    r""" Reason ID for the FPolicy Server disconnection.

Example: 9370 """

    message = fields.Str(data_key="message")
    r""" FPolicy server reason for disconnection message.

Example: TCP Connection to FPolicy server failed. """

    @property
    def resource(self):
        return FpolicyConnectionDisconnectedReason

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    postable_fields = [
        "code",
        "message",
    ]
    """code,message,"""


class FpolicyConnectionDisconnectedReason(Resource):

    _schema = FpolicyConnectionDisconnectedReasonSchema
