r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ExportClientPolicy", "ExportClientPolicySchema"]
__pdoc__ = {
    "ExportClientPolicySchema.resource": False,
    "ExportClientPolicy": False,
}


class ExportClientPolicySchema(ResourceSchema):
    """The fields of the ExportClientPolicy object"""

    id = Size(data_key="id")
    r""" Export policy ID """

    @property
    def resource(self):
        return ExportClientPolicy

    gettable_fields = [
        "id",
    ]
    """id,"""

    patchable_fields = [
        "id",
    ]
    """id,"""

    postable_fields = [
        "id",
    ]
    """id,"""


class ExportClientPolicy(Resource):

    _schema = ExportClientPolicySchema
