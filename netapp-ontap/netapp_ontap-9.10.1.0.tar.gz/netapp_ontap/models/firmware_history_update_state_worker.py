r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareHistoryUpdateStateWorker", "FirmwareHistoryUpdateStateWorkerSchema"]
__pdoc__ = {
    "FirmwareHistoryUpdateStateWorkerSchema.resource": False,
    "FirmwareHistoryUpdateStateWorker": False,
}


class FirmwareHistoryUpdateStateWorkerSchema(ResourceSchema):
    """The fields of the FirmwareHistoryUpdateStateWorker object"""

    error = fields.Nested("netapp_ontap.models.firmware_history_update_state_error.FirmwareHistoryUpdateStateErrorSchema", unknown=EXCLUDE, data_key="error")
    r""" The error field of the firmware_history_update_state_worker. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the firmware_history_update_state_worker. """

    state = fields.Str(data_key="state")
    r""" The state of each worker that a node is controlling.

Valid choices:

* idle
* working
* complete
* failed
* waiting_to_retry """

    @property
    def resource(self):
        return FirmwareHistoryUpdateStateWorker

    gettable_fields = [
        "error",
        "node.links",
        "node.name",
        "node.uuid",
        "state",
    ]
    """error,node.links,node.name,node.uuid,state,"""

    patchable_fields = [
        "error",
        "node.name",
        "node.uuid",
        "state",
    ]
    """error,node.name,node.uuid,state,"""

    postable_fields = [
        "error",
        "node.name",
        "node.uuid",
        "state",
    ]
    """error,node.name,node.uuid,state,"""


class FirmwareHistoryUpdateStateWorker(Resource):

    _schema = FirmwareHistoryUpdateStateWorkerSchema
