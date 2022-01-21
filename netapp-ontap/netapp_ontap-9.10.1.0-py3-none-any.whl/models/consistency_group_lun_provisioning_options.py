r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupLunProvisioningOptions", "ConsistencyGroupLunProvisioningOptionsSchema"]
__pdoc__ = {
    "ConsistencyGroupLunProvisioningOptionsSchema.resource": False,
    "ConsistencyGroupLunProvisioningOptions": False,
}


class ConsistencyGroupLunProvisioningOptionsSchema(ResourceSchema):
    """The fields of the ConsistencyGroupLunProvisioningOptions object"""

    action = fields.Str(data_key="action")
    r""" Operation to perform

Valid choices:

* create """

    count = Size(data_key="count")
    r""" Number of elements to perform the operation on. """

    @property
    def resource(self):
        return ConsistencyGroupLunProvisioningOptions

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "action",
        "count",
    ]
    """action,count,"""

    postable_fields = [
        "action",
        "count",
    ]
    """action,count,"""


class ConsistencyGroupLunProvisioningOptions(Resource):

    _schema = ConsistencyGroupLunProvisioningOptionsSchema
