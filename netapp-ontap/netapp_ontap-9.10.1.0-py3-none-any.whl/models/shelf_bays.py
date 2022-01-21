r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfBays", "ShelfBaysSchema"]
__pdoc__ = {
    "ShelfBaysSchema.resource": False,
    "ShelfBays": False,
}


class ShelfBaysSchema(ResourceSchema):
    """The fields of the ShelfBays object"""

    has_disk = fields.Boolean(data_key="has_disk")
    r""" The has_disk field of the shelf_bays. """

    id = Size(data_key="id")
    r""" The id field of the shelf_bays.

Example: 0 """

    state = fields.Str(data_key="state")
    r""" The state field of the shelf_bays.

Valid choices:

* unknown
* ok
* error """

    type = fields.Str(data_key="type")
    r""" The type field of the shelf_bays.

Valid choices:

* unknown
* single_disk
* multi_lun """

    @property
    def resource(self):
        return ShelfBays

    gettable_fields = [
        "has_disk",
        "id",
        "state",
        "type",
    ]
    """has_disk,id,state,type,"""

    patchable_fields = [
        "has_disk",
        "id",
        "state",
        "type",
    ]
    """has_disk,id,state,type,"""

    postable_fields = [
        "has_disk",
        "id",
        "state",
        "type",
    ]
    """has_disk,id,state,type,"""


class ShelfBays(Resource):

    _schema = ShelfBaysSchema
