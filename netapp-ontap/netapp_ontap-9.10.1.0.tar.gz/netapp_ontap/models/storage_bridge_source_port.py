r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeSourcePort", "StorageBridgeSourcePortSchema"]
__pdoc__ = {
    "StorageBridgeSourcePortSchema.resource": False,
    "StorageBridgeSourcePort": False,
}


class StorageBridgeSourcePortSchema(ResourceSchema):
    """The fields of the StorageBridgeSourcePort object"""

    id = fields.Str(data_key="id")
    r""" Initiator side switch port id

Example: 100050eb1a238892 """

    name = fields.Str(data_key="name")
    r""" Initiator side switch port name

Example: rtp-fc03-41kk11:1 """

    @property
    def resource(self):
        return StorageBridgeSourcePort

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


class StorageBridgeSourcePort(Resource):

    _schema = StorageBridgeSourcePortSchema
