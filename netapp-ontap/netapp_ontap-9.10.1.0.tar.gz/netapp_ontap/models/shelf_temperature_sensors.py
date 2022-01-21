r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfTemperatureSensors", "ShelfTemperatureSensorsSchema"]
__pdoc__ = {
    "ShelfTemperatureSensorsSchema.resource": False,
    "ShelfTemperatureSensors": False,
}


class ShelfTemperatureSensorsSchema(ResourceSchema):
    """The fields of the ShelfTemperatureSensors object"""

    ambient = fields.Boolean(data_key="ambient")
    r""" Sensor that measures the ambient temperature

Example: false """

    id = Size(data_key="id")
    r""" The id field of the shelf_temperature_sensors.

Example: 1 """

    location = fields.Str(data_key="location")
    r""" The location field of the shelf_temperature_sensors.

Example: temp sensor on midplane left """

    state = fields.Str(data_key="state")
    r""" The state field of the shelf_temperature_sensors.

Valid choices:

* ok
* error """

    temperature = Size(data_key="temperature")
    r""" Temperature, in degrees Celsius

Example: 32 """

    threshold = fields.Nested("netapp_ontap.models.shelf_threshold.ShelfThresholdSchema", unknown=EXCLUDE, data_key="threshold")
    r""" The threshold field of the shelf_temperature_sensors. """

    @property
    def resource(self):
        return ShelfTemperatureSensors

    gettable_fields = [
        "ambient",
        "id",
        "location",
        "state",
        "temperature",
        "threshold",
    ]
    """ambient,id,location,state,temperature,threshold,"""

    patchable_fields = [
        "ambient",
        "id",
        "location",
        "state",
        "temperature",
        "threshold",
    ]
    """ambient,id,location,state,temperature,threshold,"""

    postable_fields = [
        "ambient",
        "id",
        "location",
        "state",
        "temperature",
        "threshold",
    ]
    """ambient,id,location,state,temperature,threshold,"""


class ShelfTemperatureSensors(Resource):

    _schema = ShelfTemperatureSensorsSchema
