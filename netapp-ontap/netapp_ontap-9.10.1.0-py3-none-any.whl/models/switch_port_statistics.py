r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SwitchPortStatistics", "SwitchPortStatisticsSchema"]
__pdoc__ = {
    "SwitchPortStatisticsSchema.resource": False,
    "SwitchPortStatistics": False,
}


class SwitchPortStatisticsSchema(ResourceSchema):
    """The fields of the SwitchPortStatistics object"""

    receive_raw = fields.Nested("netapp_ontap.models.port_statistics_packet_counters.PortStatisticsPacketCountersSchema", unknown=EXCLUDE, data_key="receive_raw")
    r""" The receive_raw field of the switch_port_statistics. """

    transmit_raw = fields.Nested("netapp_ontap.models.port_statistics_packet_counters.PortStatisticsPacketCountersSchema", unknown=EXCLUDE, data_key="transmit_raw")
    r""" The transmit_raw field of the switch_port_statistics. """

    @property
    def resource(self):
        return SwitchPortStatistics

    gettable_fields = [
        "receive_raw",
        "transmit_raw",
    ]
    """receive_raw,transmit_raw,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SwitchPortStatistics(Resource):

    _schema = SwitchPortStatisticsSchema
