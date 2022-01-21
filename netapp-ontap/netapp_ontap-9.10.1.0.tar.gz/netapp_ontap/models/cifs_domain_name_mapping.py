r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CifsDomainNameMapping", "CifsDomainNameMappingSchema"]
__pdoc__ = {
    "CifsDomainNameMappingSchema.resource": False,
    "CifsDomainNameMapping": False,
}


class CifsDomainNameMappingSchema(ResourceSchema):
    """The fields of the CifsDomainNameMapping object"""

    trusted_domains = fields.List(fields.Str, data_key="trusted_domains")
    r""" The trusted_domains field of the cifs_domain_name_mapping. """

    @property
    def resource(self):
        return CifsDomainNameMapping

    gettable_fields = [
        "trusted_domains",
    ]
    """trusted_domains,"""

    patchable_fields = [
        "trusted_domains",
    ]
    """trusted_domains,"""

    postable_fields = [
        "trusted_domains",
    ]
    """trusted_domains,"""


class CifsDomainNameMapping(Resource):

    _schema = CifsDomainNameMappingSchema
