r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfThresholdHigh", "ShelfThresholdHighSchema"]
__pdoc__ = {
    "ShelfThresholdHighSchema.resource": False,
    "ShelfThresholdHigh": False,
}


class ShelfThresholdHighSchema(ResourceSchema):
    """The fields of the ShelfThresholdHigh object"""

    critical = Size(data_key="critical")
    r""" High critical threshold, in degrees Celsius

Example: 60 """

    warning = Size(data_key="warning")
    r""" High warning threshold, in degrees Celsius

Example: 55 """

    @property
    def resource(self):
        return ShelfThresholdHigh

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


class ShelfThresholdHigh(Resource):

    _schema = ShelfThresholdHighSchema
