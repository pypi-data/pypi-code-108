r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeSubsystemMapNamespace", "NvmeSubsystemMapNamespaceSchema"]
__pdoc__ = {
    "NvmeSubsystemMapNamespaceSchema.resource": False,
    "NvmeSubsystemMapNamespace": False,
}


class NvmeSubsystemMapNamespaceSchema(ResourceSchema):
    """The fields of the NvmeSubsystemMapNamespace object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the nvme_subsystem_map_namespace. """

    name = fields.Str(data_key="name")
    r""" The fully qualified path name of the NVMe namespace composed from the volume name, qtree name, and file name of the NVMe namespace. Valid in POST.


Example: /vol/vol1/namespace1 """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the nvme_subsystem_map_namespace. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the NVMe namespace. Valid in POST.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return NvmeSubsystemMapNamespace

    gettable_fields = [
        "links",
        "name",
        "node.links",
        "node.name",
        "node.uuid",
        "uuid",
    ]
    """links,name,node.links,node.name,node.uuid,uuid,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

    postable_fields = [
        "name",
        "node.name",
        "node.uuid",
        "uuid",
    ]
    """name,node.name,node.uuid,uuid,"""


class NvmeSubsystemMapNamespace(Resource):

    _schema = NvmeSubsystemMapNamespaceSchema
