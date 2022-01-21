r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateBlockStorageHybridCache", "AggregateBlockStorageHybridCacheSchema"]
__pdoc__ = {
    "AggregateBlockStorageHybridCacheSchema.resource": False,
    "AggregateBlockStorageHybridCache": False,
}


class AggregateBlockStorageHybridCacheSchema(ResourceSchema):
    """The fields of the AggregateBlockStorageHybridCache object"""

    disk_count = Size(data_key="disk_count")
    r""" Number of disks used in the cache tier of the aggregate. Only provided when hybrid_cache.enabled is 'true'.

Example: 6 """

    enabled = fields.Boolean(data_key="enabled")
    r""" Specifies whether the aggregate uses HDDs with SSDs as a cache. """

    raid_type = fields.Str(data_key="raid_type")
    r""" RAID type for SSD cache of the aggregate. Only provided when hybrid_cache.enabled is 'true'.

Valid choices:

* raid_dp
* raid_tec
* raid4 """

    size = Size(data_key="size")
    r""" Total usable space in bytes of SSD cache. Only provided when hybrid_cache.enabled is 'true'.

Example: 1612709888 """

    used = Size(data_key="used")
    r""" Space used in bytes of SSD cache. Only provided when hybrid_cache.enabled is 'true'.

Example: 26501122 """

    @property
    def resource(self):
        return AggregateBlockStorageHybridCache

    gettable_fields = [
        "disk_count",
        "enabled",
        "raid_type",
        "size",
        "used",
    ]
    """disk_count,enabled,raid_type,size,used,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AggregateBlockStorageHybridCache(Resource):

    _schema = AggregateBlockStorageHybridCacheSchema
