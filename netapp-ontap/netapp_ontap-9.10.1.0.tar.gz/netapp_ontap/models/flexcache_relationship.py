r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FlexcacheRelationship", "FlexcacheRelationshipSchema"]
__pdoc__ = {
    "FlexcacheRelationshipSchema.resource": False,
    "FlexcacheRelationship": False,
}


class FlexcacheRelationshipSchema(ResourceSchema):
    """The fields of the FlexcacheRelationship object"""

    cluster = fields.Nested("netapp_ontap.resources.cluster.ClusterSchema", unknown=EXCLUDE, data_key="cluster")
    r""" The cluster field of the flexcache_relationship. """

    create_time = ImpreciseDateTime(data_key="create_time")
    r""" Creation time of the relationship.

Example: 2018-06-04T19:00:00.000+0000 """

    ip_address = fields.Str(data_key="ip_address")
    r""" Cluster managerment IP of the remote cluster.

Example: 10.10.10.7 """

    size = Size(data_key="size")
    r""" Size of the remote volume. """

    state = fields.Str(data_key="state")
    r""" Volume state

Valid choices:

* error
* mixed
* offline
* online """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, data_key="svm")
    r""" The svm field of the flexcache_relationship. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE, data_key="volume")
    r""" The volume field of the flexcache_relationship. """

    @property
    def resource(self):
        return FlexcacheRelationship

    gettable_fields = [
        "cluster.links",
        "cluster.name",
        "cluster.uuid",
        "create_time",
        "ip_address",
        "size",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """cluster.links,cluster.name,cluster.uuid,create_time,ip_address,size,state,svm.links,svm.name,svm.uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "cluster.name",
        "cluster.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """cluster.name,cluster.uuid,volume.name,volume.uuid,"""

    postable_fields = [
        "cluster.name",
        "cluster.uuid",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """cluster.name,cluster.uuid,svm.name,svm.uuid,volume.name,volume.uuid,"""


class FlexcacheRelationship(Resource):

    _schema = FlexcacheRelationshipSchema
