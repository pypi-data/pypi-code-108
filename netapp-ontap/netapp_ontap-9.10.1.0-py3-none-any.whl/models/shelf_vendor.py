r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfVendor", "ShelfVendorSchema"]
__pdoc__ = {
    "ShelfVendorSchema.resource": False,
    "ShelfVendor": False,
}


class ShelfVendorSchema(ResourceSchema):
    """The fields of the ShelfVendor object"""

    manufacturer = fields.Str(data_key="manufacturer")
    r""" Support for this field will be removed in a future release. Please use vendor.name for this field.

Example: XYZ """

    name = fields.Str(data_key="name")
    r""" The name field of the shelf_vendor.

Example: XYZ """

    part_number = fields.Str(data_key="part_number")
    r""" Part number

Example: A92831142733 """

    product = fields.Str(data_key="product")
    r""" Product name

Example: LS2246 """

    serial_number = fields.Str(data_key="serial_number")
    r""" Serial number

Example: 891234572210221 """

    @property
    def resource(self):
        return ShelfVendor

    gettable_fields = [
        "manufacturer",
        "name",
        "part_number",
        "product",
        "serial_number",
    ]
    """manufacturer,name,part_number,product,serial_number,"""

    patchable_fields = [
        "manufacturer",
        "name",
        "part_number",
        "product",
        "serial_number",
    ]
    """manufacturer,name,part_number,product,serial_number,"""

    postable_fields = [
        "manufacturer",
        "name",
        "part_number",
        "product",
        "serial_number",
    ]
    """manufacturer,name,part_number,product,serial_number,"""


class ShelfVendor(Resource):

    _schema = ShelfVendorSchema
