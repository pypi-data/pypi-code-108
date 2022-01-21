r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MetroclusterLocal", "MetroclusterLocalSchema"]
__pdoc__ = {
    "MetroclusterLocalSchema.resource": False,
    "MetroclusterLocal": False,
}


class MetroclusterLocalSchema(ResourceSchema):
    """The fields of the MetroclusterLocal object"""

    cluster = fields.Nested("netapp_ontap.resources.cluster.ClusterSchema", unknown=EXCLUDE, data_key="cluster")
    r""" The cluster field of the metrocluster_local. """

    configuration_state = fields.Str(data_key="configuration_state")
    r""" Indicates the state of the local cluster configuration.

Valid choices:

* configuration_error
* configured
* not_configured
* not_reachable
* partially_configured
* unknown """

    mode = fields.Str(data_key="mode")
    r""" Specifies the mode of operation of the local cluster.

Valid choices:

* normal
* not_configured
* not_reachable
* partial_switchback
* partial_switchover
* switchover
* unknown
* waiting_for_switchback """

    partner_cluster_reachable = fields.Boolean(data_key="partner_cluster_reachable")
    r""" Specifies whether the partner cluster is reachable from the local cluster. """

    periodic_check_enabled = fields.Boolean(data_key="periodic_check_enabled")
    r""" Indicates whether or not a periodic check is enabled on the local cluster. """

    @property
    def resource(self):
        return MetroclusterLocal

    gettable_fields = [
        "cluster.links",
        "cluster.name",
        "cluster.uuid",
        "configuration_state",
        "mode",
        "partner_cluster_reachable",
        "periodic_check_enabled",
    ]
    """cluster.links,cluster.name,cluster.uuid,configuration_state,mode,partner_cluster_reachable,periodic_check_enabled,"""

    patchable_fields = [
        "cluster.name",
        "cluster.uuid",
    ]
    """cluster.name,cluster.uuid,"""

    postable_fields = [
        "cluster.name",
        "cluster.uuid",
    ]
    """cluster.name,cluster.uuid,"""


class MetroclusterLocal(Resource):

    _schema = MetroclusterLocalSchema
