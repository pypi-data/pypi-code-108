r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfVoltageSensors", "ShelfVoltageSensorsSchema"]
__pdoc__ = {
    "ShelfVoltageSensorsSchema.resource": False,
    "ShelfVoltageSensors": False,
}


class ShelfVoltageSensorsSchema(ResourceSchema):
    """The fields of the ShelfVoltageSensors object"""

    id = Size(data_key="id")
    r""" The id field of the shelf_voltage_sensors.

Example: 1 """

    location = fields.Str(data_key="location")
    r""" The location field of the shelf_voltage_sensors.

Example: rear of the shelf on the lower left power supply """

    state = fields.Str(data_key="state")
    r""" The state field of the shelf_voltage_sensors.

Valid choices:

* ok
* error """

    voltage = fields.Number(data_key="voltage")
    r""" Voltage, in volts

Example: 12.18 """

    @property
    def resource(self):
        return ShelfVoltageSensors

    gettable_fields = [
        "id",
        "location",
        "state",
        "voltage",
    ]
    """id,location,state,voltage,"""

    patchable_fields = [
        "id",
        "location",
        "state",
        "voltage",
    ]
    """id,location,state,voltage,"""

    postable_fields = [
        "id",
        "location",
        "state",
        "voltage",
    ]
    """id,location,state,voltage,"""


class ShelfVoltageSensors(Resource):

    _schema = ShelfVoltageSensorsSchema
