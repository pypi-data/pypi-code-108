r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgePhy3", "StorageBridgePhy3Schema"]
__pdoc__ = {
    "StorageBridgePhy3Schema.resource": False,
    "StorageBridgePhy3": False,
}


class StorageBridgePhy3Schema(ResourceSchema):
    """The fields of the StorageBridgePhy3 object"""

    state = fields.Str(data_key="state")
    r""" Bridge SAS port PHY3 state """

    @property
    def resource(self):
        return StorageBridgePhy3

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


class StorageBridgePhy3(Resource):

    _schema = StorageBridgePhy3Schema
