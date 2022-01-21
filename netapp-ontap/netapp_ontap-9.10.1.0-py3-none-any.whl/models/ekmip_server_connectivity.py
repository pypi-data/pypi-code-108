r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["EkmipServerConnectivity", "EkmipServerConnectivitySchema"]
__pdoc__ = {
    "EkmipServerConnectivitySchema.resource": False,
    "EkmipServerConnectivity": False,
}


class EkmipServerConnectivitySchema(ResourceSchema):
    """The fields of the EkmipServerConnectivity object"""

    code = Size(data_key="code")
    r""" Code corresponding to the error message. Returns a 0 if a given SVM is able to communicate to the EKMIP servers of all of the nodes in the cluster.

Example: 346758 """

    message = fields.Str(data_key="message")
    r""" Error message set when cluster-wide EKMIP server availability from the given SVM and node is false.

Example: embedded KMIP server status unavailable on node. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the ekmip_server_connectivity. """

    reachable = fields.Boolean(data_key="reachable")
    r""" Set to true if the given SVM on the given node is able to communicate to all EKMIP servers configured on all nodes in the cluster. """

    @property
    def resource(self):
        return EkmipServerConnectivity

    gettable_fields = [
        "code",
        "message",
        "node.links",
        "node.name",
        "node.uuid",
        "reachable",
    ]
    """code,message,node.links,node.name,node.uuid,reachable,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class EkmipServerConnectivity(Resource):

    _schema = EkmipServerConnectivitySchema
