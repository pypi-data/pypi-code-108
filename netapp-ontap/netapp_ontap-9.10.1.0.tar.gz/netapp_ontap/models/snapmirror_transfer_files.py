r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapmirrorTransferFiles", "SnapmirrorTransferFilesSchema"]
__pdoc__ = {
    "SnapmirrorTransferFilesSchema.resource": False,
    "SnapmirrorTransferFiles": False,
}


class SnapmirrorTransferFilesSchema(ResourceSchema):
    """The fields of the SnapmirrorTransferFiles object"""

    destination_path = fields.Str(data_key="destination_path")
    r""" The destination_path field of the snapmirror_transfer_files.

Example: /dirb/file2 """

    source_path = fields.Str(data_key="source_path")
    r""" The source_path field of the snapmirror_transfer_files.

Example: /dira/file1 """

    @property
    def resource(self):
        return SnapmirrorTransferFiles

    gettable_fields = [
        "destination_path",
        "source_path",
    ]
    """destination_path,source_path,"""

    patchable_fields = [
        "destination_path",
        "source_path",
    ]
    """destination_path,source_path,"""

    postable_fields = [
        "destination_path",
        "source_path",
    ]
    """destination_path,source_path,"""


class SnapmirrorTransferFiles(Resource):

    _schema = SnapmirrorTransferFilesSchema
