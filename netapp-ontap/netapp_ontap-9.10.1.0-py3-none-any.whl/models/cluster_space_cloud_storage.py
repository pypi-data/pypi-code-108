r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ClusterSpaceCloudStorage", "ClusterSpaceCloudStorageSchema"]
__pdoc__ = {
    "ClusterSpaceCloudStorageSchema.resource": False,
    "ClusterSpaceCloudStorage": False,
}


class ClusterSpaceCloudStorageSchema(ResourceSchema):
    """The fields of the ClusterSpaceCloudStorage object"""

    used = Size(data_key="used")
    r""" Total space used in cloud. """

    @property
    def resource(self):
        return ClusterSpaceCloudStorage

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


class ClusterSpaceCloudStorage(Resource):

    _schema = ClusterSpaceCloudStorageSchema
