r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeEncryptionSupport", "VolumeEncryptionSupportSchema"]
__pdoc__ = {
    "VolumeEncryptionSupportSchema.resource": False,
    "VolumeEncryptionSupport": False,
}


class VolumeEncryptionSupportSchema(ResourceSchema):
    """The fields of the VolumeEncryptionSupport object"""

    code = Size(data_key="code")
    r""" Code corresponding to the status message. Returns a 0 if volume encryption is supported in all nodes of the cluster.

Example: 346758 """

    message = fields.Str(data_key="message")
    r""" Reason for not supporting volume encryption.

Example: No platform support for volume encryption in following nodes - node1, node2. """

    supported = fields.Boolean(data_key="supported")
    r""" Set to true when volume encryption support is available on all nodes of the cluster. """

    @property
    def resource(self):
        return VolumeEncryptionSupport

    gettable_fields = [
        "code",
        "message",
        "supported",
    ]
    """code,message,supported,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeEncryptionSupport(Resource):

    _schema = VolumeEncryptionSupportSchema
