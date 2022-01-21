r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmNdmp", "SvmNdmpSchema"]
__pdoc__ = {
    "SvmNdmpSchema.resource": False,
    "SvmNdmp": False,
}


class SvmNdmpSchema(ResourceSchema):
    """The fields of the SvmNdmp object"""

    allowed = fields.Boolean(data_key="allowed")
    r""" If this is set to true, an SVM administrator can manage the NDMP service. If it is false, only the cluster administrator can manage the service. """

    @property
    def resource(self):
        return SvmNdmp

    gettable_fields = [
        "allowed",
    ]
    """allowed,"""

    patchable_fields = [
        "allowed",
    ]
    """allowed,"""

    postable_fields = [
        "allowed",
    ]
    """allowed,"""


class SvmNdmp(Resource):

    _schema = SvmNdmpSchema
