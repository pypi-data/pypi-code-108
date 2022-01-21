r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregatePatch", "AggregatePatchSchema"]
__pdoc__ = {
    "AggregatePatchSchema.resource": False,
    "AggregatePatch": False,
}


class AggregatePatchSchema(ResourceSchema):
    """The fields of the AggregatePatch object"""

    job = fields.Nested("netapp_ontap.models.job_link.JobLinkSchema", unknown=EXCLUDE, data_key="job")
    r""" The job field of the aggregate_patch. """

    num_records = Size(data_key="num_records")
    r""" Number of records """

    records = fields.List(fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE), data_key="records")
    r""" The records field of the aggregate_patch. """

    warnings = fields.List(fields.Nested("netapp_ontap.models.aggregate_warning.AggregateWarningSchema", unknown=EXCLUDE), data_key="warnings")
    r""" List of validation warnings and remediation advice for the aggregate simulate behavior. """

    @property
    def resource(self):
        return AggregatePatch

    gettable_fields = [
        "job",
        "num_records",
        "records",
        "warnings",
    ]
    """job,num_records,records,warnings,"""

    patchable_fields = [
        "job",
        "num_records",
        "records",
    ]
    """job,num_records,records,"""

    postable_fields = [
        "job",
        "num_records",
        "records",
    ]
    """job,num_records,records,"""


class AggregatePatch(Resource):

    _schema = AggregatePatchSchema
