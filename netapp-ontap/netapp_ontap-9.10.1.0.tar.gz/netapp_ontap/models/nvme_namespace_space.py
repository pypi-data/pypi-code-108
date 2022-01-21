r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeNamespaceSpace", "NvmeNamespaceSpaceSchema"]
__pdoc__ = {
    "NvmeNamespaceSpaceSchema.resource": False,
    "NvmeNamespaceSpace": False,
}


class NvmeNamespaceSpaceSchema(ResourceSchema):
    """The fields of the NvmeNamespaceSpace object"""

    block_size = Size(data_key="block_size")
    r""" The size of blocks in the namespace in bytes.<br/>
Valid in POST when creating an NVMe namespace that is not a clone of another. Disallowed in POST when creating a namespace clone.
 Valid in POST. """

    guarantee = fields.Nested("netapp_ontap.models.nvme_namespace_space_guarantee.NvmeNamespaceSpaceGuaranteeSchema", unknown=EXCLUDE, data_key="guarantee")
    r""" The guarantee field of the nvme_namespace_space. """

    size = Size(data_key="size")
    r""" The total provisioned size of the NVMe namespace. Valid in POST and PATCH. The NVMe namespace size can be increased but not be made smaller using the REST interface.<br/>
The maximum and minimum sizes listed here are the absolute maximum and absolute minimum sizes in bytes. The maximum size is variable with respect to large NVMe namespace support in ONTAP. If large namespaces are supported, the maximum size is 128 TB (140737488355328 bytes) and if not supported, the maximum size is just under 16 TB (17557557870592 bytes). The minimum size supported is always 4096 bytes.<br/>
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation.


Example: 1073741824 """

    used = Size(data_key="used")
    r""" The amount of space consumed by the main data stream of the NVMe namespace.<br/>
This value is the total space consumed in the volume by the NVMe namespace, including filesystem overhead, but excluding prefix and suffix streams. Due to internal filesystem overhead and the many ways NVMe filesystems and applications utilize blocks within a namespace, this value does not necessarily reflect actual consumption/availability from the perspective of the filesystem or application. Without specific knowledge of how the namespace blocks are utilized outside of ONTAP, this property should not be used and an indicator for an out-of-space condition.<br/>
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation. """

    @property
    def resource(self):
        return NvmeNamespaceSpace

    gettable_fields = [
        "block_size",
        "guarantee",
        "size",
        "used",
    ]
    """block_size,guarantee,size,used,"""

    patchable_fields = [
        "guarantee",
        "size",
    ]
    """guarantee,size,"""

    postable_fields = [
        "block_size",
        "guarantee",
        "size",
    ]
    """block_size,guarantee,size,"""


class NvmeNamespaceSpace(Resource):

    _schema = NvmeNamespaceSpaceSchema
