r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareUpdateProgressState", "FirmwareUpdateProgressStateSchema"]
__pdoc__ = {
    "FirmwareUpdateProgressStateSchema.resource": False,
    "FirmwareUpdateProgressState": False,
}


class FirmwareUpdateProgressStateSchema(ResourceSchema):
    """The fields of the FirmwareUpdateProgressState object"""

    attempts = Size(data_key="attempts")
    r""" The attempts field of the firmware_update_progress_state.

Example: 3 """

    code = Size(data_key="code")
    r""" Code corresponding to the status message.

Example: 2228325 """

    message = fields.Str(data_key="message")
    r""" Error message returned when a cluster firmware update job fails.

Example: Cannot open local staging ZIP file disk_firmware.zip """

    status = fields.Str(data_key="status")
    r""" The status field of the firmware_update_progress_state.

Valid choices:

* idle
* working
* complete
* failed
* waiting_to_retry """

    worker_node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="worker_node")
    r""" The worker_node field of the firmware_update_progress_state. """

    @property
    def resource(self):
        return FirmwareUpdateProgressState

    gettable_fields = [
        "attempts",
        "code",
        "message",
        "status",
        "worker_node.links",
        "worker_node.name",
        "worker_node.uuid",
    ]
    """attempts,code,message,status,worker_node.links,worker_node.name,worker_node.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareUpdateProgressState(Resource):

    _schema = FirmwareUpdateProgressStateSchema
