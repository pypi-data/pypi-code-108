r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["UnixGroupUsersNoRecords", "UnixGroupUsersNoRecordsSchema"]
__pdoc__ = {
    "UnixGroupUsersNoRecordsSchema.resource": False,
    "UnixGroupUsersNoRecords": False,
}


class UnixGroupUsersNoRecordsSchema(ResourceSchema):
    """The fields of the UnixGroupUsersNoRecords object"""

    name = fields.Str(data_key="name")
    r""" UNIX user who belongs to the specified UNIX group and the SVM. """

    @property
    def resource(self):
        return UnixGroupUsersNoRecords

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
    ]
    """name,"""


class UnixGroupUsersNoRecords(Resource):

    _schema = UnixGroupUsersNoRecordsSchema
