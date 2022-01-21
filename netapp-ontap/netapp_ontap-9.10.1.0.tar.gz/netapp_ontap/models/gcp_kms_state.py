r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["GcpKmsState", "GcpKmsStateSchema"]
__pdoc__ = {
    "GcpKmsStateSchema.resource": False,
    "GcpKmsState": False,
}


class GcpKmsStateSchema(ResourceSchema):
    """The fields of the GcpKmsState object"""

    cluster_state = fields.Boolean(data_key="cluster_state")
    r""" Set to true when Google Cloud KMS key protection is available on all nodes of the cluster. """

    code = Size(data_key="code")
    r""" Error code corresponding to the status message. Returns 0 if Google Cloud KMS key protection is available in all nodes of the cluster.

Example: 346758 """

    message = fields.Str(data_key="message")
    r""" Error message set when top-level internal key protection key (KEK) availability on cluster is false.

Example: Top-level internal key protection key (KEK) is unavailable on the following nodes with the associated reasons: Node: node1. Reason: No volumes created yet for the SVM. Wrapped KEK status will be available after creating encrypted volumes. """

    @property
    def resource(self):
        return GcpKmsState

    gettable_fields = [
        "cluster_state",
        "code",
        "message",
    ]
    """cluster_state,code,message,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class GcpKmsState(Resource):

    _schema = GcpKmsStateSchema
