r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeAnalyticsUnsupportedReason", "VolumeAnalyticsUnsupportedReasonSchema"]
__pdoc__ = {
    "VolumeAnalyticsUnsupportedReasonSchema.resource": False,
    "VolumeAnalyticsUnsupportedReason": False,
}


class VolumeAnalyticsUnsupportedReasonSchema(ResourceSchema):
    """The fields of the VolumeAnalyticsUnsupportedReason object"""

    code = fields.Str(data_key="code")
    r""" If file system analytics is not supported on the volume, this field provides the error code explaining why.

Example: 111411207 """

    message = fields.Str(data_key="message")
    r""" If file system analytics is not supported on the volume, this field provides the error message explaining why.

Example: File system analytics cannot be enabled on volumes that contain LUNs. """

    @property
    def resource(self):
        return VolumeAnalyticsUnsupportedReason

    gettable_fields = [
        "code",
        "message",
    ]
    """code,message,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeAnalyticsUnsupportedReason(Resource):

    _schema = VolumeAnalyticsUnsupportedReasonSchema
