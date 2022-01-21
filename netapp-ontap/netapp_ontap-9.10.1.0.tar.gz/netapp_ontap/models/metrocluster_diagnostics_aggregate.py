r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MetroclusterDiagnosticsAggregate", "MetroclusterDiagnosticsAggregateSchema"]
__pdoc__ = {
    "MetroclusterDiagnosticsAggregateSchema.resource": False,
    "MetroclusterDiagnosticsAggregate": False,
}


class MetroclusterDiagnosticsAggregateSchema(ResourceSchema):
    """The fields of the MetroclusterDiagnosticsAggregate object"""

    state = fields.Str(data_key="state")
    r""" Status of diagnostic operation for this component.

Valid choices:

* ok
* warning
* not_run
* not_applicable """

    summary = fields.Nested("netapp_ontap.models.error_arguments.ErrorArgumentsSchema", unknown=EXCLUDE, data_key="summary")
    r""" The summary field of the metrocluster_diagnostics_aggregate. """

    timestamp = ImpreciseDateTime(data_key="timestamp")
    r""" Time of the most recent diagnostic operation for this component

Example: 2016-03-10T22:35:16.000+0000 """

    @property
    def resource(self):
        return MetroclusterDiagnosticsAggregate

    gettable_fields = [
        "state",
        "summary",
        "timestamp",
    ]
    """state,summary,timestamp,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class MetroclusterDiagnosticsAggregate(Resource):

    _schema = MetroclusterDiagnosticsAggregateSchema
