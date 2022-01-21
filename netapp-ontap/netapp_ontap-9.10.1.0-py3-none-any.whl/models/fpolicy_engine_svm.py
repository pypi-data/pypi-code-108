r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FpolicyEngineSvm", "FpolicyEngineSvmSchema"]
__pdoc__ = {
    "FpolicyEngineSvmSchema.resource": False,
    "FpolicyEngineSvm": False,
}


class FpolicyEngineSvmSchema(ResourceSchema):
    """The fields of the FpolicyEngineSvm object"""

    uuid = fields.Str(data_key="uuid")
    r""" SVM UUID """

    @property
    def resource(self):
        return FpolicyEngineSvm

    gettable_fields = [
        "uuid",
    ]
    """uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FpolicyEngineSvm(Resource):

    _schema = FpolicyEngineSvmSchema
