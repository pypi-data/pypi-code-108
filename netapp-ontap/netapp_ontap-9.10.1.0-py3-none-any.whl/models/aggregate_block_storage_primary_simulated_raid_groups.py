r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateBlockStoragePrimarySimulatedRaidGroups", "AggregateBlockStoragePrimarySimulatedRaidGroupsSchema"]
__pdoc__ = {
    "AggregateBlockStoragePrimarySimulatedRaidGroupsSchema.resource": False,
    "AggregateBlockStoragePrimarySimulatedRaidGroups": False,
}


class AggregateBlockStoragePrimarySimulatedRaidGroupsSchema(ResourceSchema):
    """The fields of the AggregateBlockStoragePrimarySimulatedRaidGroups object"""

    data_disk_count = Size(data_key="data_disk_count")
    r""" Number of data disks in RAID group. """

    is_partition = fields.Boolean(data_key="is_partition")
    r""" Indicates whether the disk is partitioned (true) or whole (false). """

    name = fields.Str(data_key="name")
    r""" Name of the raid group. """

    parity_disk_count = Size(data_key="parity_disk_count")
    r""" Number of parity disks in RAID group. """

    raid_type = fields.Str(data_key="raid_type")
    r""" RAID type of the aggregate.

Valid choices:

* raid_dp
* raid_tec
* raid0
* raid4
* raid_ep """

    usable_size = Size(data_key="usable_size")
    r""" Usable size of each disk, in bytes. """

    @property
    def resource(self):
        return AggregateBlockStoragePrimarySimulatedRaidGroups

    gettable_fields = [
        "data_disk_count",
        "is_partition",
        "name",
        "parity_disk_count",
        "raid_type",
        "usable_size",
    ]
    """data_disk_count,is_partition,name,parity_disk_count,raid_type,usable_size,"""

    patchable_fields = [
        "data_disk_count",
        "is_partition",
        "name",
        "parity_disk_count",
        "raid_type",
        "usable_size",
    ]
    """data_disk_count,is_partition,name,parity_disk_count,raid_type,usable_size,"""

    postable_fields = [
        "data_disk_count",
        "is_partition",
        "name",
        "parity_disk_count",
        "raid_type",
        "usable_size",
    ]
    """data_disk_count,is_partition,name,parity_disk_count,raid_type,usable_size,"""


class AggregateBlockStoragePrimarySimulatedRaidGroups(Resource):

    _schema = AggregateBlockStoragePrimarySimulatedRaidGroupsSchema
