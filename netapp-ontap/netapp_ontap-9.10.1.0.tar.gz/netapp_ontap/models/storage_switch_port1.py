r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchPort1", "StorageSwitchPort1Schema"]
__pdoc__ = {
    "StorageSwitchPort1Schema.resource": False,
    "StorageSwitchPort1": False,
}


class StorageSwitchPort1Schema(ResourceSchema):
    """The fields of the StorageSwitchPort1 object"""

    id = fields.Str(data_key="id")
    r""" Storage switch zone port ID """

    name = fields.Str(data_key="name")
    r""" Storage switch zone port """

    @property
    def resource(self):
        return StorageSwitchPort1

    gettable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    patchable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    postable_fields = [
        "id",
        "name",
    ]
    """id,name,"""


class StorageSwitchPort1(Resource):

    _schema = StorageSwitchPort1Schema
