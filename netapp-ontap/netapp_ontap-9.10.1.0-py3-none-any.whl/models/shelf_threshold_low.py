r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfThresholdLow", "ShelfThresholdLowSchema"]
__pdoc__ = {
    "ShelfThresholdLowSchema.resource": False,
    "ShelfThresholdLow": False,
}


class ShelfThresholdLowSchema(ResourceSchema):
    """The fields of the ShelfThresholdLow object"""

    critical = Size(data_key="critical")
    r""" Low critical threshold, in degrees Celsius

Example: 0 """

    warning = Size(data_key="warning")
    r""" Low warning threshold, in degrees Celsius

Example: 5 """

    @property
    def resource(self):
        return ShelfThresholdLow

    gettable_fields = [
        "critical",
        "warning",
    ]
    """critical,warning,"""

    patchable_fields = [
        "critical",
        "warning",
    ]
    """critical,warning,"""

    postable_fields = [
        "critical",
        "warning",
    ]
    """critical,warning,"""


class ShelfThresholdLow(Resource):

    _schema = ShelfThresholdLowSchema
