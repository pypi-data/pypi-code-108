r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Usm", "UsmSchema"]
__pdoc__ = {
    "UsmSchema.resource": False,
    "Usm": False,
}


class UsmSchema(ResourceSchema):
    """The fields of the Usm object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the usm. """

    authentication_password = fields.Str(data_key="authentication_password")
    r""" Authentication protocol password.

Example: humTdumt*@t0nAwa11 """

    authentication_protocol = fields.Str(data_key="authentication_protocol")
    r""" Authentication protocol.

Valid choices:

* none
* md5
* sha
* sha2_256 """

    privacy_password = fields.Str(data_key="privacy_password")
    r""" Privacy protocol password.

Example: p@**GOandCLCt*200 """

    privacy_protocol = fields.Str(data_key="privacy_protocol")
    r""" Privacy protocol.

Valid choices:

* none
* des
* aes128 """

    @property
    def resource(self):
        return Usm

    gettable_fields = [
        "links",
        "authentication_protocol",
        "privacy_protocol",
    ]
    """links,authentication_protocol,privacy_protocol,"""

    patchable_fields = [
        "authentication_protocol",
        "privacy_protocol",
    ]
    """authentication_protocol,privacy_protocol,"""

    postable_fields = [
        "authentication_password",
        "authentication_protocol",
        "privacy_password",
        "privacy_protocol",
    ]
    """authentication_password,authentication_protocol,privacy_password,privacy_protocol,"""


class Usm(Resource):

    _schema = UsmSchema
