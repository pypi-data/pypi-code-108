r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchComponent", "StorageSwitchComponentSchema"]
__pdoc__ = {
    "StorageSwitchComponentSchema.resource": False,
    "StorageSwitchComponent": False,
}


class StorageSwitchComponentSchema(ResourceSchema):
    """The fields of the StorageSwitchComponent object"""

    id = Size(data_key="id")
    r""" Error component ID """

    name = fields.Str(data_key="name")
    r""" Error component name """

    @property
    def resource(self):
        return StorageSwitchComponent

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


class StorageSwitchComponent(Resource):

    _schema = StorageSwitchComponentSchema
