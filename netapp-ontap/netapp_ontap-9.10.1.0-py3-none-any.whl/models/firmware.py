r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Firmware", "FirmwareSchema"]
__pdoc__ = {
    "FirmwareSchema.resource": False,
    "Firmware": False,
}


class FirmwareSchema(ResourceSchema):
    """The fields of the Firmware object"""

    cluster_fw_progress = fields.List(fields.Nested("netapp_ontap.models.firmware_update_progress.FirmwareUpdateProgressSchema", unknown=EXCLUDE), data_key="cluster_fw_progress")
    r""" The cluster_fw_progress field of the firmware. """

    disk = fields.Nested("netapp_ontap.models.firmware_disk.FirmwareDiskSchema", unknown=EXCLUDE, data_key="disk")
    r""" The disk field of the firmware. """

    dqp = fields.Nested("netapp_ontap.models.firmware_dqp.FirmwareDqpSchema", unknown=EXCLUDE, data_key="dqp")
    r""" The dqp field of the firmware. """

    shelf = fields.Nested("netapp_ontap.models.firmware_shelf.FirmwareShelfSchema", unknown=EXCLUDE, data_key="shelf")
    r""" The shelf field of the firmware. """

    sp_bmc = fields.Nested("netapp_ontap.models.firmware_sp_bmc.FirmwareSpBmcSchema", unknown=EXCLUDE, data_key="sp_bmc")
    r""" The sp_bmc field of the firmware. """

    @property
    def resource(self):
        return Firmware

    gettable_fields = [
        "cluster_fw_progress",
        "disk",
        "dqp",
        "shelf",
        "sp_bmc",
    ]
    """cluster_fw_progress,disk,dqp,shelf,sp_bmc,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class Firmware(Resource):

    _schema = FirmwareSchema
