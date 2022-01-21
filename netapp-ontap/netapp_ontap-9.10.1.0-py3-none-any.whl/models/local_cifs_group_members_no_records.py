r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LocalCifsGroupMembersNoRecords", "LocalCifsGroupMembersNoRecordsSchema"]
__pdoc__ = {
    "LocalCifsGroupMembersNoRecordsSchema.resource": False,
    "LocalCifsGroupMembersNoRecords": False,
}


class LocalCifsGroupMembersNoRecordsSchema(ResourceSchema):
    """The fields of the LocalCifsGroupMembersNoRecords object"""

    name = fields.Str(data_key="name")
    r""" Local user, Active Directory user, or Active Directory group which is a member of the specified local group. """

    @property
    def resource(self):
        return LocalCifsGroupMembersNoRecords

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


class LocalCifsGroupMembersNoRecords(Resource):

    _schema = LocalCifsGroupMembersNoRecordsSchema
