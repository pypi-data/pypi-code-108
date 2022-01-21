r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupTieringObjectStoresInner", "ConsistencyGroupTieringObjectStoresInnerSchema"]
__pdoc__ = {
    "ConsistencyGroupTieringObjectStoresInnerSchema.resource": False,
    "ConsistencyGroupTieringObjectStoresInner": False,
}


class ConsistencyGroupTieringObjectStoresInnerSchema(ResourceSchema):
    """The fields of the ConsistencyGroupTieringObjectStoresInner object"""

    name = fields.Str(data_key="name")
    r""" The name of the object store to use. Used for placement. """

    @property
    def resource(self):
        return ConsistencyGroupTieringObjectStoresInner

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class ConsistencyGroupTieringObjectStoresInner(Resource):

    _schema = ConsistencyGroupTieringObjectStoresInnerSchema
