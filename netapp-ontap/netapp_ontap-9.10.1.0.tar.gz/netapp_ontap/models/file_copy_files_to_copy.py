r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FileCopyFilesToCopy", "FileCopyFilesToCopySchema"]
__pdoc__ = {
    "FileCopyFilesToCopySchema.resource": False,
    "FileCopyFilesToCopy": False,
}


class FileCopyFilesToCopySchema(ResourceSchema):
    """The fields of the FileCopyFilesToCopy object"""

    destination = fields.Nested("netapp_ontap.models.file.FileSchema", unknown=EXCLUDE, data_key="destination")
    r""" The destination field of the file_copy_files_to_copy. """

    source = fields.Nested("netapp_ontap.models.file.FileSchema", unknown=EXCLUDE, data_key="source")
    r""" The source field of the file_copy_files_to_copy. """

    @property
    def resource(self):
        return FileCopyFilesToCopy

    gettable_fields = [
        "destination.path",
        "destination.svm",
        "destination.volume",
        "source.path",
        "source.svm",
        "source.volume",
    ]
    """destination.path,destination.svm,destination.volume,source.path,source.svm,source.volume,"""

    patchable_fields = [
        "destination.path",
        "destination.svm",
        "destination.volume",
        "source.path",
        "source.svm",
        "source.volume",
    ]
    """destination.path,destination.svm,destination.volume,source.path,source.svm,source.volume,"""

    postable_fields = [
        "destination.path",
        "destination.svm",
        "destination.volume",
        "source.path",
        "source.svm",
        "source.volume",
    ]
    """destination.path,destination.svm,destination.volume,source.path,source.svm,source.volume,"""


class FileCopyFilesToCopy(Resource):

    _schema = FileCopyFilesToCopySchema
