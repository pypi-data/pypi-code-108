r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasFlexcacheOriginComponent", "NasFlexcacheOriginComponentSchema"]
__pdoc__ = {
    "NasFlexcacheOriginComponentSchema.resource": False,
    "NasFlexcacheOriginComponent": False,
}


class NasFlexcacheOriginComponentSchema(ResourceSchema):
    """The fields of the NasFlexcacheOriginComponent object"""

    name = fields.Str(data_key="name")
    r""" Name of the source component. """

    @property
    def resource(self):
        return NasFlexcacheOriginComponent

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


class NasFlexcacheOriginComponent(Resource):

    _schema = NasFlexcacheOriginComponentSchema
