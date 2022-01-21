r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NetworkRouteForSvm", "NetworkRouteForSvmSchema"]
__pdoc__ = {
    "NetworkRouteForSvmSchema.resource": False,
    "NetworkRouteForSvm": False,
}


class NetworkRouteForSvmSchema(ResourceSchema):
    """The fields of the NetworkRouteForSvm object"""

    destination = fields.Nested("netapp_ontap.models.ip_info.IpInfoSchema", unknown=EXCLUDE, data_key="destination")
    r""" The destination field of the network_route_for_svm. """

    gateway = fields.Str(data_key="gateway")
    r""" The IP address of the gateway router leading to the destination.

Example: 10.1.1.1 """

    @property
    def resource(self):
        return NetworkRouteForSvm

    gettable_fields = [
        "destination",
        "gateway",
    ]
    """destination,gateway,"""

    patchable_fields = [
        "destination",
        "gateway",
    ]
    """destination,gateway,"""

    postable_fields = [
        "destination",
        "gateway",
    ]
    """destination,gateway,"""


class NetworkRouteForSvm(Resource):

    _schema = NetworkRouteForSvmSchema
