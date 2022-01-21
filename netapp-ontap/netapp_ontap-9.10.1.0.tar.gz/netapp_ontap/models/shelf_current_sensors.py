r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfCurrentSensors", "ShelfCurrentSensorsSchema"]
__pdoc__ = {
    "ShelfCurrentSensorsSchema.resource": False,
    "ShelfCurrentSensors": False,
}


class ShelfCurrentSensorsSchema(ResourceSchema):
    """The fields of the ShelfCurrentSensors object"""

    current = Size(data_key="current")
    r""" Current, in milliamps

Example: 14410 """

    id = Size(data_key="id")
    r""" The id field of the shelf_current_sensors.

Example: 1 """

    location = fields.Str(data_key="location")
    r""" The location field of the shelf_current_sensors.

Example: rear of the shelf on the lower left power supply """

    state = fields.Str(data_key="state")
    r""" The state field of the shelf_current_sensors.

Valid choices:

* ok
* error """

    @property
    def resource(self):
        return ShelfCurrentSensors

    gettable_fields = [
        "current",
        "id",
        "location",
        "state",
    ]
    """current,id,location,state,"""

    patchable_fields = [
        "current",
        "id",
        "location",
        "state",
    ]
    """current,id,location,state,"""

    postable_fields = [
        "current",
        "id",
        "location",
        "state",
    ]
    """current,id,location,state,"""


class ShelfCurrentSensors(Resource):

    _schema = ShelfCurrentSensorsSchema
