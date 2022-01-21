r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CloudStoreAggregate", "CloudStoreAggregateSchema"]
__pdoc__ = {
    "CloudStoreAggregateSchema.resource": False,
    "CloudStoreAggregate": False,
}


class CloudStoreAggregateSchema(ResourceSchema):
    """The fields of the CloudStoreAggregate object"""

    name = fields.Str(data_key="name")
    r""" The name field of the cloud_store_aggregate.

Example: aggr1 """

    @property
    def resource(self):
        return CloudStoreAggregate

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class CloudStoreAggregate(Resource):

    _schema = CloudStoreAggregateSchema
