r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareDqpRecordCount", "FirmwareDqpRecordCountSchema"]
__pdoc__ = {
    "FirmwareDqpRecordCountSchema.resource": False,
    "FirmwareDqpRecordCount": False,
}


class FirmwareDqpRecordCountSchema(ResourceSchema):
    """The fields of the FirmwareDqpRecordCount object"""

    alias = Size(data_key="alias")
    r""" Alias record count

Example: 200 """

    device = Size(data_key="device")
    r""" Device record count

Example: 29 """

    drive = Size(data_key="drive")
    r""" Drive record count

Example: 680 """

    system = Size(data_key="system")
    r""" System record count

Example: 3 """

    @property
    def resource(self):
        return FirmwareDqpRecordCount

    gettable_fields = [
        "alias",
        "device",
        "drive",
        "system",
    ]
    """alias,device,drive,system,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareDqpRecordCount(Resource):

    _schema = FirmwareDqpRecordCountSchema
