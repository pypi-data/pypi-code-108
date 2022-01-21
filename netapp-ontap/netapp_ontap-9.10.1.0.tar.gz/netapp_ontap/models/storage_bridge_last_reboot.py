r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageBridgeLastReboot", "StorageBridgeLastRebootSchema"]
__pdoc__ = {
    "StorageBridgeLastRebootSchema.resource": False,
    "StorageBridgeLastReboot": False,
}


class StorageBridgeLastRebootSchema(ResourceSchema):
    """The fields of the StorageBridgeLastReboot object"""

    reason = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="reason")
    r""" The error message and code explaining why the bridge rebooted. """

    time = ImpreciseDateTime(data_key="time")
    r""" The time field of the storage_bridge_last_reboot.

Example: 2020-12-09T05:47:58.000+0000 """

    @property
    def resource(self):
        return StorageBridgeLastReboot

    gettable_fields = [
        "reason",
        "time",
    ]
    """reason,time,"""

    patchable_fields = [
        "time",
    ]
    """time,"""

    postable_fields = [
        "time",
    ]
    """time,"""


class StorageBridgeLastReboot(Resource):

    _schema = StorageBridgeLastRebootSchema
