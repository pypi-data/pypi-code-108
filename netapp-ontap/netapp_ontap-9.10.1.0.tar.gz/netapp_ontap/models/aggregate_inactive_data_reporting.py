r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateInactiveDataReporting", "AggregateInactiveDataReportingSchema"]
__pdoc__ = {
    "AggregateInactiveDataReportingSchema.resource": False,
    "AggregateInactiveDataReporting": False,
}


class AggregateInactiveDataReportingSchema(ResourceSchema):
    """The fields of the AggregateInactiveDataReporting object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" Specifes whether or not inactive data reporting is enabled on the aggregate. """

    start_time = ImpreciseDateTime(data_key="start_time")
    r""" Timestamp at which inactive data reporting was enabled on the aggregate.

Example: 2019-12-12T16:00:00.000+0000 """

    @property
    def resource(self):
        return AggregateInactiveDataReporting

    gettable_fields = [
        "enabled",
        "start_time",
    ]
    """enabled,start_time,"""

    patchable_fields = [
        "enabled",
    ]
    """enabled,"""

    postable_fields = [
    ]
    """"""


class AggregateInactiveDataReporting(Resource):

    _schema = AggregateInactiveDataReportingSchema
