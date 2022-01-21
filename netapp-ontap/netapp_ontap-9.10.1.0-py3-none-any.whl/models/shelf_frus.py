r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfFrus", "ShelfFrusSchema"]
__pdoc__ = {
    "ShelfFrusSchema.resource": False,
    "ShelfFrus": False,
}


class ShelfFrusSchema(ResourceSchema):
    """The fields of the ShelfFrus object"""

    firmware_version = fields.Str(data_key="firmware_version")
    r""" The firmware_version field of the shelf_frus.

Example: 191.0 """

    id = Size(data_key="id")
    r""" The id field of the shelf_frus. """

    installed = fields.Boolean(data_key="installed")
    r""" The installed field of the shelf_frus.

Example: true """

    part_number = fields.Str(data_key="part_number")
    r""" The part_number field of the shelf_frus.

Example: 111-00690+A2 """

    psu = fields.Nested("netapp_ontap.models.shelf_psu.ShelfPsuSchema", unknown=EXCLUDE, data_key="psu")
    r""" The psu field of the shelf_frus. """

    serial_number = fields.Str(data_key="serial_number")
    r""" The serial_number field of the shelf_frus.

Example: 8000166294 """

    state = fields.Str(data_key="state")
    r""" The state field of the shelf_frus.

Valid choices:

* ok
* error """

    type = fields.Str(data_key="type")
    r""" The type field of the shelf_frus.

Valid choices:

* module
* psu """

    @property
    def resource(self):
        return ShelfFrus

    gettable_fields = [
        "firmware_version",
        "id",
        "installed",
        "part_number",
        "psu",
        "serial_number",
        "state",
        "type",
    ]
    """firmware_version,id,installed,part_number,psu,serial_number,state,type,"""

    patchable_fields = [
        "firmware_version",
        "id",
        "installed",
        "part_number",
        "psu",
        "serial_number",
        "state",
        "type",
    ]
    """firmware_version,id,installed,part_number,psu,serial_number,state,type,"""

    postable_fields = [
        "firmware_version",
        "id",
        "installed",
        "part_number",
        "psu",
        "serial_number",
        "state",
        "type",
    ]
    """firmware_version,id,installed,part_number,psu,serial_number,state,type,"""


class ShelfFrus(Resource):

    _schema = ShelfFrusSchema
