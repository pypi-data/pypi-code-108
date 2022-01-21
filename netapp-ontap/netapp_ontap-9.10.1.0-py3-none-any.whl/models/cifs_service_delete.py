r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CifsServiceDelete", "CifsServiceDeleteSchema"]
__pdoc__ = {
    "CifsServiceDeleteSchema.resource": False,
    "CifsServiceDelete": False,
}


class CifsServiceDeleteSchema(ResourceSchema):
    """The fields of the CifsServiceDelete object"""

    ad_domain = fields.Nested("netapp_ontap.models.ad_domain.AdDomainSchema", unknown=EXCLUDE, data_key="ad_domain")
    r""" The ad_domain field of the cifs_service_delete. """

    @property
    def resource(self):
        return CifsServiceDelete

    gettable_fields = [
        "ad_domain",
    ]
    """ad_domain,"""

    patchable_fields = [
        "ad_domain",
    ]
    """ad_domain,"""

    postable_fields = [
        "ad_domain",
    ]
    """ad_domain,"""


class CifsServiceDelete(Resource):

    _schema = CifsServiceDeleteSchema
