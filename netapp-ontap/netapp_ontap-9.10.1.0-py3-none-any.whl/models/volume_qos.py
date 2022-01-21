r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeQos", "VolumeQosSchema"]
__pdoc__ = {
    "VolumeQosSchema.resource": False,
    "VolumeQos": False,
}


class VolumeQosSchema(ResourceSchema):
    """The fields of the VolumeQos object"""

    policy = fields.Nested("netapp_ontap.resources.qos_policy.QosPolicySchema", unknown=EXCLUDE, data_key="policy")
    r""" The policy field of the volume_qos. """

    @property
    def resource(self):
        return VolumeQos

    gettable_fields = [
        "policy.links",
        "policy.max_throughput_iops",
        "policy.max_throughput_mbps",
        "policy.min_throughput_iops",
        "policy.min_throughput_mbps",
        "policy.name",
        "policy.uuid",
    ]
    """policy.links,policy.max_throughput_iops,policy.max_throughput_mbps,policy.min_throughput_iops,policy.min_throughput_mbps,policy.name,policy.uuid,"""

    patchable_fields = [
        "policy.max_throughput_iops",
        "policy.max_throughput_mbps",
        "policy.min_throughput_iops",
        "policy.min_throughput_mbps",
        "policy.name",
        "policy.uuid",
    ]
    """policy.max_throughput_iops,policy.max_throughput_mbps,policy.min_throughput_iops,policy.min_throughput_mbps,policy.name,policy.uuid,"""

    postable_fields = [
        "policy.max_throughput_iops",
        "policy.max_throughput_mbps",
        "policy.min_throughput_iops",
        "policy.min_throughput_mbps",
        "policy.name",
        "policy.uuid",
    ]
    """policy.max_throughput_iops,policy.max_throughput_mbps,policy.min_throughput_iops,policy.min_throughput_mbps,policy.name,policy.uuid,"""


class VolumeQos(Resource):

    _schema = VolumeQosSchema
