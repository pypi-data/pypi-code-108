r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfThreshold", "ShelfThresholdSchema"]
__pdoc__ = {
    "ShelfThresholdSchema.resource": False,
    "ShelfThreshold": False,
}


class ShelfThresholdSchema(ResourceSchema):
    """The fields of the ShelfThreshold object"""

    high = fields.Nested("netapp_ontap.models.shelf_threshold_high.ShelfThresholdHighSchema", unknown=EXCLUDE, data_key="high")
    r""" The high field of the shelf_threshold. """

    low = fields.Nested("netapp_ontap.models.shelf_threshold_low.ShelfThresholdLowSchema", unknown=EXCLUDE, data_key="low")
    r""" The low field of the shelf_threshold. """

    @property
    def resource(self):
        return ShelfThreshold

    gettable_fields = [
        "high",
        "low",
    ]
    """high,low,"""

    patchable_fields = [
        "high",
        "low",
    ]
    """high,low,"""

    postable_fields = [
        "high",
        "low",
    ]
    """high,low,"""


class ShelfThreshold(Resource):

    _schema = ShelfThresholdSchema
