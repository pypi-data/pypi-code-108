r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PerformanceSvmNfsMetricHistorical", "PerformanceSvmNfsMetricHistoricalSchema"]
__pdoc__ = {
    "PerformanceSvmNfsMetricHistoricalSchema.resource": False,
    "PerformanceSvmNfsMetricHistorical": False,
}


class PerformanceSvmNfsMetricHistoricalSchema(ResourceSchema):
    """The fields of the PerformanceSvmNfsMetricHistorical object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the performance_svm_nfs_metric_historical. """

    timestamp = ImpreciseDateTime(data_key="timestamp")
    r""" The timestamp of the performance data.

Example: 2017-01-25T11:20:13.000+0000 """

    v3 = fields.Nested("netapp_ontap.models.performance_svm_nfs_metric_historical_v3.PerformanceSvmNfsMetricHistoricalV3Schema", unknown=EXCLUDE, data_key="v3")
    r""" The v3 field of the performance_svm_nfs_metric_historical. """

    v4 = fields.Nested("netapp_ontap.models.performance_svm_nfs_metric_historical_v4.PerformanceSvmNfsMetricHistoricalV4Schema", unknown=EXCLUDE, data_key="v4")
    r""" The v4 field of the performance_svm_nfs_metric_historical. """

    v41 = fields.Nested("netapp_ontap.models.performance_svm_nfs_metric_historical_v41.PerformanceSvmNfsMetricHistoricalV41Schema", unknown=EXCLUDE, data_key="v41")
    r""" The v41 field of the performance_svm_nfs_metric_historical. """

    @property
    def resource(self):
        return PerformanceSvmNfsMetricHistorical

    gettable_fields = [
        "links",
        "timestamp",
        "v3",
        "v4",
        "v41",
    ]
    """links,timestamp,v3,v4,v41,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class PerformanceSvmNfsMetricHistorical(Resource):

    _schema = PerformanceSvmNfsMetricHistoricalSchema
