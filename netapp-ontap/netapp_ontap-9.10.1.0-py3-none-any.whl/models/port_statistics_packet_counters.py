r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PortStatisticsPacketCounters", "PortStatisticsPacketCountersSchema"]
__pdoc__ = {
    "PortStatisticsPacketCountersSchema.resource": False,
    "PortStatisticsPacketCounters": False,
}


class PortStatisticsPacketCountersSchema(ResourceSchema):
    """The fields of the PortStatisticsPacketCounters object"""

    discards = Size(data_key="discards")
    r""" Total number of discarded packets.

Example: 100 """

    errors = Size(data_key="errors")
    r""" Number of packet errors.

Example: 200 """

    packets = Size(data_key="packets")
    r""" Total packet count.

Example: 500 """

    @property
    def resource(self):
        return PortStatisticsPacketCounters

    gettable_fields = [
        "discards",
        "errors",
        "packets",
    ]
    """discards,errors,packets,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class PortStatisticsPacketCounters(Resource):

    _schema = PortStatisticsPacketCountersSchema
