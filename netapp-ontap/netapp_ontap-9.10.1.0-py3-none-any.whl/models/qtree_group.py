r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QtreeGroup", "QtreeGroupSchema"]
__pdoc__ = {
    "QtreeGroupSchema.resource": False,
    "QtreeGroup": False,
}


class QtreeGroupSchema(ResourceSchema):
    """The fields of the QtreeGroup object"""

    id = fields.Str(data_key="id")
    r""" The numeric ID of the group that owns the qtree. Valid in POST or PATCH.

Example: 20001 """

    name = fields.Str(data_key="name")
    r""" Alphanumeric group name of group that owns the qtree. Valid in POST or PATCH.

Example: unix_group1 """

    @property
    def resource(self):
        return QtreeGroup

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


class QtreeGroup(Resource):

    _schema = QtreeGroupSchema
