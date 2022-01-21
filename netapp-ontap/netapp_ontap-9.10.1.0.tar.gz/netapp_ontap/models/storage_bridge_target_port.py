r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeTargetPort", "StorageBridgeTargetPortSchema"]
__pdoc__ = {
    "StorageBridgeTargetPortSchema.resource": False,
    "StorageBridgeTargetPort": False,
}


class StorageBridgeTargetPortSchema(ResourceSchema):
    """The fields of the StorageBridgeTargetPort object"""

    id = fields.Str(data_key="id")
    r""" Target side switch port id

Example: 100050eb1a238892 """

    name = fields.Str(data_key="name")
    r""" Target side switch port name

Example: rtp-fc03-41kk11:6 """

    wwn = fields.Str(data_key="wwn")
    r""" Target side switch port world wide name

Example: 2100001086a54100 """

    @property
    def resource(self):
        return StorageBridgeTargetPort

    gettable_fields = [
        "id",
        "name",
        "wwn",
    ]
    """id,name,wwn,"""

    patchable_fields = [
        "id",
        "name",
        "wwn",
    ]
    """id,name,wwn,"""

    postable_fields = [
        "id",
        "name",
        "wwn",
    ]
    """id,name,wwn,"""


class StorageBridgeTargetPort(Resource):

    _schema = StorageBridgeTargetPortSchema
