r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchConnections", "StorageSwitchConnectionsSchema"]
__pdoc__ = {
    "StorageSwitchConnectionsSchema.resource": False,
    "StorageSwitchConnections": False,
}


class StorageSwitchConnectionsSchema(ResourceSchema):
    """The fields of the StorageSwitchConnections object"""

    peer_port = fields.Nested("netapp_ontap.models.storage_switch_peer_port.StorageSwitchPeerPortSchema", unknown=EXCLUDE, data_key="peer_port")
    r""" The peer_port field of the storage_switch_connections. """

    source_port = fields.Nested("netapp_ontap.models.storage_switch_source_port.StorageSwitchSourcePortSchema", unknown=EXCLUDE, data_key="source_port")
    r""" The source_port field of the storage_switch_connections. """

    @property
    def resource(self):
        return StorageSwitchConnections

    gettable_fields = [
        "peer_port",
        "source_port",
    ]
    """peer_port,source_port,"""

    patchable_fields = [
        "peer_port",
        "source_port",
    ]
    """peer_port,source_port,"""

    postable_fields = [
        "peer_port",
        "source_port",
    ]
    """peer_port,source_port,"""


class StorageSwitchConnections(Resource):

    _schema = StorageSwitchConnectionsSchema
