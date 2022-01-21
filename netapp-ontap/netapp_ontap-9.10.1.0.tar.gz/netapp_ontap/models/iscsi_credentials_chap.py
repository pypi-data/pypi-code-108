r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IscsiCredentialsChap", "IscsiCredentialsChapSchema"]
__pdoc__ = {
    "IscsiCredentialsChapSchema.resource": False,
    "IscsiCredentialsChap": False,
}


class IscsiCredentialsChapSchema(ResourceSchema):
    """The fields of the IscsiCredentialsChap object"""

    inbound = fields.Nested("netapp_ontap.models.iscsi_credentials_chap_inbound.IscsiCredentialsChapInboundSchema", unknown=EXCLUDE, data_key="inbound")
    r""" The inbound field of the iscsi_credentials_chap. """

    outbound = fields.Nested("netapp_ontap.models.iscsi_credentials_chap_outbound.IscsiCredentialsChapOutboundSchema", unknown=EXCLUDE, data_key="outbound")
    r""" The outbound field of the iscsi_credentials_chap. """

    @property
    def resource(self):
        return IscsiCredentialsChap

    gettable_fields = [
        "inbound",
        "outbound",
    ]
    """inbound,outbound,"""

    patchable_fields = [
        "inbound",
        "outbound",
    ]
    """inbound,outbound,"""

    postable_fields = [
        "inbound",
        "outbound",
    ]
    """inbound,outbound,"""


class IscsiCredentialsChap(Resource):

    _schema = IscsiCredentialsChapSchema
