r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["GcpConnectivity", "GcpConnectivitySchema"]
__pdoc__ = {
    "GcpConnectivitySchema.resource": False,
    "GcpConnectivity": False,
}


class GcpConnectivitySchema(ResourceSchema):
    """The fields of the GcpConnectivity object"""

    code = Size(data_key="code")
    r""" Code corresponding to the error message. Returns a 0 if Google Cloud KMS service is reachable from all nodes in the cluster.

Example: 346758 """

    message = fields.Str(data_key="message")
    r""" Set to the error message when 'reachable' is false.

Example: Google Cloud KMS service is not reachable from all nodes - <reason>. """

    reachable = fields.Boolean(data_key="reachable")
    r""" Set to true if the Google Cloud KMS service is reachable from all nodes of the cluster. """

    @property
    def resource(self):
        return GcpConnectivity

    gettable_fields = [
        "code",
        "message",
        "reachable",
    ]
    """code,message,reachable,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class GcpConnectivity(Resource):

    _schema = GcpConnectivitySchema
