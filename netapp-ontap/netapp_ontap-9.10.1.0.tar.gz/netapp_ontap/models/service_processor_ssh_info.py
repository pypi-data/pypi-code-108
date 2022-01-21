r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ServiceProcessorSshInfo", "ServiceProcessorSshInfoSchema"]
__pdoc__ = {
    "ServiceProcessorSshInfoSchema.resource": False,
    "ServiceProcessorSshInfo": False,
}


class ServiceProcessorSshInfoSchema(ResourceSchema):
    """The fields of the ServiceProcessorSshInfo object"""

    allowed_addresses = fields.List(fields.Str, data_key="allowed_addresses")
    r""" Allowed IP addresses """

    @property
    def resource(self):
        return ServiceProcessorSshInfo

    gettable_fields = [
        "allowed_addresses",
    ]
    """allowed_addresses,"""

    patchable_fields = [
        "allowed_addresses",
    ]
    """allowed_addresses,"""

    postable_fields = [
        "allowed_addresses",
    ]
    """allowed_addresses,"""


class ServiceProcessorSshInfo(Resource):

    _schema = ServiceProcessorSshInfoSchema
