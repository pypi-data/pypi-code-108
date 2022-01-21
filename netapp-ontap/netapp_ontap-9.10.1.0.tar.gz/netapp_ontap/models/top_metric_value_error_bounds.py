r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TopMetricValueErrorBounds", "TopMetricValueErrorBoundsSchema"]
__pdoc__ = {
    "TopMetricValueErrorBoundsSchema.resource": False,
    "TopMetricValueErrorBounds": False,
}


class TopMetricValueErrorBoundsSchema(ResourceSchema):
    """The fields of the TopMetricValueErrorBounds object"""

    lower_bound = Size(data_key="lower_bound")
    r""" Lower bound of the nominal value of a metric.

Example: 34 """

    upper_bound = Size(data_key="upper_bound")
    r""" Upper bound of the nominal value of a metric.

Example: 54 """

    @property
    def resource(self):
        return TopMetricValueErrorBounds

    gettable_fields = [
        "lower_bound",
        "upper_bound",
    ]
    """lower_bound,upper_bound,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class TopMetricValueErrorBounds(Resource):

    _schema = TopMetricValueErrorBoundsSchema
