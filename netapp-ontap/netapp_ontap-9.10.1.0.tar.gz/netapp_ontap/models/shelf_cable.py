r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfCable", "ShelfCableSchema"]
__pdoc__ = {
    "ShelfCableSchema.resource": False,
    "ShelfCable": False,
}


class ShelfCableSchema(ResourceSchema):
    """The fields of the ShelfCable object"""

    identifier = fields.Str(data_key="identifier")
    r""" The identifier field of the shelf_cable.

Example: 500a0980000b6c3f-50000d1703544b80 """

    length = fields.Str(data_key="length")
    r""" The length field of the shelf_cable.

Example: 2m """

    part_number = fields.Str(data_key="part_number")
    r""" The part_number field of the shelf_cable.

Example: 112-00431+A0 """

    serial_number = fields.Str(data_key="serial_number")
    r""" The serial_number field of the shelf_cable.

Example: 616930439 """

    @property
    def resource(self):
        return ShelfCable

    gettable_fields = [
        "identifier",
        "length",
        "part_number",
        "serial_number",
    ]
    """identifier,length,part_number,serial_number,"""

    patchable_fields = [
        "identifier",
        "length",
        "part_number",
        "serial_number",
    ]
    """identifier,length,part_number,serial_number,"""

    postable_fields = [
        "identifier",
        "length",
        "part_number",
        "serial_number",
    ]
    """identifier,length,part_number,serial_number,"""


class ShelfCable(Resource):

    _schema = ShelfCableSchema
