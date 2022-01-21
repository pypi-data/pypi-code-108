r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgePhy1", "StorageBridgePhy1Schema"]
__pdoc__ = {
    "StorageBridgePhy1Schema.resource": False,
    "StorageBridgePhy1": False,
}


class StorageBridgePhy1Schema(ResourceSchema):
    """The fields of the StorageBridgePhy1 object"""

    state = fields.Str(data_key="state")
    r""" Bridge SAS port PHY1 state """

    @property
    def resource(self):
        return StorageBridgePhy1

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


class StorageBridgePhy1(Resource):

    _schema = StorageBridgePhy1Schema
