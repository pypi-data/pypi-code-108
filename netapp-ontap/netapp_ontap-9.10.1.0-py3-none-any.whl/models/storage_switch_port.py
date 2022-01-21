r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchPort", "StorageSwitchPortSchema"]
__pdoc__ = {
    "StorageSwitchPortSchema.resource": False,
    "StorageSwitchPort": False,
}


class StorageSwitchPortSchema(ResourceSchema):
    """The fields of the StorageSwitchPort object"""

    name = fields.Str(data_key="name")
    r""" Storage switch port name """

    speed = Size(data_key="speed")
    r""" Storage switch port speed, in Gbps """

    @property
    def resource(self):
        return StorageSwitchPort

    gettable_fields = [
        "name",
        "speed",
    ]
    """name,speed,"""

    patchable_fields = [
        "name",
        "speed",
    ]
    """name,speed,"""

    postable_fields = [
        "name",
        "speed",
    ]
    """name,speed,"""


class StorageSwitchPort(Resource):

    _schema = StorageSwitchPortSchema
