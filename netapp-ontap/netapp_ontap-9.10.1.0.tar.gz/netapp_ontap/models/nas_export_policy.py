r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasExportPolicy", "NasExportPolicySchema"]
__pdoc__ = {
    "NasExportPolicySchema.resource": False,
    "NasExportPolicy": False,
}


class NasExportPolicySchema(ResourceSchema):
    """The fields of the NasExportPolicy object"""

    id = Size(data_key="id")
    r""" The ID of an existing NFS export policy. """

    name = fields.Str(data_key="name")
    r""" The name of an existing NFS export policy. """

    @property
    def resource(self):
        return NasExportPolicy

    gettable_fields = [
        "id",
        "name",
    ]
    """id,name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "id",
        "name",
    ]
    """id,name,"""


class NasExportPolicy(Resource):

    _schema = NasExportPolicySchema
