r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeSpace1", "VolumeSpace1Schema"]
__pdoc__ = {
    "VolumeSpace1Schema.resource": False,
    "VolumeSpace1": False,
}


class VolumeSpace1Schema(ResourceSchema):
    """The fields of the VolumeSpace1 object"""

    afs_total = Size(data_key="afs_total")
    r""" Total size of AFS, excluding snap-reserve, in bytes. """

    available = Size(data_key="available")
    r""" The available space, in bytes. """

    available_percent = Size(data_key="available_percent")
    r""" The space available, as a percent. """

    block_storage_inactive_user_data = Size(data_key="block_storage_inactive_user_data")
    r""" The size that is physically used in the block storage of the volume and has a cold temperature. In bytes. This parameter is only supported if the volume is in an aggregate that is either attached to a cloud store or could be attached to a cloud store. """

    block_storage_inactive_user_data_percent = Size(data_key="block_storage_inactive_user_data_percent")
    r""" Percentage of size that is physically used in the performance tier of the volume. """

    capacity_tier_footprint = Size(data_key="capacity_tier_footprint")
    r""" Space used by capacity tier for this volume in the FabricPool aggregate, in bytes. """

    cross_volume_dedupe_metafiles_footprint = Size(data_key="cross_volume_dedupe_metafiles_footprint")
    r""" Cross volume deduplication metadata footprint, in bytes. """

    cross_volume_dedupe_metafiles_temporary_footprint = Size(data_key="cross_volume_dedupe_metafiles_temporary_footprint")
    r""" Cross volume temporary deduplication metadata footprint, in bytes. """

    dedupe_metafiles_footprint = Size(data_key="dedupe_metafiles_footprint")
    r""" Deduplication metadata footprint, in bytes. """

    dedupe_metafiles_temporary_footprint = Size(data_key="dedupe_metafiles_temporary_footprint")
    r""" Temporary deduplication metadata footprint, in bytes. """

    delayed_free_footprint = Size(data_key="delayed_free_footprint")
    r""" Delayed free blocks footprint, in bytes. """

    expected_available = Size(data_key="expected_available")
    r""" Size that should be available for the volume, irrespective of available size in the aggregate, in bytes. """

    file_operation_metadata = Size(data_key="file_operation_metadata")
    r""" File operation metadata footprint, in bytes. """

    filesystem_size = Size(data_key="filesystem_size")
    r""" Total usable size of the volume, in bytes. """

    filesystem_size_fixed = fields.Boolean(data_key="filesystem_size_fixed")
    r""" Specifies whether the file system is to remain of the same size when set to true or to grow when set to false. This option is automatically set to true when a volume becomes SnapMirrored. """

    footprint = Size(data_key="footprint")
    r""" Data used for this volume in the aggregate, in bytes. """

    fractional_reserve = Size(data_key="fractional_reserve")
    r""" Used to change the amount of space reserved for overwrites of reserved objects in a volume. """

    full_threshold_percent = Size(data_key="full_threshold_percent")
    r""" Volume full threshold percentage at which EMS warnings can be sent. """

    local_tier_footprint = Size(data_key="local_tier_footprint")
    r""" Space used by the local tier for this volume in the aggregate, in bytes. """

    logical_space = fields.Nested("netapp_ontap.models.volume_space1_logical_space.VolumeSpace1LogicalSpaceSchema", unknown=EXCLUDE, data_key="logical_space")
    r""" The logical_space field of the volume_space1. """

    metadata = Size(data_key="metadata")
    r""" Space used by the volume metadata in the aggregate, in bytes. """

    nearly_full_threshold_percent = Size(data_key="nearly_full_threshold_percent")
    r""" Volume nearly full threshold percentage at which EMS warnings can be sent. """

    over_provisioned = Size(data_key="over_provisioned")
    r""" The amount of space not available for this volume in the aggregate, in bytes. """

    overwrite_reserve = Size(data_key="overwrite_reserve")
    r""" Reserved space for overwrites, in bytes. """

    overwrite_reserve_used = Size(data_key="overwrite_reserve_used")
    r""" Overwrite logical reserve space used, in bytes. """

    percent_used = Size(data_key="percent_used")
    r""" Percentage of the volume size that is used. """

    performance_tier_footprint = Size(data_key="performance_tier_footprint")
    r""" Space used by the performance tier for this volume in the FabricPool aggregate, in bytes. """

    physical_used = Size(data_key="physical_used")
    r""" Size that is physically used in the volume, in bytes. """

    physical_used_percent = Size(data_key="physical_used_percent")
    r""" Size that is physically used in the volume, as a percentage. """

    size = Size(data_key="size")
    r""" Total provisioned size. The default size is equal to the minimum size of 20MB, in bytes. """

    size_available_for_snapshots = Size(data_key="size_available_for_snapshots")
    r""" Available space for Snapshot copies from snap-reserve, in bytes. """

    snapmirror_destination_footprint = Size(data_key="snapmirror_destination_footprint")
    r""" SnapMirror destination footprint, in bytes. """

    snapshot = fields.Nested("netapp_ontap.models.volume_space1_snapshot.VolumeSpace1SnapshotSchema", unknown=EXCLUDE, data_key="snapshot")
    r""" The snapshot field of the volume_space1. """

    snapshot_reserve_unusable = Size(data_key="snapshot_reserve_unusable")
    r""" Snapshot reserve that is not available for Snapshot copy creation, in bytes. """

    snapshot_spill = Size(data_key="snapshot_spill")
    r""" Space used by the snapshot copies beyond the snap-reserve, in bytes. """

    total_footprint = Size(data_key="total_footprint")
    r""" Data and metadata used for this volume in the aggregate, in bytes. """

    used = Size(data_key="used")
    r""" The virtual space used (includes volume reserves) before storage efficiency, in bytes. """

    used_by_afs = Size(data_key="used_by_afs")
    r""" The space used by Active Filesystem, in bytes. """

    user_data = Size(data_key="user_data")
    r""" User data, in bytes. """

    volume_guarantee_footprint = Size(data_key="volume_guarantee_footprint")
    r""" Space reserved for future writes in the volume, in bytes. """

    @property
    def resource(self):
        return VolumeSpace1

    gettable_fields = [
        "afs_total",
        "available",
        "available_percent",
        "block_storage_inactive_user_data",
        "block_storage_inactive_user_data_percent",
        "capacity_tier_footprint",
        "cross_volume_dedupe_metafiles_footprint",
        "cross_volume_dedupe_metafiles_temporary_footprint",
        "dedupe_metafiles_footprint",
        "dedupe_metafiles_temporary_footprint",
        "delayed_free_footprint",
        "expected_available",
        "file_operation_metadata",
        "filesystem_size",
        "filesystem_size_fixed",
        "footprint",
        "fractional_reserve",
        "full_threshold_percent",
        "local_tier_footprint",
        "logical_space",
        "metadata",
        "nearly_full_threshold_percent",
        "over_provisioned",
        "overwrite_reserve",
        "overwrite_reserve_used",
        "percent_used",
        "performance_tier_footprint",
        "physical_used",
        "physical_used_percent",
        "size",
        "size_available_for_snapshots",
        "snapmirror_destination_footprint",
        "snapshot",
        "snapshot_reserve_unusable",
        "snapshot_spill",
        "total_footprint",
        "used",
        "used_by_afs",
        "user_data",
        "volume_guarantee_footprint",
    ]
    """afs_total,available,available_percent,block_storage_inactive_user_data,block_storage_inactive_user_data_percent,capacity_tier_footprint,cross_volume_dedupe_metafiles_footprint,cross_volume_dedupe_metafiles_temporary_footprint,dedupe_metafiles_footprint,dedupe_metafiles_temporary_footprint,delayed_free_footprint,expected_available,file_operation_metadata,filesystem_size,filesystem_size_fixed,footprint,fractional_reserve,full_threshold_percent,local_tier_footprint,logical_space,metadata,nearly_full_threshold_percent,over_provisioned,overwrite_reserve,overwrite_reserve_used,percent_used,performance_tier_footprint,physical_used,physical_used_percent,size,size_available_for_snapshots,snapmirror_destination_footprint,snapshot,snapshot_reserve_unusable,snapshot_spill,total_footprint,used,used_by_afs,user_data,volume_guarantee_footprint,"""

    patchable_fields = [
        "afs_total",
        "available_percent",
        "expected_available",
        "filesystem_size_fixed",
        "fractional_reserve",
        "full_threshold_percent",
        "logical_space",
        "nearly_full_threshold_percent",
        "physical_used",
        "physical_used_percent",
        "size",
        "snapshot",
        "used_by_afs",
    ]
    """afs_total,available_percent,expected_available,filesystem_size_fixed,fractional_reserve,full_threshold_percent,logical_space,nearly_full_threshold_percent,physical_used,physical_used_percent,size,snapshot,used_by_afs,"""

    postable_fields = [
        "afs_total",
        "available_percent",
        "expected_available",
        "filesystem_size_fixed",
        "fractional_reserve",
        "full_threshold_percent",
        "logical_space",
        "nearly_full_threshold_percent",
        "physical_used",
        "physical_used_percent",
        "size",
        "snapshot",
        "used_by_afs",
    ]
    """afs_total,available_percent,expected_available,filesystem_size_fixed,fractional_reserve,full_threshold_percent,logical_space,nearly_full_threshold_percent,physical_used,physical_used_percent,size,snapshot,used_by_afs,"""


class VolumeSpace1(Resource):

    _schema = VolumeSpace1Schema
