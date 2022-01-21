r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ClusterSpaceBlockStorageMedias", "ClusterSpaceBlockStorageMediasSchema"]
__pdoc__ = {
    "ClusterSpaceBlockStorageMediasSchema.resource": False,
    "ClusterSpaceBlockStorageMedias": False,
}


class ClusterSpaceBlockStorageMediasSchema(ResourceSchema):
    """The fields of the ClusterSpaceBlockStorageMedias object"""

    available = Size(data_key="available")
    r""" Available space """

    efficiency = fields.Nested("netapp_ontap.models.space_efficiency.SpaceEfficiencySchema", unknown=EXCLUDE, data_key="efficiency")
    r""" Storage Efficiency """

    efficiency_without_snapshots = fields.Nested("netapp_ontap.models.space_efficiency.SpaceEfficiencySchema", unknown=EXCLUDE, data_key="efficiency_without_snapshots")
    r""" Storage efficiency that does not include the savings provided by Snapshot copies. """

    efficiency_without_snapshots_flexclones = fields.Nested("netapp_ontap.models.space_efficiency.SpaceEfficiencySchema", unknown=EXCLUDE, data_key="efficiency_without_snapshots_flexclones")
    r""" Storage efficiency that does not include the savings provided by Snapshot copies and FlexClones. """

    physical_used = Size(data_key="physical_used")
    r""" Total physical used space """

    size = Size(data_key="size")
    r""" Total space """

    type = fields.Str(data_key="type")
    r""" The type of media being used

Valid choices:

* hdd
* hybrid
* lun
* ssd
* vmdisk """

    used = Size(data_key="used")
    r""" Used space """

    @property
    def resource(self):
        return ClusterSpaceBlockStorageMedias

    gettable_fields = [
        "available",
        "efficiency",
        "efficiency_without_snapshots",
        "efficiency_without_snapshots_flexclones",
        "physical_used",
        "size",
        "type",
        "used",
    ]
    """available,efficiency,efficiency_without_snapshots,efficiency_without_snapshots_flexclones,physical_used,size,type,used,"""

    patchable_fields = [
        "available",
        "efficiency",
        "efficiency_without_snapshots",
        "efficiency_without_snapshots_flexclones",
        "physical_used",
        "size",
        "type",
        "used",
    ]
    """available,efficiency,efficiency_without_snapshots,efficiency_without_snapshots_flexclones,physical_used,size,type,used,"""

    postable_fields = [
        "available",
        "efficiency",
        "efficiency_without_snapshots",
        "efficiency_without_snapshots_flexclones",
        "physical_used",
        "size",
        "type",
        "used",
    ]
    """available,efficiency,efficiency_without_snapshots,efficiency_without_snapshots_flexclones,physical_used,size,type,used,"""


class ClusterSpaceBlockStorageMedias(Resource):

    _schema = ClusterSpaceBlockStorageMediasSchema
