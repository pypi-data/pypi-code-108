r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmNis", "SvmNisSchema"]
__pdoc__ = {
    "SvmNisSchema.resource": False,
    "SvmNis": False,
}


class SvmNisSchema(ResourceSchema):
    """The fields of the SvmNis object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the svm_nis. """

    domain = fields.Str(data_key="domain")
    r""" The domain field of the svm_nis. """

    enabled = fields.Boolean(data_key="enabled")
    r""" Enable NIS? Setting to true creates a configuration if not already created. """

    servers = fields.List(fields.Str, data_key="servers")
    r""" The servers field of the svm_nis. """

    @property
    def resource(self):
        return SvmNis

    gettable_fields = [
        "links",
        "domain",
        "enabled",
        "servers",
    ]
    """links,domain,enabled,servers,"""

    patchable_fields = [
        "domain",
        "enabled",
        "servers",
    ]
    """domain,enabled,servers,"""

    postable_fields = [
        "domain",
        "enabled",
        "servers",
    ]
    """domain,enabled,servers,"""


class SvmNis(Resource):

    _schema = SvmNisSchema
