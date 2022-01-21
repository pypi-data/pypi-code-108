r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["UnixGroupUsersUnixGroup", "UnixGroupUsersUnixGroupSchema"]
__pdoc__ = {
    "UnixGroupUsersUnixGroupSchema.resource": False,
    "UnixGroupUsersUnixGroup": False,
}


class UnixGroupUsersUnixGroupSchema(ResourceSchema):
    """The fields of the UnixGroupUsersUnixGroup object"""

    name = fields.Str(data_key="name")
    r""" UNIX group name. """

    @property
    def resource(self):
        return UnixGroupUsersUnixGroup

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class UnixGroupUsersUnixGroup(Resource):

    _schema = UnixGroupUsersUnixGroupSchema
