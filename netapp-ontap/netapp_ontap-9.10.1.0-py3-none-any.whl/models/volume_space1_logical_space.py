r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeSpace1LogicalSpace", "VolumeSpace1LogicalSpaceSchema"]
__pdoc__ = {
    "VolumeSpace1LogicalSpaceSchema.resource": False,
    "VolumeSpace1LogicalSpace": False,
}


class VolumeSpace1LogicalSpaceSchema(ResourceSchema):
    """The fields of the VolumeSpace1LogicalSpace object"""

    available = Size(data_key="available")
    r""" The amount of space available in this volume with storage efficiency space considered used, in bytes. """

    enforcement = fields.Boolean(data_key="enforcement")
    r""" Specifies whether space accounting for operations on the volume is done along with storage efficiency. """

    reporting = fields.Boolean(data_key="reporting")
    r""" Specifies whether space reporting on the volume is done along with storage efficiency. """

    used = Size(data_key="used")
    r""" SUM of (physical-used, shared_refs, compression_saved_in_plane0, vbn_zero, future_blk_cnt), in bytes. """

    used_by_afs = Size(data_key="used_by_afs")
    r""" The virtual space used by AFS alone (includes volume reserves) and along with storage efficiency, in bytes. """

    used_by_snapshots = Size(data_key="used_by_snapshots")
    r""" Size that is logically used across all Snapshot copies in the volume, in bytes. """

    used_percent = Size(data_key="used_percent")
    r""" SUM of (physical-used, shared_refs, compression_saved_in_plane0, vbn_zero, future_blk_cnt), as a percentage. """

    @property
    def resource(self):
        return VolumeSpace1LogicalSpace

    gettable_fields = [
        "available",
        "enforcement",
        "reporting",
        "used",
        "used_by_afs",
        "used_by_snapshots",
        "used_percent",
    ]
    """available,enforcement,reporting,used,used_by_afs,used_by_snapshots,used_percent,"""

    patchable_fields = [
        "enforcement",
        "reporting",
    ]
    """enforcement,reporting,"""

    postable_fields = [
        "enforcement",
        "reporting",
    ]
    """enforcement,reporting,"""


class VolumeSpace1LogicalSpace(Resource):

    _schema = VolumeSpace1LogicalSpaceSchema
