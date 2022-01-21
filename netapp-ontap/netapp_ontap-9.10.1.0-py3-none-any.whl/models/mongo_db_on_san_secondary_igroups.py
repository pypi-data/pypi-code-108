r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MongoDbOnSanSecondaryIgroups", "MongoDbOnSanSecondaryIgroupsSchema"]
__pdoc__ = {
    "MongoDbOnSanSecondaryIgroupsSchema.resource": False,
    "MongoDbOnSanSecondaryIgroups": False,
}


class MongoDbOnSanSecondaryIgroupsSchema(ResourceSchema):
    """The fields of the MongoDbOnSanSecondaryIgroups object"""

    name = fields.Str(data_key="name")
    r""" The name of the initiator group for each secondary. """

    @property
    def resource(self):
        return MongoDbOnSanSecondaryIgroups

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


class MongoDbOnSanSecondaryIgroups(Resource):

    _schema = MongoDbOnSanSecondaryIgroupsSchema
