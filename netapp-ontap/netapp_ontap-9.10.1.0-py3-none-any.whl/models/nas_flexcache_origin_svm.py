r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasFlexcacheOriginSvm", "NasFlexcacheOriginSvmSchema"]
__pdoc__ = {
    "NasFlexcacheOriginSvmSchema.resource": False,
    "NasFlexcacheOriginSvm": False,
}


class NasFlexcacheOriginSvmSchema(ResourceSchema):
    """The fields of the NasFlexcacheOriginSvm object"""

    name = fields.Str(data_key="name")
    r""" Name of the source SVM. """

    @property
    def resource(self):
        return NasFlexcacheOriginSvm

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
    ]
    """name,"""


class NasFlexcacheOriginSvm(Resource):

    _schema = NasFlexcacheOriginSvmSchema
