r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupVolumeProvisioningOptions", "ConsistencyGroupVolumeProvisioningOptionsSchema"]
__pdoc__ = {
    "ConsistencyGroupVolumeProvisioningOptionsSchema.resource": False,
    "ConsistencyGroupVolumeProvisioningOptions": False,
}


class ConsistencyGroupVolumeProvisioningOptionsSchema(ResourceSchema):
    """The fields of the ConsistencyGroupVolumeProvisioningOptions object"""

    action = fields.Str(data_key="action")
    r""" Operation to perform

Valid choices:

* create
* add """

    count = Size(data_key="count")
    r""" Number of elements to perform the operation on. """

    storage_service = fields.Nested("netapp_ontap.models.consistency_group_provisioning_options_storage_service.ConsistencyGroupProvisioningOptionsStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the consistency_group_volume_provisioning_options. """

    @property
    def resource(self):
        return ConsistencyGroupVolumeProvisioningOptions

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "action",
        "count",
        "storage_service",
    ]
    """action,count,storage_service,"""

    postable_fields = [
        "action",
        "count",
        "storage_service",
    ]
    """action,count,storage_service,"""


class ConsistencyGroupVolumeProvisioningOptions(Resource):

    _schema = ConsistencyGroupVolumeProvisioningOptionsSchema
