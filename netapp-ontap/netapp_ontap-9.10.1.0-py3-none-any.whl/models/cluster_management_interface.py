r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ClusterManagementInterface", "ClusterManagementInterfaceSchema"]
__pdoc__ = {
    "ClusterManagementInterfaceSchema.resource": False,
    "ClusterManagementInterface": False,
}


class ClusterManagementInterfaceSchema(ResourceSchema):
    """The fields of the ClusterManagementInterface object"""

    ip = fields.Nested("netapp_ontap.models.ip_interface_and_gateway.IpInterfaceAndGatewaySchema", unknown=EXCLUDE, data_key="ip")
    r""" The ip field of the cluster_management_interface. """

    @property
    def resource(self):
        return ClusterManagementInterface

    gettable_fields = [
        "ip",
    ]
    """ip,"""

    patchable_fields = [
        "ip",
    ]
    """ip,"""

    postable_fields = [
        "ip",
    ]
    """ip,"""


class ClusterManagementInterface(Resource):

    _schema = ClusterManagementInterfaceSchema
