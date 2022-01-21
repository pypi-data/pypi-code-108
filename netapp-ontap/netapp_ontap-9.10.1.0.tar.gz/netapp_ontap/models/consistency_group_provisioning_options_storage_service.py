r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupProvisioningOptionsStorageService", "ConsistencyGroupProvisioningOptionsStorageServiceSchema"]
__pdoc__ = {
    "ConsistencyGroupProvisioningOptionsStorageServiceSchema.resource": False,
    "ConsistencyGroupProvisioningOptionsStorageService": False,
}


class ConsistencyGroupProvisioningOptionsStorageServiceSchema(ResourceSchema):
    """The fields of the ConsistencyGroupProvisioningOptionsStorageService object"""

    name = fields.Str(data_key="name")
    r""" Storage service name. If not specified, the default value is the most performant for the platform.


Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return ConsistencyGroupProvisioningOptionsStorageService

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


class ConsistencyGroupProvisioningOptionsStorageService(Resource):

    _schema = ConsistencyGroupProvisioningOptionsStorageServiceSchema
