r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfError", "ShelfErrorSchema"]
__pdoc__ = {
    "ShelfErrorSchema.resource": False,
    "ShelfError": False,
}


class ShelfErrorSchema(ResourceSchema):
    """The fields of the ShelfError object"""

    reason = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="reason")
    r""" The reason field of the shelf_error. """

    severity = fields.Str(data_key="severity")
    r""" The severity field of the shelf_error.

Valid choices:

* unknown
* notice
* warning
* error
* critical """

    type = fields.Str(data_key="type")
    r""" The type field of the shelf_error.

Valid choices:

* not_applicable
* connection_issue
* connection_activity
* module_error
* shelf_error """

    @property
    def resource(self):
        return ShelfError

    gettable_fields = [
        "reason",
        "severity",
        "type",
    ]
    """reason,severity,type,"""

    patchable_fields = [
        "severity",
        "type",
    ]
    """severity,type,"""

    postable_fields = [
        "severity",
        "type",
    ]
    """severity,type,"""


class ShelfError(Resource):

    _schema = ShelfErrorSchema
