r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupProvisioningOptions", "ConsistencyGroupProvisioningOptionsSchema"]
__pdoc__ = {
    "ConsistencyGroupProvisioningOptionsSchema.resource": False,
    "ConsistencyGroupProvisioningOptions": False,
}


class ConsistencyGroupProvisioningOptionsSchema(ResourceSchema):
    """The fields of the ConsistencyGroupProvisioningOptions object"""

    action = fields.Str(data_key="action")
    r""" Operation to perform

Valid choices:

* create """

    storage_service = fields.Nested("netapp_ontap.models.consistency_group_provisioning_options_storage_service.ConsistencyGroupProvisioningOptionsStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the consistency_group_provisioning_options. """

    @property
    def resource(self):
        return ConsistencyGroupProvisioningOptions

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "action",
        "storage_service",
    ]
    """action,storage_service,"""

    postable_fields = [
        "action",
        "storage_service",
    ]
    """action,storage_service,"""


class ConsistencyGroupProvisioningOptions(Resource):

    _schema = ConsistencyGroupProvisioningOptionsSchema
