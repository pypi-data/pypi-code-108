r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmCifsService", "SvmCifsServiceSchema"]
__pdoc__ = {
    "SvmCifsServiceSchema.resource": False,
    "SvmCifsService": False,
}


class SvmCifsServiceSchema(ResourceSchema):
    """The fields of the SvmCifsService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the svm_cifs_service. """

    ad_domain = fields.Nested("netapp_ontap.models.ad_domain_svm.AdDomainSvmSchema", unknown=EXCLUDE, data_key="ad_domain")
    r""" The ad_domain field of the svm_cifs_service. """

    allowed = fields.Boolean(data_key="allowed")
    r""" If this is set to true, an SVM administrator can manage the CIFS service. If it is false, only the cluster administrator can manage the service. """

    enabled = fields.Boolean(data_key="enabled")
    r""" If allowed, setting to true enables the CIFS service. """

    name = fields.Str(data_key="name")
    r""" The NetBIOS name of the CIFS server.

Example: CIFS1 """

    @property
    def resource(self):
        return SvmCifsService

    gettable_fields = [
        "links",
        "ad_domain",
        "allowed",
        "enabled",
        "name",
    ]
    """links,ad_domain,allowed,enabled,name,"""

    patchable_fields = [
        "allowed",
    ]
    """allowed,"""

    postable_fields = [
        "ad_domain",
        "allowed",
        "enabled",
        "name",
    ]
    """ad_domain,allowed,enabled,name,"""


class SvmCifsService(Resource):

    _schema = SvmCifsServiceSchema
