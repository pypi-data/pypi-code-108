r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NdmpScsi", "NdmpScsiSchema"]
__pdoc__ = {
    "NdmpScsiSchema.resource": False,
    "NdmpScsi": False,
}


class NdmpScsiSchema(ResourceSchema):
    """The fields of the NdmpScsi object"""

    device_id = fields.Str(data_key="device_id")
    r""" Indicates the NDMP SCSI device ID. """

    host_adapter = Size(data_key="host_adapter")
    r""" Indicates the NDMP SCSI host adapter. """

    lun_id = Size(data_key="lun_id")
    r""" Indicates the NDMP SCSI LUN ID. """

    target_id = Size(data_key="target_id")
    r""" Indicates the NDMP SCSI target ID. """

    @property
    def resource(self):
        return NdmpScsi

    gettable_fields = [
        "device_id",
        "host_adapter",
        "lun_id",
        "target_id",
    ]
    """device_id,host_adapter,lun_id,target_id,"""

    patchable_fields = [
        "device_id",
        "host_adapter",
        "lun_id",
        "target_id",
    ]
    """device_id,host_adapter,lun_id,target_id,"""

    postable_fields = [
        "device_id",
        "host_adapter",
        "lun_id",
        "target_id",
    ]
    """device_id,host_adapter,lun_id,target_id,"""


class NdmpScsi(Resource):

    _schema = NdmpScsiSchema
