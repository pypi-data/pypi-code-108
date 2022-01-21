r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateSpare", "AggregateSpareSchema"]
__pdoc__ = {
    "AggregateSpareSchema.resource": False,
    "AggregateSpare": False,
}


class AggregateSpareSchema(ResourceSchema):
    """The fields of the AggregateSpare object"""

    checksum_style = fields.Str(data_key="checksum_style")
    r""" The checksum type that has been assigned to the spares.

Valid choices:

* block
* advanced_zoned """

    disk_class = fields.Str(data_key="disk_class")
    r""" Disk class of spares.

Valid choices:

* unknown
* capacity
* performance
* archive
* solid_state
* array
* virtual
* data_center
* capacity_flash """

    disk_type = fields.Str(data_key="disk_type")
    r""" Type of disk.

Valid choices:

* fc
* lun
* nl_sas
* nvme_ssd
* sas
* sata
* scsi
* ssd
* ssd_cap
* ssd_zns
* vm_disk """

    is_partition = fields.Boolean(data_key="is_partition")
    r""" Indicates whether a disk is partitioned (true) or whole (false)

Example: true """

    layout_requirements = fields.List(fields.Nested("netapp_ontap.models.layout_requirement.LayoutRequirementSchema", unknown=EXCLUDE), data_key="layout_requirements")
    r""" Available RAID protections and their restrictions. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the aggregate_spare. """

    size = Size(data_key="size")
    r""" Usable size of each spare, in bytes.

Example: 10156769280 """

    syncmirror_pool = fields.Str(data_key="syncmirror_pool")
    r""" SyncMirror spare pool.

Valid choices:

* pool0
* pool1 """

    usable = Size(data_key="usable")
    r""" Total number of usable spares in the bucket. The usable count for each class of spares does not include reserved spare capacity recommended by ONTAP best practices.

Example: 9 """

    @property
    def resource(self):
        return AggregateSpare

    gettable_fields = [
        "checksum_style",
        "disk_class",
        "disk_type",
        "is_partition",
        "layout_requirements",
        "node.links",
        "node.name",
        "node.uuid",
        "size",
        "syncmirror_pool",
        "usable",
    ]
    """checksum_style,disk_class,disk_type,is_partition,layout_requirements,node.links,node.name,node.uuid,size,syncmirror_pool,usable,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""


class AggregateSpare(Resource):

    _schema = AggregateSpareSchema
