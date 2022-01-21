r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ClusterPeerEncryption", "ClusterPeerEncryptionSchema"]
__pdoc__ = {
    "ClusterPeerEncryptionSchema.resource": False,
    "ClusterPeerEncryption": False,
}


class ClusterPeerEncryptionSchema(ResourceSchema):
    """The fields of the ClusterPeerEncryption object"""

    proposed = fields.Str(data_key="proposed")
    r""" The proposed field of the cluster_peer_encryption.

Valid choices:

* none
* tls_psk """

    state = fields.Str(data_key="state")
    r""" The state field of the cluster_peer_encryption.

Valid choices:

* none
* tls_psk """

    @property
    def resource(self):
        return ClusterPeerEncryption

    gettable_fields = [
        "proposed",
        "state",
    ]
    """proposed,state,"""

    patchable_fields = [
        "proposed",
    ]
    """proposed,"""

    postable_fields = [
        "proposed",
    ]
    """proposed,"""


class ClusterPeerEncryption(Resource):

    _schema = ClusterPeerEncryptionSchema
