r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FileInfoLinks", "FileInfoLinksSchema"]
__pdoc__ = {
    "FileInfoLinksSchema.resource": False,
    "FileInfoLinks": False,
}


class FileInfoLinksSchema(ResourceSchema):
    """The fields of the FileInfoLinks object"""

    metadata = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="metadata")
    r""" The metadata field of the file_info_links. """

    self_ = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="self")
    r""" The self_ field of the file_info_links. """

    @property
    def resource(self):
        return FileInfoLinks

    gettable_fields = [
        "metadata",
        "self_",
    ]
    """metadata,self_,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FileInfoLinks(Resource):

    _schema = FileInfoLinksSchema
