r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupSpace", "ConsistencyGroupSpaceSchema"]
__pdoc__ = {
    "ConsistencyGroupSpaceSchema.resource": False,
    "ConsistencyGroupSpace": False,
}


class ConsistencyGroupSpaceSchema(ResourceSchema):
    """The fields of the ConsistencyGroupSpace object"""

    available = Size(data_key="available")
    r""" The amount of space available in the consistency group, in bytes.<br/>


Example: 5737418 """

    size = Size(data_key="size")
    r""" The total provisioned size of the consistency group, in bytes.<br/>


Example: 1073741824 """

    used = Size(data_key="used")
    r""" The amount of space consumed in the consistency group, in bytes.<br/>


Example: 5737418 """

    @property
    def resource(self):
        return ConsistencyGroupSpace

    gettable_fields = [
        "available",
        "size",
        "used",
    ]
    """available,size,used,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ConsistencyGroupSpace(Resource):

    _schema = ConsistencyGroupSpaceSchema
