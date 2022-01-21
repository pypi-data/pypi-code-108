r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareHistoryUpdateState", "FirmwareHistoryUpdateStateSchema"]
__pdoc__ = {
    "FirmwareHistoryUpdateStateSchema.resource": False,
    "FirmwareHistoryUpdateState": False,
}


class FirmwareHistoryUpdateStateSchema(ResourceSchema):
    """The fields of the FirmwareHistoryUpdateState object"""

    worker = fields.Nested("netapp_ontap.models.firmware_history_update_state_worker.FirmwareHistoryUpdateStateWorkerSchema", unknown=EXCLUDE, data_key="worker")
    r""" The worker field of the firmware_history_update_state. """

    @property
    def resource(self):
        return FirmwareHistoryUpdateState

    gettable_fields = [
        "worker",
    ]
    """worker,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareHistoryUpdateState(Resource):

    _schema = FirmwareHistoryUpdateStateSchema
