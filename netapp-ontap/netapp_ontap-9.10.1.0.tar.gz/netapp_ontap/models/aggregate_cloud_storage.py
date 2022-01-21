r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateCloudStorage", "AggregateCloudStorageSchema"]
__pdoc__ = {
    "AggregateCloudStorageSchema.resource": False,
    "AggregateCloudStorage": False,
}


class AggregateCloudStorageSchema(ResourceSchema):
    """The fields of the AggregateCloudStorage object"""

    attach_eligible = fields.Boolean(data_key="attach_eligible")
    r""" Specifies whether the aggregate is eligible for a cloud store to be attached. """

    stores = fields.List(fields.Nested("netapp_ontap.models.cloud_storage_tier.CloudStorageTierSchema", unknown=EXCLUDE), data_key="stores")
    r""" Configuration information for each cloud storage portion of the aggregate. """

    tiering_fullness_threshold = Size(data_key="tiering_fullness_threshold")
    r""" The percentage of space in the performance tier that must be used before data is tiered out to the cloud store. Only valid for PATCH operations. """

    @property
    def resource(self):
        return AggregateCloudStorage

    gettable_fields = [
        "attach_eligible",
        "stores",
    ]
    """attach_eligible,stores,"""

    patchable_fields = [
        "tiering_fullness_threshold",
    ]
    """tiering_fullness_threshold,"""

    postable_fields = [
    ]
    """"""


class AggregateCloudStorage(Resource):

    _schema = AggregateCloudStorageSchema
