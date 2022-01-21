r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgePhy2", "StorageBridgePhy2Schema"]
__pdoc__ = {
    "StorageBridgePhy2Schema.resource": False,
    "StorageBridgePhy2": False,
}


class StorageBridgePhy2Schema(ResourceSchema):
    """The fields of the StorageBridgePhy2 object"""

    state = fields.Str(data_key="state")
    r""" Bridge SAS port PHY2 state """

    @property
    def resource(self):
        return StorageBridgePhy2

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


class StorageBridgePhy2(Resource):

    _schema = StorageBridgePhy2Schema
