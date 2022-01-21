r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareDisk", "FirmwareDiskSchema"]
__pdoc__ = {
    "FirmwareDiskSchema.resource": False,
    "FirmwareDisk": False,
}


class FirmwareDiskSchema(ResourceSchema):
    """The fields of the FirmwareDisk object"""

    average_duration_per_disk = Size(data_key="average_duration_per_disk")
    r""" Average firmware update duration per disk (in seconds).

Example: 120 """

    num_waiting_download = Size(data_key="num_waiting_download")
    r""" The number of disks waiting to download the firmware update.

Example: 0 """

    total_completion_estimate = Size(data_key="total_completion_estimate")
    r""" Estimated firmware update duration to completion (in minutes).

Example: 0 """

    update_status = fields.Str(data_key="update_status")
    r""" Status of the background disk firmware update.

Valid choices:

* running
* idle """

    @property
    def resource(self):
        return FirmwareDisk

    gettable_fields = [
        "average_duration_per_disk",
        "num_waiting_download",
        "total_completion_estimate",
        "update_status",
    ]
    """average_duration_per_disk,num_waiting_download,total_completion_estimate,update_status,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareDisk(Resource):

    _schema = FirmwareDiskSchema
