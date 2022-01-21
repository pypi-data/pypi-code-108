r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NvmeInterfaceIpInterfaceLocation", "NvmeInterfaceIpInterfaceLocationSchema"]
__pdoc__ = {
    "NvmeInterfaceIpInterfaceLocationSchema.resource": False,
    "NvmeInterfaceIpInterfaceLocation": False,
}


class NvmeInterfaceIpInterfaceLocationSchema(ResourceSchema):
    """The fields of the NvmeInterfaceIpInterfaceLocation object"""

    port = fields.Nested("netapp_ontap.resources.port.PortSchema", unknown=EXCLUDE, data_key="port")
    r""" The port field of the nvme_interface_ip_interface_location. """

    @property
    def resource(self):
        return NvmeInterfaceIpInterfaceLocation

    gettable_fields = [
        "port.links",
        "port.name",
        "port.node",
        "port.uuid",
    ]
    """port.links,port.name,port.node,port.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NvmeInterfaceIpInterfaceLocation(Resource):

    _schema = NvmeInterfaceIpInterfaceLocationSchema
