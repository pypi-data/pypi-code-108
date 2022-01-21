r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgePhy4", "StorageBridgePhy4Schema"]
__pdoc__ = {
    "StorageBridgePhy4Schema.resource": False,
    "StorageBridgePhy4": False,
}


class StorageBridgePhy4Schema(ResourceSchema):
    """The fields of the StorageBridgePhy4 object"""

    state = fields.Str(data_key="state")
    r""" Bridge SAS port PHY4 state """

    @property
    def resource(self):
        return StorageBridgePhy4

    gettable_fields = [
        "state",
    ]
    """state,"""

    patchable_fields = [
        "state",
    ]
    """state,"""

    postable_fields = [
        "state",
    ]
    """state,"""


class StorageBridgePhy4(Resource):

    _schema = StorageBridgePhy4Schema
