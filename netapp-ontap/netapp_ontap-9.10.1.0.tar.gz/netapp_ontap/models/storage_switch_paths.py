r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchPaths", "StorageSwitchPathsSchema"]
__pdoc__ = {
    "StorageSwitchPathsSchema.resource": False,
    "StorageSwitchPaths": False,
}


class StorageSwitchPathsSchema(ResourceSchema):
    """The fields of the StorageSwitchPaths object"""

    adapter = fields.Nested("netapp_ontap.models.storage_switch_adapter.StorageSwitchAdapterSchema", unknown=EXCLUDE, data_key="adapter")
    r""" The adapter field of the storage_switch_paths. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the storage_switch_paths. """

    port = fields.Nested("netapp_ontap.models.storage_switch_port.StorageSwitchPortSchema", unknown=EXCLUDE, data_key="port")
    r""" The port field of the storage_switch_paths. """

    @property
    def resource(self):
        return StorageSwitchPaths

    gettable_fields = [
        "adapter",
        "node.links",
        "node.name",
        "node.uuid",
        "port",
    ]
    """adapter,node.links,node.name,node.uuid,port,"""

    patchable_fields = [
        "adapter",
        "node.name",
        "node.uuid",
        "port",
    ]
    """adapter,node.name,node.uuid,port,"""

    postable_fields = [
        "adapter",
        "node.name",
        "node.uuid",
        "port",
    ]
    """adapter,node.name,node.uuid,port,"""


class StorageSwitchPaths(Resource):

    _schema = StorageSwitchPathsSchema
