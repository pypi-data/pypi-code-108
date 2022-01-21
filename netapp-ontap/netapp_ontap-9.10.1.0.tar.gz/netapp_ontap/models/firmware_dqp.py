r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareDqp", "FirmwareDqpSchema"]
__pdoc__ = {
    "FirmwareDqpSchema.resource": False,
    "FirmwareDqp": False,
}


class FirmwareDqpSchema(ResourceSchema):
    """The fields of the FirmwareDqp object"""

    file_name = fields.Str(data_key="file_name")
    r""" Firmware file name

Example: qual_devices_v3 """

    record_count = fields.Nested("netapp_ontap.models.firmware_dqp_record_count.FirmwareDqpRecordCountSchema", unknown=EXCLUDE, data_key="record_count")
    r""" The record_count field of the firmware_dqp. """

    revision = fields.Str(data_key="revision")
    r""" Firmware revision

Example: 20200117 """

    version = fields.Str(data_key="version")
    r""" Firmware version

Example: 3.18 """

    @property
    def resource(self):
        return FirmwareDqp

    gettable_fields = [
        "file_name",
        "record_count",
        "revision",
        "version",
    ]
    """file_name,record_count,revision,version,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareDqp(Resource):

    _schema = FirmwareDqpSchema
