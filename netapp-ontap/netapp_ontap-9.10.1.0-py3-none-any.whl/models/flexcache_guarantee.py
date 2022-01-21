r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FlexcacheGuarantee", "FlexcacheGuaranteeSchema"]
__pdoc__ = {
    "FlexcacheGuaranteeSchema.resource": False,
    "FlexcacheGuarantee": False,
}


class FlexcacheGuaranteeSchema(ResourceSchema):
    """The fields of the FlexcacheGuarantee object"""

    type = fields.Str(data_key="type")
    r""" The type of space guarantee of this volume in the aggregate.

Valid choices:

* volume
* none """

    @property
    def resource(self):
        return FlexcacheGuarantee

    gettable_fields = [
        "type",
    ]
    """type,"""

    patchable_fields = [
        "type",
    ]
    """type,"""

    postable_fields = [
        "type",
    ]
    """type,"""


class FlexcacheGuarantee(Resource):

    _schema = FlexcacheGuaranteeSchema
