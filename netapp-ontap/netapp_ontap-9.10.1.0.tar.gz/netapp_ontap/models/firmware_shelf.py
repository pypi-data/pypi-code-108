r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareShelf", "FirmwareShelfSchema"]
__pdoc__ = {
    "FirmwareShelfSchema.resource": False,
    "FirmwareShelf": False,
}


class FirmwareShelfSchema(ResourceSchema):
    """The fields of the FirmwareShelf object"""

    in_progress_count = Size(data_key="in_progress_count")
    r""" The in_progress_count field of the firmware_shelf.

Example: 2 """

    update_status = fields.Str(data_key="update_status")
    r""" Status of the shelf firmware update.

Valid choices:

* running
* idle """

    @property
    def resource(self):
        return FirmwareShelf

    gettable_fields = [
        "in_progress_count",
        "update_status",
    ]
    """in_progress_count,update_status,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareShelf(Resource):

    _schema = FirmwareShelfSchema
