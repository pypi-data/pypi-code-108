r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareUpload", "SoftwareUploadSchema"]
__pdoc__ = {
    "SoftwareUploadSchema.resource": False,
    "SoftwareUpload": False,
}


class SoftwareUploadSchema(ResourceSchema):
    """The fields of the SoftwareUpload object"""

    file = fields.Str(data_key="file")
    r""" Package file on a local file system

Example: base64 encoded package file content """

    @property
    def resource(self):
        return SoftwareUpload

    gettable_fields = [
        "file",
    ]
    """file,"""

    patchable_fields = [
        "file",
    ]
    """file,"""

    postable_fields = [
        "file",
    ]
    """file,"""


class SoftwareUpload(Resource):

    _schema = SoftwareUploadSchema
