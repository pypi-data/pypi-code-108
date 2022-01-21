r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FileInfoConstituent", "FileInfoConstituentSchema"]
__pdoc__ = {
    "FileInfoConstituentSchema.resource": False,
    "FileInfoConstituent": False,
}


class FileInfoConstituentSchema(ResourceSchema):
    """The fields of the FileInfoConstituent object"""

    name = fields.Str(data_key="name")
    r""" FlexGroup volume constituent name.

Example: fg__0001 """

    uuid = fields.Str(data_key="uuid")
    r""" FlexGroup volume constituent UUID.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return FileInfoConstituent

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FileInfoConstituent(Resource):

    _schema = FileInfoConstituentSchema
