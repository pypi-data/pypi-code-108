r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["PerformanceFcpMetricSvm", "PerformanceFcpMetricSvmSchema"]
__pdoc__ = {
    "PerformanceFcpMetricSvmSchema.resource": False,
    "PerformanceFcpMetricSvm": False,
}


class PerformanceFcpMetricSvmSchema(ResourceSchema):
    """The fields of the PerformanceFcpMetricSvm object"""

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the SVM.


Example: 02c9e252-41be-11e9-81d5-00a0986138f7 """

    @property
    def resource(self):
        return PerformanceFcpMetricSvm

    gettable_fields = [
        "uuid",
    ]
    """uuid,"""

    patchable_fields = [
        "uuid",
    ]
    """uuid,"""

    postable_fields = [
        "uuid",
    ]
    """uuid,"""


class PerformanceFcpMetricSvm(Resource):

    _schema = PerformanceFcpMetricSvmSchema
