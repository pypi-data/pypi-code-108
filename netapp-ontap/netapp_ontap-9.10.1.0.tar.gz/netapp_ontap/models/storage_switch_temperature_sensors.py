r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchTemperatureSensors", "StorageSwitchTemperatureSensorsSchema"]
__pdoc__ = {
    "StorageSwitchTemperatureSensorsSchema.resource": False,
    "StorageSwitchTemperatureSensors": False,
}


class StorageSwitchTemperatureSensorsSchema(ResourceSchema):
    """The fields of the StorageSwitchTemperatureSensors object"""

    name = fields.Str(data_key="name")
    r""" Temperature sensor name """

    reading = Size(data_key="reading")
    r""" Temperature sensor reading, in degrees celsius. """

    state = fields.Str(data_key="state")
    r""" Temperature sensor state

Valid choices:

* error
* ok """

    @property
    def resource(self):
        return StorageSwitchTemperatureSensors

    gettable_fields = [
        "name",
        "reading",
        "state",
    ]
    """name,reading,state,"""

    patchable_fields = [
        "name",
        "reading",
        "state",
    ]
    """name,reading,state,"""

    postable_fields = [
        "name",
        "reading",
        "state",
    ]
    """name,reading,state,"""


class StorageSwitchTemperatureSensors(Resource):

    _schema = StorageSwitchTemperatureSensorsSchema
