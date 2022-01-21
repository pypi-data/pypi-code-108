r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AntiRansomwareVolumeSpace", "AntiRansomwareVolumeSpaceSchema"]
__pdoc__ = {
    "AntiRansomwareVolumeSpaceSchema.resource": False,
    "AntiRansomwareVolumeSpace": False,
}


class AntiRansomwareVolumeSpaceSchema(ResourceSchema):
    """The fields of the AntiRansomwareVolumeSpace object"""

    snapshot_count = Size(data_key="snapshot_count")
    r""" Total number of Anti-ransomware backup Snapshot copies. """

    used = Size(data_key="used")
    r""" Total space in bytes used by the Anti-ransomware feature. """

    used_by_logs = Size(data_key="used_by_logs")
    r""" Space in bytes used by the Anti-ransomware analytics logs. """

    used_by_snapshots = Size(data_key="used_by_snapshots")
    r""" Space in bytes used by the Anti-ransomware backup Snapshot copies. """

    @property
    def resource(self):
        return AntiRansomwareVolumeSpace

    gettable_fields = [
        "snapshot_count",
        "used",
        "used_by_logs",
        "used_by_snapshots",
    ]
    """snapshot_count,used,used_by_logs,used_by_snapshots,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AntiRansomwareVolumeSpace(Resource):

    _schema = AntiRansomwareVolumeSpaceSchema
