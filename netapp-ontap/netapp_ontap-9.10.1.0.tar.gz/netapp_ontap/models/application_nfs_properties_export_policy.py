r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationNfsPropertiesExportPolicy", "ApplicationNfsPropertiesExportPolicySchema"]
__pdoc__ = {
    "ApplicationNfsPropertiesExportPolicySchema.resource": False,
    "ApplicationNfsPropertiesExportPolicy": False,
}


class ApplicationNfsPropertiesExportPolicySchema(ResourceSchema):
    """The fields of the ApplicationNfsPropertiesExportPolicy object"""

    name = fields.Str(data_key="name")
    r""" Export policy name """

    @property
    def resource(self):
        return ApplicationNfsPropertiesExportPolicy

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationNfsPropertiesExportPolicy(Resource):

    _schema = ApplicationNfsPropertiesExportPolicySchema
