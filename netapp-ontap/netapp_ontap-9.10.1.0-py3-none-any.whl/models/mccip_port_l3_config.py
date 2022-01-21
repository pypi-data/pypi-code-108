r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MccipPortL3Config", "MccipPortL3ConfigSchema"]
__pdoc__ = {
    "MccipPortL3ConfigSchema.resource": False,
    "MccipPortL3Config": False,
}


class MccipPortL3ConfigSchema(ResourceSchema):
    """The fields of the MccipPortL3Config object"""

    ipv4_interface = fields.Nested("netapp_ontap.models.ip_interface_and_gateway.IpInterfaceAndGatewaySchema", unknown=EXCLUDE, data_key="ipv4_interface")
    r""" The ipv4_interface field of the mccip_port_l3_config. """

    @property
    def resource(self):
        return MccipPortL3Config

    gettable_fields = [
        "ipv4_interface",
    ]
    """ipv4_interface,"""

    patchable_fields = [
        "ipv4_interface",
    ]
    """ipv4_interface,"""

    postable_fields = [
        "ipv4_interface",
    ]
    """ipv4_interface,"""


class MccipPortL3Config(Resource):

    _schema = MccipPortL3ConfigSchema
