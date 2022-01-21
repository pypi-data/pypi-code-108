r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateWarning", "AggregateWarningSchema"]
__pdoc__ = {
    "AggregateWarningSchema.resource": False,
    "AggregateWarning": False,
}


class AggregateWarningSchema(ResourceSchema):
    """The fields of the AggregateWarning object"""

    action = fields.Nested("netapp_ontap.models.aggregate_warning_action.AggregateWarningActionSchema", unknown=EXCLUDE, data_key="action")
    r""" The action field of the aggregate_warning. """

    name = fields.Str(data_key="name")
    r""" Name of the entity that returns the warning. """

    warning = fields.Nested("netapp_ontap.models.aggregate_warning_warning.AggregateWarningWarningSchema", unknown=EXCLUDE, data_key="warning")
    r""" The warning field of the aggregate_warning. """

    @property
    def resource(self):
        return AggregateWarning

    gettable_fields = [
        "action",
        "name",
        "warning",
    ]
    """action,name,warning,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AggregateWarning(Resource):

    _schema = AggregateWarningSchema
