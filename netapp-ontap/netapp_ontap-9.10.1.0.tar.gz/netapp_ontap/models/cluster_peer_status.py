r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ClusterPeerStatus", "ClusterPeerStatusSchema"]
__pdoc__ = {
    "ClusterPeerStatusSchema.resource": False,
    "ClusterPeerStatus": False,
}


class ClusterPeerStatusSchema(ResourceSchema):
    """The fields of the ClusterPeerStatus object"""

    state = fields.Str(data_key="state")
    r""" The state field of the cluster_peer_status.

Valid choices:

* available
* partial
* unavailable
* pending
* unidentified """

    update_time = ImpreciseDateTime(data_key="update_time")
    r""" The last time the state was updated.

Example: 2017-01-25T11:20:13.000+0000 """

    @property
    def resource(self):
        return ClusterPeerStatus

    gettable_fields = [
        "state",
        "update_time",
    ]
    """state,update_time,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ClusterPeerStatus(Resource):

    _schema = ClusterPeerStatusSchema
