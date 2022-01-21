r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NfsServiceQtree", "NfsServiceQtreeSchema"]
__pdoc__ = {
    "NfsServiceQtreeSchema.resource": False,
    "NfsServiceQtree": False,
}


class NfsServiceQtreeSchema(ResourceSchema):
    """The fields of the NfsServiceQtree object"""

    export_enabled = fields.Boolean(data_key="export_enabled")
    r""" Specifies whether qtree export is enabled. """

    validate_export = fields.Boolean(data_key="validate_export")
    r""" Specifies whether qtree export validation is enabled. """

    @property
    def resource(self):
        return NfsServiceQtree

    gettable_fields = [
        "export_enabled",
        "validate_export",
    ]
    """export_enabled,validate_export,"""

    patchable_fields = [
        "export_enabled",
        "validate_export",
    ]
    """export_enabled,validate_export,"""

    postable_fields = [
        "export_enabled",
        "validate_export",
    ]
    """export_enabled,validate_export,"""


class NfsServiceQtree(Resource):

    _schema = NfsServiceQtreeSchema
