r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateSpaceCloudStorage", "AggregateSpaceCloudStorageSchema"]
__pdoc__ = {
    "AggregateSpaceCloudStorageSchema.resource": False,
    "AggregateSpaceCloudStorage": False,
}


class AggregateSpaceCloudStorageSchema(ResourceSchema):
    """The fields of the AggregateSpaceCloudStorage object"""

    used = Size(data_key="used")
    r""" Used space in bytes in the cloud store. Only applicable for aggregates with a cloud store tier.

Example: 402743264 """

    @property
    def resource(self):
        return AggregateSpaceCloudStorage

    gettable_fields = [
        "used",
    ]
    """used,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AggregateSpaceCloudStorage(Resource):

    _schema = AggregateSpaceCloudStorageSchema
