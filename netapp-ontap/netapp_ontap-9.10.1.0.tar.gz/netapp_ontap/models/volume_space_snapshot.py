r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeSpaceSnapshot", "VolumeSpaceSnapshotSchema"]
__pdoc__ = {
    "VolumeSpaceSnapshotSchema.resource": False,
    "VolumeSpaceSnapshot": False,
}


class VolumeSpaceSnapshotSchema(ResourceSchema):
    """The fields of the VolumeSpaceSnapshot object"""

    autodelete_enabled = fields.Boolean(data_key="autodelete_enabled")
    r""" Specifies whether Snapshot copy autodelete is currently enabled on this volume. """

    reserve_percent = Size(data_key="reserve_percent")
    r""" The space that has been set aside as a reserve for Snapshot copy usage, in percent. """

    used = Size(data_key="used")
    r""" The total space used by Snapshot copies in the volume, in bytes. """

    @property
    def resource(self):
        return VolumeSpaceSnapshot

    gettable_fields = [
        "reserve_percent",
        "used",
    ]
    """reserve_percent,used,"""

    patchable_fields = [
        "autodelete_enabled",
        "reserve_percent",
    ]
    """autodelete_enabled,reserve_percent,"""

    postable_fields = [
        "reserve_percent",
    ]
    """reserve_percent,"""


class VolumeSpaceSnapshot(Resource):

    _schema = VolumeSpaceSnapshotSchema
