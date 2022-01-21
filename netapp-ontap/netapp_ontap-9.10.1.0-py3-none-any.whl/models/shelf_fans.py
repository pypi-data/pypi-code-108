r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfFans", "ShelfFansSchema"]
__pdoc__ = {
    "ShelfFansSchema.resource": False,
    "ShelfFans": False,
}


class ShelfFansSchema(ResourceSchema):
    """The fields of the ShelfFans object"""

    id = Size(data_key="id")
    r""" The id field of the shelf_fans.

Example: 1 """

    location = fields.Str(data_key="location")
    r""" The location field of the shelf_fans.

Example: rear of the shelf on the lower left power supply """

    rpm = Size(data_key="rpm")
    r""" The rpm field of the shelf_fans.

Example: 3020 """

    state = fields.Str(data_key="state")
    r""" The state field of the shelf_fans.

Valid choices:

* ok
* error """

    @property
    def resource(self):
        return ShelfFans

    gettable_fields = [
        "id",
        "location",
        "rpm",
        "state",
    ]
    """id,location,rpm,state,"""

    patchable_fields = [
        "id",
        "location",
        "rpm",
        "state",
    ]
    """id,location,rpm,state,"""

    postable_fields = [
        "id",
        "location",
        "rpm",
        "state",
    ]
    """id,location,rpm,state,"""


class ShelfFans(Resource):

    _schema = ShelfFansSchema
