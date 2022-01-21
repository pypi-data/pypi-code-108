r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeEncryptionStatus", "VolumeEncryptionStatusSchema"]
__pdoc__ = {
    "VolumeEncryptionStatusSchema.resource": False,
    "VolumeEncryptionStatus": False,
}


class VolumeEncryptionStatusSchema(ResourceSchema):
    """The fields of the VolumeEncryptionStatus object"""

    code = fields.Str(data_key="code")
    r""" Encryption progress message code. """

    message = fields.Str(data_key="message")
    r""" Encryption progress message. """

    @property
    def resource(self):
        return VolumeEncryptionStatus

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


class VolumeEncryptionStatus(Resource):

    _schema = VolumeEncryptionStatusSchema
