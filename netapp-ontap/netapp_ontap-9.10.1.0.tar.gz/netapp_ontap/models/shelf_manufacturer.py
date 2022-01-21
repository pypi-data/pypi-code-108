r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfManufacturer", "ShelfManufacturerSchema"]
__pdoc__ = {
    "ShelfManufacturerSchema.resource": False,
    "ShelfManufacturer": False,
}


class ShelfManufacturerSchema(ResourceSchema):
    """The fields of the ShelfManufacturer object"""

    name = fields.Str(data_key="name")
    r""" The name field of the shelf_manufacturer.

Example: NETAPP """

    @property
    def resource(self):
        return ShelfManufacturer

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


class ShelfManufacturer(Resource):

    _schema = ShelfManufacturerSchema
