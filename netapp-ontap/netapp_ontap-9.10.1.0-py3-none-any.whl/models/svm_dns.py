r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmDns", "SvmDnsSchema"]
__pdoc__ = {
    "SvmDnsSchema.resource": False,
    "SvmDns": False,
}


class SvmDnsSchema(ResourceSchema):
    """The fields of the SvmDns object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the svm_dns. """

    domains = fields.List(fields.Str, data_key="domains")
    r""" The domains field of the svm_dns. """

    servers = fields.List(fields.Str, data_key="servers")
    r""" The servers field of the svm_dns. """

    @property
    def resource(self):
        return SvmDns

    gettable_fields = [
        "links",
        "domains",
        "servers",
    ]
    """links,domains,servers,"""

    patchable_fields = [
        "domains",
        "servers",
    ]
    """domains,servers,"""

    postable_fields = [
        "domains",
        "servers",
    ]
    """domains,servers,"""


class SvmDns(Resource):

    _schema = SvmDnsSchema
