r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QtreeUser", "QtreeUserSchema"]
__pdoc__ = {
    "QtreeUserSchema.resource": False,
    "QtreeUser": False,
}


class QtreeUserSchema(ResourceSchema):
    """The fields of the QtreeUser object"""

    id = fields.Str(data_key="id")
    r""" The numeric ID of the user who owns the qtree. Valid in POST or PATCH.

Example: 10001 """

    name = fields.Str(data_key="name")
    r""" Alphanumeric username of user who owns the qtree. Valid in POST or PATCH.

Example: unix_user1 """

    @property
    def resource(self):
        return QtreeUser

    gettable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    patchable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    postable_fields = [
        "id",
        "name",
    ]
    """id,name,"""


class QtreeUser(Resource):

    _schema = QtreeUserSchema
