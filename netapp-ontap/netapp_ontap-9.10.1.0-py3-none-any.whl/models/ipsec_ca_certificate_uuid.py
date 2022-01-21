r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IpsecCaCertificateUuid", "IpsecCaCertificateUuidSchema"]
__pdoc__ = {
    "IpsecCaCertificateUuidSchema.resource": False,
    "IpsecCaCertificateUuid": False,
}


class IpsecCaCertificateUuidSchema(ResourceSchema):
    """The fields of the IpsecCaCertificateUuid object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the ipsec_ca_certificate_uuid. """

    uuid = fields.Str(data_key="uuid")
    r""" Certificate UUID

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return IpsecCaCertificateUuid

    gettable_fields = [
        "links",
        "uuid",
    ]
    """links,uuid,"""

    patchable_fields = [
        "uuid",
    ]
    """uuid,"""

    postable_fields = [
        "uuid",
    ]
    """uuid,"""


class IpsecCaCertificateUuid(Resource):

    _schema = IpsecCaCertificateUuidSchema
