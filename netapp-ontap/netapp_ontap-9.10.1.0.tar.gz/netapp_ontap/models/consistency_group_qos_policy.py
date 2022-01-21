r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupQosPolicy", "ConsistencyGroupQosPolicySchema"]
__pdoc__ = {
    "ConsistencyGroupQosPolicySchema.resource": False,
    "ConsistencyGroupQosPolicy": False,
}


class ConsistencyGroupQosPolicySchema(ResourceSchema):
    """The fields of the ConsistencyGroupQosPolicy object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the consistency_group_qos_policy. """

    max_throughput_iops = Size(data_key="max_throughput_iops")
    r""" Specifies the maximum throughput in IOPS, 0 means none. This is mutually exclusive with name and UUID during POST and PATCH.

Example: 10000 """

    max_throughput_mbps = Size(data_key="max_throughput_mbps")
    r""" Specifies the maximum throughput in Megabytes per sec, 0 means none. This is mutually exclusive with name and UUID during POST and PATCH.

Example: 500 """

    min_throughput_iops = Size(data_key="min_throughput_iops")
    r""" Specifies the minimum throughput in IOPS, 0 means none. Setting "min_throughput" is supported on AFF platforms only, unless FabricPool tiering policies are set. This is mutually exclusive with name and UUID during POST and PATCH.

Example: 2000 """

    min_throughput_mbps = Size(data_key="min_throughput_mbps")
    r""" Specifies the minimum throughput in Megabytes per sec, 0 means none. This is mutually exclusive with name and UUID during POST and PATCH.

Example: 500 """

    name = fields.Str(data_key="name")
    r""" The QoS policy group name. This is mutually exclusive with UUID and other QoS attributes during POST and PATCH.

Example: performance """

    uuid = fields.Str(data_key="uuid")
    r""" The QoS policy group UUID. This is mutually exclusive with name and other QoS attributes during POST and PATCH.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return ConsistencyGroupQosPolicy

    gettable_fields = [
        "links",
        "max_throughput_iops",
        "max_throughput_mbps",
        "min_throughput_iops",
        "min_throughput_mbps",
        "name",
        "uuid",
    ]
    """links,max_throughput_iops,max_throughput_mbps,min_throughput_iops,min_throughput_mbps,name,uuid,"""

    patchable_fields = [
        "max_throughput_iops",
        "max_throughput_mbps",
        "min_throughput_iops",
        "min_throughput_mbps",
        "name",
        "uuid",
    ]
    """max_throughput_iops,max_throughput_mbps,min_throughput_iops,min_throughput_mbps,name,uuid,"""

    postable_fields = [
        "max_throughput_iops",
        "max_throughput_mbps",
        "min_throughput_iops",
        "min_throughput_mbps",
        "name",
        "uuid",
    ]
    """max_throughput_iops,max_throughput_mbps,min_throughput_iops,min_throughput_mbps,name,uuid,"""


class ConsistencyGroupQosPolicy(Resource):

    _schema = ConsistencyGroupQosPolicySchema
