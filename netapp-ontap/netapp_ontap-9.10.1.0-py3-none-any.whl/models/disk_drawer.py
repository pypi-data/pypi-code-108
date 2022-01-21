r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["DiskDrawer", "DiskDrawerSchema"]
__pdoc__ = {
    "DiskDrawerSchema.resource": False,
    "DiskDrawer": False,
}


class DiskDrawerSchema(ResourceSchema):
    """The fields of the DiskDrawer object"""

    id = Size(data_key="id")
    r""" The id field of the disk_drawer. """

    slot = Size(data_key="slot")
    r""" The slot field of the disk_drawer. """

    @property
    def resource(self):
        return DiskDrawer

    gettable_fields = [
        "id",
        "slot",
    ]
    """id,slot,"""

    patchable_fields = [
        "id",
        "slot",
    ]
    """id,slot,"""

    postable_fields = [
        "id",
        "slot",
    ]
    """id,slot,"""


class DiskDrawer(Resource):

    _schema = DiskDrawerSchema
