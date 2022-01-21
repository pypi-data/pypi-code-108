r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SecurityAssociationIpsec", "SecurityAssociationIpsecSchema"]
__pdoc__ = {
    "SecurityAssociationIpsecSchema.resource": False,
    "SecurityAssociationIpsec": False,
}


class SecurityAssociationIpsecSchema(ResourceSchema):
    """The fields of the SecurityAssociationIpsec object"""

    action = fields.Str(data_key="action")
    r""" Action for the IPsec security association.

Valid choices:

* bypass
* discard
* esp_transport """

    inbound = fields.Nested("netapp_ontap.models.security_association_ipsec_inbound.SecurityAssociationIpsecInboundSchema", unknown=EXCLUDE, data_key="inbound")
    r""" The inbound field of the security_association_ipsec. """

    outbound = fields.Nested("netapp_ontap.models.security_association_ipsec_outbound.SecurityAssociationIpsecOutboundSchema", unknown=EXCLUDE, data_key="outbound")
    r""" The outbound field of the security_association_ipsec. """

    state = fields.Str(data_key="state")
    r""" State of the IPsec security association. """

    @property
    def resource(self):
        return SecurityAssociationIpsec

    gettable_fields = [
        "action",
        "inbound",
        "outbound",
        "state",
    ]
    """action,inbound,outbound,state,"""

    patchable_fields = [
        "action",
        "inbound",
        "outbound",
        "state",
    ]
    """action,inbound,outbound,state,"""

    postable_fields = [
        "action",
        "inbound",
        "outbound",
        "state",
    ]
    """action,inbound,outbound,state,"""


class SecurityAssociationIpsec(Resource):

    _schema = SecurityAssociationIpsecSchema
