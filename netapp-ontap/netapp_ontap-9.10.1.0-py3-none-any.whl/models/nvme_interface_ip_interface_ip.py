r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeInterfaceIpInterfaceIp", "NvmeInterfaceIpInterfaceIpSchema"]
__pdoc__ = {
    "NvmeInterfaceIpInterfaceIpSchema.resource": False,
    "NvmeInterfaceIpInterfaceIp": False,
}


class NvmeInterfaceIpInterfaceIpSchema(ResourceSchema):
    """The fields of the NvmeInterfaceIpInterfaceIp object"""

    address = fields.Str(data_key="address")
    r""" The address field of the nvme_interface_ip_interface_ip. """

    @property
    def resource(self):
        return NvmeInterfaceIpInterfaceIp

    gettable_fields = [
        "address",
    ]
    """address,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeInterfaceIpInterfaceIp(Resource):

    _schema = NvmeInterfaceIpInterfaceIpSchema
