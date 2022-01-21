r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MaxdataOnSanApplicationComponentsTieringObjectStores", "MaxdataOnSanApplicationComponentsTieringObjectStoresSchema"]
__pdoc__ = {
    "MaxdataOnSanApplicationComponentsTieringObjectStoresSchema.resource": False,
    "MaxdataOnSanApplicationComponentsTieringObjectStores": False,
}


class MaxdataOnSanApplicationComponentsTieringObjectStoresSchema(ResourceSchema):
    """The fields of the MaxdataOnSanApplicationComponentsTieringObjectStores object"""

    name = fields.Str(data_key="name")
    r""" The name of the object-store to use. """

    @property
    def resource(self):
        return MaxdataOnSanApplicationComponentsTieringObjectStores

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
    ]
    """name,"""


class MaxdataOnSanApplicationComponentsTieringObjectStores(Resource):

    _schema = MaxdataOnSanApplicationComponentsTieringObjectStoresSchema
