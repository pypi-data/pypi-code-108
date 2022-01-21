r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PerformanceReducedThroughput", "PerformanceReducedThroughputSchema"]
__pdoc__ = {
    "PerformanceReducedThroughputSchema.resource": False,
    "PerformanceReducedThroughput": False,
}


class PerformanceReducedThroughputSchema(ResourceSchema):
    """The fields of the PerformanceReducedThroughput object"""

    links = fields.Nested("netapp_ontap.models.collection_links.CollectionLinksSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the performance_reduced_throughput. """

    num_records = Size(data_key="num_records")
    r""" Number of records """

    records = fields.List(fields.Nested("netapp_ontap.models.performance_metric_reduced_throughput.PerformanceMetricReducedThroughputSchema", unknown=EXCLUDE), data_key="records")
    r""" The records field of the performance_reduced_throughput. """

    @property
    def resource(self):
        return PerformanceReducedThroughput

    gettable_fields = [
        "links",
        "num_records",
        "records",
    ]
    """links,num_records,records,"""

    patchable_fields = [
        "num_records",
    ]
    """num_records,"""

    postable_fields = [
        "num_records",
    ]
    """num_records,"""


class PerformanceReducedThroughput(Resource):

    _schema = PerformanceReducedThroughputSchema
